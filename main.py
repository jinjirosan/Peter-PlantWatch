#!/usr/bin/env python3
# reverted

import time
import threading
import sys
from PIL import Image
import ltr559

from config import Config
from views import MainView, SettingsView, ChannelView, DetailView, ChannelEditView
from controllers import ViewController
from models import Channel, Alarm
from hardware import setup_gpio, initialize_display, BUTTONS, LABELS
from plant_logging import log_values
from constants import DISPLAY_WIDTH, DISPLAY_HEIGHT

FPS = 10

viewcontroller = None  # Declare globally

def handle_button(pin):
    global viewcontroller
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
    global viewcontroller  # Use global viewcontroller
    display = initialize_display()
    light = ltr559.LTR559()
    image = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=(255, 255, 255))
    image_blank = Image.new("RGBA", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=(0, 0, 0))

    channels = [Channel(1, 1, 1), Channel(2, 2, 2), Channel(3, 3, 3)]
    alarm = Alarm(image)
    config = Config()
    setup_gpio(BUTTONS, handle_button)

    config.load()
    for channel in channels: channel.update_from_yml(config.get_channel(channel.channel))
    alarm.update_from_yml(config.get_general())

    main_options = [
        {"title": "Alarm Interval", "prop": "interval", "inc": 1, "min": 1, "max": 60, "format": lambda value: f"{value:02.0f}sec", "object": alarm, "help": "Time between alarm beeps."},
        {"title": "Alarm Enable", "prop": "enabled", "mode": "bool", "format": lambda value: "Yes" if value else "No", "object": alarm, "help": "Enable the piezo alarm beep."},
    ]

    viewcontroller = ViewController([
        (MainView(image, channels=channels, alarm=alarm), SettingsView(image, options=main_options)),
        (DetailView(image, channel=channels[0]), ChannelEditView(image, channel=channels[0])),
        (DetailView(image, channel=channels[1]), ChannelEditView(image, channel=channels[1])),
        (DetailView(image, channel=channels[2]), ChannelEditView(image, channel=channels[2])),
    ])

    while True:
        for channel in channels:
            config.set_channel(channel.channel, channel)
            channel.update()
            if channel.alarm:
                alarm.trigger()

            # Log measured values for each channel
            soil_moisture_abs = channel.sensor.moisture
            soil_moisture_percent = channel.sensor.saturation * 100
            water_given = channel.water()
            light_level = light.get_lux()
            log_values(channel.channel, soil_moisture_abs, soil_moisture_percent, water_given, light_level)

        light_level_low = light.get_lux() < config.get_general().get("light_level_low")
        alarm.update(light_level_low)
        viewcontroller.update()

        if light_level_low and config.get_general().get("black_screen_when_light_low"):
            display.sleep()
            display.display(image_blank.convert("RGB"))
        else:
            viewcontroller.render()
            display.wake()
            display.display(image.convert("RGB"))

        config.set_general({"alarm_enable": alarm.enabled, "alarm_interval": alarm.interval})
        config.save()
        time.sleep(1.0 / FPS)

if __name__ == "__main__":
    main()