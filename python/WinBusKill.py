import os
import sys
import usb.core
import usb.util
import time
import json
import logging
import tkinter 
from tkinter import messagebox
from tkinter import Tk
import ctypes

#hide tk root window
root = Tk()
root.withdraw()


def main():

    appdata = os.getenv('APPDATA')

    #get %appdata from os for user
    filename="WinBusKill.log"
    delim = "\\"
    log_location= appdata + delim + filename
        
    #Define logging
    logging.basicConfig(
    filename=log_location,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Get configuration parameters
    parameters = {}

    configuration = "config.json"

    if configuration:
        with open(configuration, 'r') as f:
            parameters = f.read()
        parameters = json.loads(parameters)
    else:
        messagebox.showwarning("Configuration File Error", "Oops something is wrong !!\n Causes Include: \n - Incorrect configuration file information \n - Configuration file not present\n - Incorrect filename must be config.json")
        sys.exit()  
        
    VendorId = parameters['IdVendor']
    ProductId = parameters['ProductId']
    UsbNumberBase = int(parameters['UsbNumberBase'])
    ConnectTime = parameters['ConnectInterval']
    DisconnectTime = parameters['DisconnectInterval']
    TriggerAction = parameters['TriggerAction']
    
    # check TriggerAction variable set correctly
    if TriggerAction not in ["lock", "shutdown"]:
        messagebox.showwarning("Trigger Action Error", "Trigger action must be set to lock or shutdown in config.json file")
        sys.exit()

      # check USsbNumberBase variable set correctly
    if UsbNumberBase not in [16, 10]:
        messagebox.showwarning("USB Number Base Error", "USBNumberBase must be either 16 or 10 in the config.json file")
        sys.exit()
        
    #convert string to correct int base 10 or 16 depending omm config for pyusb
    VendorId=int(VendorId ,UsbNumberBase)
    ProductId=int(ProductId ,UsbNumberBase) 
    ConnectTime=int(ConnectTime)
    DisconnectTime=int(DisconnectTime)
        
    # find USB devices or raise exception dialog

    try:
        dev = usb.core.find(idVendor=VendorId, idProduct=ProductId)
        logging.info("WinBusKill started")

        # if not connected continuosly recheck every via time interval
        while dev is None:
            time.sleep(ConnectTime)
            dev = usb.core.find(idVendor=VendorId, idProduct=ProductId)
    except:
         messagebox.showwarning("Pyusb Exception", "Pyusb USB Exception Error occurred.")
         logging.info("WinBusKill Pyusb Connection Error")
         sys.exit()
            
    #pop tkinter messagebox to ask if you want to enable protection
    enable_protection = messagebox.askyesno("BusKill Protector","Do you want to enable BusKill USB protection?")
    if enable_protection is True:
       logging.info("WinBusKill USB Inserted - Enabling Protection") 
    else:
       logging.warning("WinBusKill USB Inserted - Protection Disabled")
       sys.exit()
        
    #check for usb device disconnect every time interval
    dev = usb.core.find(idVendor=VendorId, idProduct=ProductId)

    while dev != None:
        time.sleep(DisconnectTime)
        try:
            dev = usb.core.find(idVendor=VendorId, idProduct=ProductId)
        except:
            messagebox.showwarning("Pyusb Exception", "Pyusb USB Exception Error occurred.")
            logging.info("WinBusKill Pyusb Connection Error")
            sys.exit()
        
    logging.critical("WinBusKill USB Protection Removed - Locking Workstation")   
    time.sleep(DisconnectTime)

    # lock or shutdown workstation
    
    if TriggerAction == "lock":
        ctypes.windll.user32.LockWorkStation()

if __name__ == '__main__':
    while True:
        main()
