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
# main.py : v2-2.5 (stable) - refactor C1.0.0

import logging
import math
import pathlib
import random
import sys
import threading
import time
from PIL import Image, ImageDraw

import ltr559
import RPi.GPIO as GPIO
import ST7735
from fonts.ttf import RobotoMedium as UserFont
import yaml
from grow import Piezo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
from grow.moisture import Moisture
from grow.pump import Pump
from models import Channel, Alarm
from views import MainView, SettingsView, DetailView, ChannelEditView
from controllers import ViewController
from config import Config
from constants import DISPLAY_WIDTH, DISPLAY_HEIGHT, BUTTONS, LABELS, FPS, COLOR_WHITE
from plant_logging import log_values

def handle_button(pin):
    index = BUTTONS.index(pin)
    label = LABELS[index]

    if label == "A":
        viewcontroller.button_a()
    elif label == "B":
        if not viewcontroller.button_b():
            if viewcontroller.home:
                if alarm.sleeping():
                    alarm.cancel_sleep()
                else:
                    alarm.sleep()
    elif label == "X":
        viewcontroller.button_x()
    elif label == "Y":
        viewcontroller.button_y()

def main():
    global viewcontroller, alarm

    # Basic logging configuration
    logging.basicConfig(level=logging.DEBUG)

    # Set up the ST7735 SPI Display
    display = ST7735.ST7735(
        port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=80000000
    )
    display.begin()

    # Set up light sensor
    light = ltr559.LTR559()

    # Set up our canvas and prepare for drawing
    image = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=(255, 255, 255))  # Use RGB mode for display compatibility
    draw = ImageDraw.Draw(image)  # Create a drawing context for the canvas

    # Setup blank image for darkness
    image_blank = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=(0, 0, 0))

    # Pick a random selection of plant icons to display on screen
    channels = [
        Channel(1, 1, 1),
        Channel(2, 2, 2),
        Channel(3, 3, 3),
    ]

    alarm = Alarm(image)

    config = Config()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for pin in BUTTONS:
        GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=200)

    config.load()

    for channel in channels:
        channel.update_from_yml(config.get_channel(channel.channel))

    alarm.update_from_yml(config.get_general())

    print("Channels:")
    for channel in channels:
        print(channel)

    print(
        """Settings:
Alarm Enabled: {}
Alarm Interval: {:.2f}s
Low Light Set Screen To Black: {}
Low Light Value {:.2f}
""".format(
            alarm.enabled,
            alarm.interval,
            config.get_general().get("black_screen_when_light_low"),
            config.get_general().get("light_level_low")
        )
    )

    main_options = [
        {
            "title": "Alarm Interval",
            "prop": "interval",
            "inc": 1,
            "min": 1,
            "max": 60,
            "format": lambda value: f"{value:02.0f}sec",
            "object": alarm,
            "help": "Time between alarm beeps.",
        },
        {
            "title": "Alarm Enable",
            "prop": "enabled",
            "mode": "bool",
            "format": lambda value: "Yes" if value else "No",
            "object": alarm,
            "help": "Enable the piezo alarm beep.",
        },
    ]

    viewcontroller = ViewController(
        [
            (
                MainView(image, channels=channels, alarm=alarm),
                SettingsView(image, options=main_options),
            ),
            (
                DetailView(image, channel=channels[0]),
                ChannelEditView(image, channel=channels[0]),
            ),
            (
                DetailView(image, channel=channels[1]),
                ChannelEditView(image, channel=channels[1]),
            ),
            (
                DetailView(image, channel=channels[2]),
                ChannelEditView(image, channel=channels[2]),
            ),
        ]
    )

    # Log values initially
    for channel in channels:
        log_values(
            channel.channel,
            channel.sensor.moisture,
            channel.sensor.saturation * 100,
            channel.water(),
            light.get_lux()
        )

    last_log_time = time.time()  # Track the last log time

    while True:
        for channel in channels:
            config.set_channel(channel.channel, channel)
            channel.update()
            if channel.alarm:
                alarm.trigger()

        light_level_low = light.get_lux() < config.get_general().get("light_level_low")

        alarm.update(light_level_low)

        viewcontroller.update()

        if light_level_low and config.get_general().get("black_screen_when_light_low"):
            display.sleep()
            display.display(image_blank.convert("RGB"))
        else:
            viewcontroller.render()
            display.wake()
            display.display(image)

        config.set_general(
            {
                "alarm_enable": alarm.enabled,
                "alarm_interval": alarm.interval,
            }
        )

        current_time = time.time()
        if current_time - last_log_time >= 600:  # Log every 600 seconds (10 minutes)
            logging.debug("Logging values for all channels")
            for channel in channels:
                log_values(
                    channel.channel,
                    channel.sensor.moisture,
                    channel.sensor.saturation * 100,
                    channel.water(),
                    light.get_lux()
                )
            last_log_time = current_time

        config.save()

        time.sleep(1.0 / FPS)

if __name__ == "__main__":
    main()
