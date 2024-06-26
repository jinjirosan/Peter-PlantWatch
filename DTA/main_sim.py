#!/usr/bin/env python3

import time
import logging
from config_sim import log_dir
from models_sim import Channel, Context
from mock_sensor_data import generate_mock_data
from plant_logging_sim import log_values

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize channels
channels = [
    Channel(display_channel=1, sensor_channel=1, pump_channel=1, auto_water=True, enabled=True),
    Channel(display_channel=2, sensor_channel=2, pump_channel=2, auto_water=True, enabled=True),
    Channel(display_channel=3, sensor_channel=3, pump_channel=3, auto_water=True, enabled=True),
]

# Simulate updates
for _ in range(100):  # Run 100 simulation cycles
    mock_data = generate_mock_data()
    context = Context(light_level=mock_data['light_level'])
    
    for channel in channels:
        # Update sensor data
        channel.sensor.moisture = mock_data['moisture']
        channel.sensor.saturation = mock_data['saturation']
        
        # Run the update method
        channel.update(context)
    
    time.sleep(1)  # Simulate time passing between updates
