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
# models.py : v2-2.7.2.f3 (stable) - refactor C1.0.0
# changelog : f1 - condition for ignoring invalid readings checks if the saturation is higher than the defined water_level instead of assuming it is always 100%
#           : f2 - ensure the update method in Channel properly reflects when watering occurs
#           : f3 - correctly import log_values

import time
import math
import threading
import logging
from collections import deque
from grow.moisture import Moisture
from grow.pump import Pump
from grow import Piezo  # Import Piezo
from PIL import Image
from views import View  # Import View class
from icons import icon_alarm, icon_snooze  # Import icons
from plant_logging import log_values  # Add this line to import log_values

class Channel:
    colors = [
        (31, 137, 251),
        (99, 255, 124),
        (254, 219, 82),
        (247, 0, 63)
    ]

    def __init__(
        self,
        display_channel,
        sensor_channel,
        pump_channel,
        title=None,
        water_level=0.5,
        warn_level=0.5,
        pump_speed=0.5,
        pump_time=0.2,
        watering_delay=60,
        wet_point=0.7,
        dry_point=26.7,
        icon=None,
        auto_water=False,
        enabled=False,
    ):
        self.channel = display_channel
        self.sensor = Moisture(sensor_channel)
        self.pump = Pump(pump_channel)
        self.water_level = water_level
        self.warn_level = warn_level
        self.auto_water = auto_water
        self.pump_speed = pump_speed
        self.pump_time = pump_time
        self.watering_delay = watering_delay
        self._wet_point = wet_point
        self._dry_point = dry_point
        self.last_dose = time.time()
        self.icon = icon
        self._enabled = enabled
        self.alarm = False
        self.title = f"Channel {display_channel}" if title is None else title

        self.sensor.set_wet_point(wet_point)
        self.sensor.set_dry_point(dry_point)

        # Debounce mechanism
        self.moisture_readings = deque(maxlen=5)  # Store the last 5 readings
        self.reading_interval = 60  # Interval between readings in seconds
        self.large_change_threshold = 10.0  # Threshold for ignoring large changes in percentage

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def wet_point(self):
        return self._wet_point

    @property
    def dry_point(self):
        return self._dry_point

    @wet_point.setter
    def wet_point(self, wet_point):
        self._wet_point = wet_point
        self.sensor.set_wet_point(wet_point)

    @dry_point.setter
    def dry_point(self, dry_point):
        self._dry_point = dry_point
        self.sensor.set_dry_point(dry_point)

    def add_moisture_reading(self, reading):
        if reading == 0 and self.sensor.saturation > self.water_level:
            logging.warning(f"Ignoring invalid reading: {reading}")
            return
        self.moisture_readings.append(reading)
        logging.debug(f"Added moisture reading: {reading}, current window: {list(self.moisture_readings)}")

    def get_moving_average(self):
        if len(self.moisture_readings) < 2:
            return self.moisture_readings[0]
        return sum(self.moisture_readings) / len(self.moisture_readings)

    def should_water(self):
        if len(self.moisture_readings) < self.moisture_readings.maxlen:
            return False  # Not enough data yet

        # Calculate the moving average of the readings
        moving_average = self.get_moving_average()
        logging.debug(f"Moving average: {moving_average}")

        # Check for large changes and ignore them
        for reading in self.moisture_readings:
            if abs(reading - moving_average) > self.large_change_threshold:
                logging.debug(f"Ignoring large change in reading: {reading}")
                return False

        # Check if there is a steady decline
        steady_decline = all(x > y for x, y in zip(self.moisture_readings, list(self.moisture_readings)[1:]))
        logging.debug(f"Steady decline detected: {steady_decline}")
        return steady_decline

    def warn_color(self):
        value = self.sensor.moisture

    def indicator_color(self, value):
        value = 1.0 - value

        if value == 1.0:
            return self.colors[-1]
        if value == 0.0:
            return self.colors[0]

        value *= len(self.colors) - 1
        a = int(math.floor(value))
        b = a + 1
        blend = float(value - a)

        r, g, b = [int(((self.colors[b][i] - self.colors[a][i]) * blend) + self.colors[a][i]) for i in range(3)]

        return (r, g, b)

    def update_from_yml(self, config):
        if config is not None:
            self.pump_speed = config.get("pump_speed", self.pump_speed)
            self.pump_time = config.get("pump_time", self.pump_time)
            self.warn_level = config.get("warn_level", self.warn_level)
            self.water_level = config.get("water_level", self.water_level)
            self.watering_delay = config.get("watering_delay", self.watering_delay)
            self.auto_water = config.get("auto_water", self.auto_water)
            self.enabled = config.get("enabled", self.enabled)
            self.wet_point = config.get("wet_point", self.wet_point)
            self.dry_point = config.get("dry_point", self.dry_point)

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "warn_level": self.warn_level,
            "wet_point": self.wet_point,
            "dry_point": self.dry_point,
            "watering_delay": self.watering_delay,
            "auto_water": self.auto_water,
            "pump_time": self.pump_time,
            "pump_speed": self.pump_speed,
            "water_level": self.water_level,
        }

    def __str__(self):
        return """Channel: {channel}
Enabled: {enabled}
Alarm level: {warn_level}
Auto water: {auto_water}
Water level: {water_level}
Pump speed: {pump_speed}
Pump time: {pump_time}
Delay: {watering_delay}
Wet point: {wet_point}
Dry point: {dry_point}
""".format(
            channel=self.channel,
            enabled=self.enabled,
            warn_level=self.warn_level,
            auto_water=self.auto_water,
            water_level=self.water_level,
            pump_speed=self.pump_speed,
            pump_time=self.pump_time,
            watering_delay=self.watering_delay,
            wet_point=self.wet_point,
            dry_point=self.dry_point,
        )

    def water(self):
        if not self.auto_water:
            return False
        if time.time() - self.last_dose > self.watering_delay:
            self.pump.dose(self.pump_speed, self.pump_time, blocking=False)
            self.last_dose = time.time()
            return True
        return False

    def render(self, image, font):
        pass

    def update(self):
        if not self.enabled:
            return
        sat = self.sensor.saturation
        if sat > self.water_level and self.sensor.moisture == 0:
            logging.warning(f"Ignoring invalid sensor reading: moisture={self.sensor.moisture}, saturation={sat}")
            return

        self.add_moisture_reading(sat)
        
        watered = False
        if self.should_water() and sat < self.water_level:
            watered = self.water()
            if watered:
                logging.info(
                    "Watering Channel: {} - rate {:.2f} for {:.2f}sec".format(
                        self.channel, self.pump_speed, self.pump_time
                    )
                )
        
        if sat < self.warn_level:
            if not self.alarm:
                logging.warning(
                    "Alarm on Channel: {} - saturation is {:.2f}% (warn level {:.2f}%)".format(
                        self.channel, sat * 100, self.warn_level * 100
                    )
                )
            self.alarm = True
        else:
            self.alarm = False

        # Log the current state, including whether watering was performed
        log_values(
            self.channel,
            self.sensor.moisture,
            sat * 100,
            watered,
            light.get_lux()
        )



class Alarm(View):
    def __init__(self, image, enabled=True, interval=10.0, beep_frequency=440):
        self.piezo = Piezo()
        self.enabled = enabled
        self.interval = interval
        self.beep_frequency = beep_frequency
        self._triggered = False
        self._time_last_beep = time.time()
        self._sleep_until = None

        View.__init__(self, image)

    def update_from_yml(self, config):
        if config is not None:
            self.enabled = config.get("alarm_enable", self.enabled)
            self.interval = config.get("alarm_interval", self.interval)

    def update(self, lights_out=False):
        if self._sleep_until is not None:
            if self._sleep_until > time.time():
                return
            self._sleep_until = None

        if (
            self.enabled
            and not lights_out
            and self._triggered
            and time.time() - self._time_last_beep > self.interval
        ):
            self.piezo.beep(self.beep_frequency, 0.1, blocking=False)
            threading.Timer(
                0.3,
                self.piezo.beep,
                args=[self.beep_frequency, 0.1],
                kwargs={"blocking": False},
            ).start()
            threading.Timer(
                0.6,
                self.piezo.beep,
                args=[self.beep_frequency, 0.1],
                kwargs={"blocking": False},
            ).start()
            self._time_last_beep = time.time()

            self._triggered = False

    def render(self, position=(0, 0)):
        x, y = position
        r = 129
        if self._triggered and self._sleep_until is None:
            r = int(((math.sin(time.time() * 3 * math.pi) + 1.0) / 2.0) * 128) + 127

        if self._sleep_until is None:
            self.icon(icon_alarm, (x, y - 1), (r, 129, 129))
        else:
            self.icon(icon_snooze, (x, y - 1), (r, 129, 129))

    def trigger(self):
        self._triggered = True

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def cancel_sleep(self):
        self._sleep_until = None

    def sleeping(self):
        return self._sleep_until is not None

    def sleep(self, duration=500):
        self._sleep_until = time.time() + duration
