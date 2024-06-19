#!/usr/bin/env python3

from PIL import Image

ICONS_DIR = "/usr/share/grow-monitor/icons"

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
