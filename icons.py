#!/usr/bin/env python3

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
