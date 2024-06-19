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
# hardware.py : v2-2.5 (stable) - refactor C1.0.0

import RPi.GPIO as GPIO
import ST7735

BUTTONS = [5, 6, 16, 24]
LABELS = ["A", "B", "X", "Y"]

def setup_gpio(button_pins, handle_button):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(button_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in button_pins:
        GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=200)

def initialize_display():
    display = ST7735.ST7735(
        port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=80000000
    )
    display.begin()
    return display
