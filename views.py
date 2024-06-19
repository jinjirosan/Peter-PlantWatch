#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
import math
import time
from constants import DISPLAY_WIDTH, DISPLAY_HEIGHT, COLOR_WHITE, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_BLACK
from fonts.ttf import RobotoMedium as UserFont

# Update paths to icons
ICONS_DIR = "/usr/share/grow-monitor/icons"

# Load icons
icon_drop = Image.open(f"{ICONS_DIR}/icon-drop.png").convert("RGBA")
icon_nodrop = Image.open(f"{ICONS_DIR}/icon-nodrop.png").convert("RGBA")
icon_rightarrow = Image.open(f"{ICONS_DIR}/icon-rightarrow.png").convert("RGBA")
icon_alarm = Image.open(f"{ICONS_DIR}/icon-alarm.png").convert("RGBA")
icon_snooze = Image.open(f"{ICONS_DIR}/icon-snooze.png").convert("RGBA")
icon_help = Image.open(f"{ICONS_DIR}/icon-help.png").convert("RGBA")
icon_settings = Image.open(f"{ICONS_DIR}/icon-settings.png").convert("RGBA")
icon_channel = Image.open(f"{ICONS_DIR}/icon-channel.png").convert("RGBA")
icon_backdrop = Image.open(f"{ICONS_DIR}/icon-backdrop.png").convert("RGBA")
icon_return = Image.open(f"{ICONS_DIR}/icon-return.png").convert("RGBA")

class View:
    def __init__(self, image):
        self._image = image
        self._draw = ImageDraw.Draw(image)
        self.font = ImageFont.truetype(UserFont, 14)
        self.font_small = ImageFont.truetype(UserFont, 10)

    def update(self): pass
    def render(self): pass
    def clear(self):
        self._draw.rectangle((0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0))

    def icon(self, icon, position, color):
        col = Image.new("RGBA", icon.size, color=color)
        self._image.paste(col, position, mask=icon)

    def label(self, position="X", text=None, bgcolor=(0, 0, 0), textcolor=(255, 255, 255), margin=4):
        if position not in ["A", "B", "X", "Y"]:
            raise ValueError(f"Invalid label position {position}")

        text_w, text_h = self._draw.textsize(text, font=self.font)
        text_h, text_w = 11, text_w + margin * 2 + 2

        x, y = {"A": (0, 0), "B": (0, DISPLAY_HEIGHT - text_h), "X": (DISPLAY_WIDTH - text_w, 0), "Y": (DISPLAY_WIDTH - text_w, DISPLAY_HEIGHT - text_h)}[position]
        x2, y2 = x + text_w, y + text_h

        self._draw.rectangle((x, y, x2, y2), bgcolor)
        self._draw.text((x + margin, y + margin - 1), text, font=self.font, fill=textcolor)

    def overlay(self, text, top=0):
        self._draw.rectangle((0, top, DISPLAY_WIDTH, DISPLAY_HEIGHT), fill=(192, 225, 254))
        self._draw.rectangle((0, top, DISPLAY_WIDTH, top + 1), fill=COLOR_BLUE)
        self.text_in_rect(text, self.font, (3, top, DISPLAY_WIDTH - 3, DISPLAY_HEIGHT - 2), line_spacing=1)

    def text_in_rect(self, text, font, rect, line_spacing=1.1, textcolor=(0, 0, 0)):
        x1, y1, x2, y2 = rect
        width, height = x2 - x1, y2 - y1

        while font.size > 0:
            space_width = font.getsize(" ")[0]
            line_height = int(font.size * line_spacing)
            max_lines = math.floor(height / line_height)
            lines = []
            words = text.split(" ")

            while len(lines) < max_lines and len(words) > 0:
                line = []
                while len(words) > 0 and font.getsize(" ".join(line + [words[0]]))[0] <= width:
                    line.append(words.pop(0))
                lines.append(" ".join(line))

            if len(lines) <= max_lines and len(words) == 0:
                y = int(y1 + (height / 2) - (len(lines) * line_height / 2) - (line_height - font.size) / 2)
                bounds = [x2, y, x1, y + len(lines) * line_height]

                for line in lines:
                    line_width = font.getsize(line)[0]
                    x = int(x1 + (width / 2) - (line_width / 2))
                    bounds[0] = min(bounds[0], x)
                    bounds[2] = max(bounds[2], x + line_width)
                    self._draw.text((x, y), line, font=self.font, fill=textcolor)
                    y += line_height
                return tuple(bounds)

            font = ImageFont.truetype(font.path, font.size - 1)

class MainView(View):
    def __init__(self, image, channels=None, alarm=None):
        super().__init__(image)
        self.channels = channels
        self.alarm = alarm

    def render_channel(self, channel):
        bar_x = 33
        bar_margin = 2
        bar_width = 30
        label_width = 16
        label_y = 0

        x = [bar_x, bar_x + ((bar_width + bar_margin) * 1), bar_x + ((bar_width + bar_margin) * 2)][channel.channel - 1]
        saturation = channel.sensor.saturation
        active = channel.sensor.active and channel.enabled
        warn_level = channel.warn_level

        if active:
            self._draw.rectangle((x, int((1.0 - saturation) * DISPLAY_HEIGHT), x + bar_width - 1, DISPLAY_HEIGHT),
                                 channel.indicator_color(saturation) if active else (229, 229, 229))

        y = int((1.0 - warn_level) * DISPLAY_HEIGHT)
        self._draw.rectangle((x, y, x + bar_width - 1, y), (255, 0, 0) if channel.alarm else (0, 0, 0))

        x += (bar_width - label_width) // 2
        self.icon(icon_channel, (x, label_y), (200, 200, 200) if active else (64, 64, 64))
        tw, th = self.font.getsize(str(channel.channel))
        self._draw.text((x + int(math.ceil(8 - (tw / 2.0))), label_y + 1), str(channel.channel), font=self.font,
                        fill=(55, 55, 55) if active else (100, 100, 100))

    def render(self):
        self.clear()
        for channel in self.channels:
            self.render_channel(channel)
        self.icon(icon_backdrop, (0, 0), COLOR_WHITE)
        self.icon(icon_rightarrow, (3, 3), (55, 55, 55))
        self.alarm.render((3, DISPLAY_HEIGHT - 23))
        self.icon(icon_backdrop.rotate(180), (DISPLAY_WIDTH - 26, 0), COLOR_WHITE)
        self.icon(icon_settings, (DISPLAY_WIDTH - 19 - 3, 3), (55, 55, 55))

    def button_a(self):
        return False

    def button_b(self):
        return False

    def button_x(self):
        return False

    def button_y(self):
        return False

class EditView(View):
    def __init__(self, image, options=[]):
        super().__init__(image)
        self._options = options
        self._current_option = 0
        self._change_mode = False
        self._help_mode = False
        self.channel = None

    def render(self):
        self.icon(icon_backdrop.rotate(180), (DISPLAY_WIDTH - 26, 0), COLOR_WHITE)
        self.icon(icon_return, (DISPLAY_WIDTH - 19 - 3, 3), (55, 55, 55))

        option = self._options[self._current_option]
        title = option["title"]
        prop = option["prop"]
        obj = option.get("object", self.channel)
        value = getattr(obj, prop)
        text = option["format"](value)
        mode = option.get("mode", "int")
        help_text = option["help"]

        if self._change_mode:
            self.label("Y", "Yes" if mode == "bool" else "++", textcolor=COLOR_BLACK, bgcolor=COLOR_WHITE)
            self.label("B", "No" if mode == "bool" else "--", textcolor=COLOR_BLACK, bgcolor=COLOR_WHITE)
        else:
            self.label("B", "Next", textcolor=COLOR_BLACK, bgcolor=COLOR_WHITE)
            self.label("Y", "Change", textcolor=COLOR_BLACK, bgcolor=COLOR_WHITE)

        self._draw.text((3, 36), f"{title} : {text}", font=self.font, fill=COLOR_WHITE)

        if self._help_mode:
            self.icon(icon_backdrop.rotate(90), (0, 0), COLOR_BLUE)
            self._draw.rectangle((7, 3, 23, 19), COLOR_BLACK)
            self.overlay(help_text, top=26)

        self.icon(icon_help, (0, 0), COLOR_BLUE)

    def button_a(self):
        self._help_mode = not self._help_mode
        return True

    def button_b(self):
        if self._help_mode:
            return True

        if self._change_mode:
            option = self._options[self._current_option]
            prop = option["prop"]
            mode = option.get("mode", "int")
            obj = option.get("object", self.channel)

            value = getattr(obj, prop)
            if mode == "bool":
                value = False
            else:
                inc = option["inc"]
                limit = option["min"]
                value -= inc
                if mode == "float":
                    value = round(value, option.get("round", 1))
                if value < limit:
                    value = limit
            setattr(obj, prop, value)
        else:
            self._current_option += 1
            self._current_option %= len(self._options)

        return True

    def button_x(self):
        if self._change_mode:
            self._change_mode = False
            return True
        return False

    def button_y(self):
        if self._help_mode:
            return True
        if self._change_mode:
            option = self._options[self._current_option]
            prop = option["prop"]
            mode = option.get("mode", "int")
            obj = option.get("object", self.channel)

            value = getattr(obj, prop)
            if mode == "bool":
                value = True
            else:
                inc = option["inc"]
                limit = option["max"]
                value += inc
                if mode == "float":
                    value = round(value, option.get("round", 1))
                if value > limit:
                    value = limit
            setattr(obj, prop, value)
        else:
            self._change_mode = True

        return True

class SettingsView(EditView):
    def __init__(self, image, options=[]):
        super().__init__(image, options)

    def render(self):
        self.clear()
        self._draw.text((28, 5), "Settings", font=self.font, fill=COLOR_WHITE)
        super().render()

class ChannelView(View):
    def __init__(self, image, channel=None):
        super().__init__(image)
        self.channel = channel

    def draw_status(self, position):
        status = f"Sat: {self.channel.sensor.saturation * 100:.2f}%"
        self._draw.text(position, status, font=self.font, fill=(255, 255, 255))

    def draw_context(self, position, metric="Hz"):
        context = f"Now: {self.channel.sensor.moisture:.2f}Hz"
        if metric.lower() == "sat":
            context = f"Now: {self.channel.sensor.saturation * 100:.2f}%"
        self._draw.text(position, context, font=self.font, fill=(255, 255, 255))

class DetailView(ChannelView):
    def render(self):
        self.clear()
        if self.channel.enabled:
            graph_height = DISPLAY_HEIGHT - 8 - 20
            graph_width = DISPLAY_WIDTH - 64
            graph_x = (DISPLAY_WIDTH - graph_width) // 2
            graph_y = 8

            self.draw_status((graph_x, graph_y + graph_height + 4))
            self._draw.rectangle((graph_x, graph_y, graph_x + graph_width, graph_y + graph_height), (50, 50, 50))

            for x, value in enumerate(self.channel.sensor.history[:graph_width]):
                color = self.channel.indicator_color(value)
                h = value * graph_height
                x = graph_x + graph_width - x - 1
                self._draw.rectangle((x, graph_y + graph_height - h, x + 1, graph_y + graph_height), color)

            alarm_line = int(self.channel.warn_level * graph_height)
            r = 255
            if self.channel.alarm:
                r = int(((math.sin(time.time() * 3 * math.pi) + 1.0) / 2.0) * 128) + 127

            self._draw.rectangle((0, graph_height + 8 - alarm_line, DISPLAY_WIDTH - 40, graph_height + 8 - alarm_line), (r, 0, 0))
            self._draw.rectangle((DISPLAY_WIDTH - 20, graph_height + 8 - alarm_line, DISPLAY_WIDTH, graph_height + 8 - alarm_line), (r, 0, 0))
            self.icon(icon_alarm, (DISPLAY_WIDTH - 40, graph_height + 8 - alarm_line - 10), (r, 0, 0))

        x_positions = [40, 72, 104]
        label_x = x_positions[self.channel.channel - 1]
        label_y = 0
        active = self.channel.sensor.active and self.channel.enabled

        for x in x_positions:
            self.icon(icon_channel, (x, label_y - 10), (16, 16, 16))

        self.icon(icon_channel, (label_x, label_y), (200, 200, 200))
        tw, th = self.font.getsize(str(self.channel.channel))
        self._draw.text((label_x + int(math.ceil(8 - (tw / 2.0))), label_y + 1), str(self.channel.channel), font=self.font, fill=(55, 55, 55) if active else (100, 100, 100))

        self.icon(icon_backdrop, (0, 0), COLOR_WHITE)
        self.icon(icon_rightarrow, (3, 3), (55, 55, 55))
        self.icon(icon_backdrop.rotate(180), (DISPLAY_WIDTH - 26, 0), COLOR_WHITE)
        self.icon(icon_settings, (DISPLAY_WIDTH - 19 - 3, 3), (55, 55, 55))

class ChannelEditView(ChannelView, EditView):
    def __init__(self, image, channel=None):
        options = [
            {"title": "Alarm Level", "prop": "warn_level", "inc": 0.05, "min": 0, "max": 1.0, "mode": "float", "round": 2, "format": lambda value: f"{value * 100:0.2f}%", "help": "Saturation at which alarm is triggered", "context": "sat"},
            {"title": "Enabled", "prop": "enabled", "mode": "bool", "format": lambda value: "Yes" if value else "No", "help": "Enable/disable this channel"},
            {"title": "Watering Level", "prop": "water_level", "inc": 0.05, "min": 0, "max": 1.0, "mode": "float", "round": 2, "format": lambda value: f"{value * 100:0.2f}%", "help": "Saturation at which watering occurs", "context": "sat"},
            {"title": "Auto Water", "prop": "auto_water", "mode": "bool", "format": lambda value: "Yes" if value else "No", "help": "Enable/disable watering"},
            {"title": "Wet Point", "prop": "wet_point", "inc": 0.5, "min": 1, "max": 27, "mode": "float", "round": 2, "format": lambda value: f"{value:0.2f}Hz", "help": "Frequency for fully saturated soil", "context": "hz"},
            {"title": "Dry Point", "prop": "dry_point", "inc": 0.5, "min": 1, "max": 27, "mode": "float", "round": 2, "format": lambda value: f"{value:0.2f}Hz", "help": "Frequency for fully dried soil", "context": "hz"},
            {"title": "Pump Time", "prop": "pump_time", "inc": 0.05, "min": 0.05, "max": 2.0, "mode": "float", "round": 2, "format": lambda value: f"{value:0.2f}sec", "help": "Time to run pump"},
            {"title": "Pump Speed", "prop": "pump_speed", "inc": 0.05, "min": 0.05, "max": 1.0, "mode": "float", "round": 2, "format": lambda value: f"{value*100:0.0f}%", "help": "Speed of pump"},
            {"title": "Watering Delay", "prop": "watering_delay", "inc": 10, "min": 30, "max": 500, "mode": "int", "format": lambda value: f"{value:0.0f}sec", "help": "Delay between waterings"},
        ]
        EditView.__init__(self, image, options)
        ChannelView.__init__(self, image, channel)

    def render(self):
        self.clear()
        super().render()
        option = self._options[self._current_option]
        if "context" in option:
            self.draw_context((34, 6), option["context"])
