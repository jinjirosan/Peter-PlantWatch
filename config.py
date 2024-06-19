#!/usr/bin/env python3

import yaml
import pathlib
import sys

class Config:
    def __init__(self):
        self.config = {}
        self._last_save = ""

    def load(self, settings_file="settings.yml"):
        settings_file = pathlib.Path(settings_file if len(sys.argv) <= 1 else sys.argv[1])
        if settings_file.is_file():
            try:
                with open(settings_file, "r") as file:
                    self.config = yaml.safe_load(file)
            except yaml.parser.ParserError as e:
                logging.error(f"Error parsing settings file {settings_file}: {e}")
                raise

    def save(self, settings_file="settings.yml"):
        settings_file = pathlib.Path(settings_file if len(sys.argv) <= 1 else sys.argv[1])
        dump = yaml.dump(self.config)
        if dump != self._last_save:
            with open(settings_file, "w") as file:
                file.write(dump)
            self._last_save = dump

    def get_channel(self, channel_id):
        return self.config.get(f"channel{channel_id}", {})

    def set(self, section, settings):
        if not isinstance(settings, dict):
            raise ValueError("Settings should be a dictionary")
        self.config.setdefault(section, {}).update(settings)

    def set_channel(self, channel_id, settings):
        self.set(f"channel{channel_id}", settings)

    def get_general(self):
        return self.config.get("general", {})

    def set_general(self, settings):
        self.set("general", settings)
