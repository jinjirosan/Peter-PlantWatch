#!/usr/bin/env python3
#    ___     _                                         
#   / _ \___| |_ ___ _ __                              
#  / /_)/ _ \ __/ _ \ '__|                             
# / ___/  __/ ||  __/ |                                
# \/    \___|\__\___|_|                                                                                 
#    ___ _             _   __    __      _       _     
#   / _ \ | __ _ _ __ | |_/ / /\ \ \__ _| |_ ___| |__  
#  / /_)/ |/ _` | '_ \| __\ \/  \/ / _` | __/ __| '_ \ 
# / ___/| | (_| | | | | |_ \  /\  / (_| | || (__| | | |
# \/    |_|\__,_|_| |_|\__| \/  \/ \__,_|\__\___|_| |_|
#                       .: auto-grow the greens yo :.                          
#
# Automated plant monitoring and watering system
#
# hardware platform  : Raspberry Pi Zero W
# HAT                : Pimoroni Grow Hat Mini
# Water drivers      : COM3700 Mini submersible water pump
# Sensors            : Capacitive Soil moisture sensor with PFM output
#                    : BME280 Temperature, Humidity, Air pressure
#                    : LTR-559 light and proximity sensor 
# Codebase           : Python3
#
# (2024) JinjiroSan
#
# PeterPlantwatch/
# ├── main.py
# ├── config.py
# ├── views.py
# ├── controllers.py
# ├── models.py
# ├── icons.py
# ├── constants.py
# ├── hardware.py
# └── plant_logging.py
#
# plant_logging.py : v2-2.5.1.f3 (stable) - refactor C1.0.0
# changelog : include a mechanism to track the last watering event and ensure it only logs "Yes" for the actual watering event
#           : f1 fixing runtime errors
#           : f2 added simulation logging for auto_water simulation
#           : f3 fixed sim log

import logging
import os
import time

# Ensure the /var/log directory exists
log_dir = "/var/log/plantwatch"
os.makedirs(log_dir, exist_ok=True)

# Function to set up logging for a specific channel
def setup_channel_logger(channel_id):
    logger = logging.getLogger(f"Channel{channel_id}")
    logger.setLevel(logging.INFO)
    log_path = os.path.join(log_dir, f"plantwatch_channel_{channel_id}.log")
    
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

# Setting up loggers for each channel
channel_loggers = {i: setup_channel_logger(i) for i in range(1, 4)}
last_watered_times = {i: None for i in range(1, 4)}

def log_values(channel_id, soil_moisture_abs, soil_moisture_percent, water_given, light_level, simulate=False):
    logger = channel_loggers[channel_id]
    water_status = "Yes" if water_given else "No"
    log_type = "Simulated" if simulate else ""

    # Check if the water was given and it is a new event
    if water_given and not simulate:
        last_watered_times[channel_id] = time.time()
    elif last_watered_times[channel_id] and time.time() - last_watered_times[channel_id] < 600:  # 600 seconds = 10 minutes
        water_status = "No"
        
    message = (f"{log_type} soil moisture (abs): {soil_moisture_abs}, "
               f"soil moisture (%): {soil_moisture_percent:.2f}, "
               f"water given: {water_status}, "
               f"light level: {light_level}")
    logger.info(message)
