#!/usr/bin/env python3


from grow.moisture import Moisture
from grow.pump import Pump
from grow import Piezo
from constants import COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW, COLOR_RED
from views import View, icon_alarm, icon_snooze
import logging
import time
import threading
import math

class Channel:
    colors = [COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW, COLOR_RED]

    def __init__(self, display_channel, sensor_channel, pump_channel, title=None, water_level=0.5, warn_level=0.5, pump_speed=0.5, pump_time=0.2, watering_delay=60, wet_point=0.7, dry_point=26.7, icon=None, auto_water=False, enabled=False):
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

    def __str__(self):
        return f"""Channel: {self.channel}
Enabled: {self.enabled}
Alarm level: {self.warn_level}
Auto water: {self.auto_water}
Water level: {self.water_level}
Pump speed: {self.pump_speed}
Pump time: {self.pump_time}
Delay: {self.watering_delay}
Wet point: {self.wet_point}
Dry point: {self.dry_point}
"""

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
        if sat < self.water_level:
            if self.water():
                logging.info(f"Watering Channel: {self.channel} - rate {self.pump_speed:.2f} for {self.pump_time:.2f}sec")
        if sat < self.warn_level:
            if not self.alarm:
                logging.warning(f"Alarm on Channel: {self.channel} - saturation is {sat * 100:.2f}% (warn level {self.warn_level * 100:.2f}%)")
            self.alarm = True
        else:
            self.alarm = False

class Alarm(View):
    def __init__(self, image, enabled=True, interval=10.0, beep_frequency=440):
        self.piezo = Piezo()
        self.enabled = enabled
        self.interval = interval
        self.beep_frequency = beep_frequency
        self._triggered = False
        self._time_last_beep = time.time()
        self._sleep_until = None
        super().__init__(image)

    def update_from_yml(self, config):
        if config is not None:
            self.enabled = config.get("alarm_enable", self.enabled)
            self.interval = config.get("alarm_interval", self.interval)

    def update(self, lights_out=False):
        if self._sleep_until is not None:
            if self._sleep_until > time.time():
                return
            self._sleep_until = None

        if self.enabled and not lights_out and self._triggered and time.time() - self._time_last_beep > self.interval:
            self.piezo.beep(self.beep_frequency, 0.1, blocking=False)
            threading.Timer(0.3, self.piezo.beep, args=[self.beep_frequency, 0.1], kwargs={"blocking": False}).start()
            threading.Timer(0.6, self.piezo.beep, args=[self.beep_frequency, 0.1], kwargs={"blocking": False}).start()
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