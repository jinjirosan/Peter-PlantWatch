#!/usr/bin/env python3

import logging
import os

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

def log_values(channel_id, soil_moisture_abs, soil_moisture_percent, water_given, light_level, wet_point, dry_point, auto_water):
    logger = channel_loggers[channel_id]
    water_status = "Yes" if water_given else "No"
    auto_water_status = "Enabled" if auto_water else "Disabled"
    message = (f"soil moisture (abs): {soil_moisture_abs}, "
               f"soil moisture (%): {soil_moisture_percent:.2f}, "
               f"water given: {water_status}, "
               f"light level: {light_level}, "
               f"wet point: {wet_point}, "
               f"dry point: {dry_point}, "
               f"auto water: {auto_water_status}")
    logger.info(message)
