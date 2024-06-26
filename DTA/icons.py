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
# icons.py : v2-2.5 (stable) - refactor C1.0.0

from PIL import Image

ICONS_DIR = "/usr/share/peterplantwatch/icons"

def load_icon(name):
    return Image.open(f"{ICONS_DIR}/{name}.png").convert("RGBA")

icon_drop = load_icon("icon-drop")
icon_nodrop = load_icon("icon-nodrop")
icon_rightarrow = load_icon("icon-rightarrow")
icon_alarm = load_icon("icon-alarm")
icon_snooze = load_icon("icon-snooze")
icon_help = load_icon("icon-help")
icon_settings = load_icon("icon-settings")
icon_channel = load_icon("icon-channel")
icon_backdrop = load_icon("icon-backdrop")
icon_return = load_icon("icon-return")
