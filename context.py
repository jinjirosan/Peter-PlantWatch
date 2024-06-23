
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
# context.py : v2-1.0 (stable) - refactor C1.0.0
# 
class Context:
    def __init__(self):
        self.light_level = None
        self.soil_moisture = {}
        self.temperature = None
        self.humidity = None
        # Add other relevant fields as needed
