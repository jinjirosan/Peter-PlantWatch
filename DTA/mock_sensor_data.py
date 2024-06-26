# mock_sensor_data.py

import random

def generate_mock_data():
    return {
        'moisture': random.uniform(4.0, 5.0),
        'saturation': random.uniform(0.1, 0.5),
        'light_level': random.uniform(30.0, 60.0)
    }
