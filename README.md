# Peter PlantWatch

My daughter planted sunflower seeds in class today to learn about the different stages of growth and how to care for plants. After a couple of weeks all the kids brought the pots home with the assignment to water them and measure size every week.

I thought, why not combine that with coding, IoT and automation because well we can .. and --> lazy :-)

As every device needs a name we've decided on Peter PlantWatch.

## The project

It started with a Pi Zero W and the Pimoroni Grow HAT but we extended the platform with small aquarium pumps, a BME280 temp/humidity sensor, a camera to take daily snapshots, writing the metrics to a logfile and offloading those metrics to my Splunk back-end for dashboarding.

I designed the brackets, mounts and parts in Blender and printed on my Snapmaker A250. The stands are in lime green and the mounts/brackets are in bright orange.

![PeterPlantwatch](https://github.com/jinjirosan/Peter-PlantWatch/blob/main/images/IMG_9332.png)

![PeterPlantwatch](https://github.com/jinjirosan/Peter-PlantWatch/blob/main/images/IMG_9274.gif)

## Files

We refined the code and split it into modular pieces to be able to easily extend functionality while we're building the project further.

```bash
PeterPlantwatch/
├── main.py
├── config.py
├── views.py
├── controllers.py
├── models.py
├── icons.py
├── constants.py
├── hardware.py
└── plant_logging.py
```

1. **main.py**: Entry point for the application. Initializes hardware, loads configuration, and runs the main loop.
2. **config.py**: Handles loading and saving configuration from/to a YAML file.
3. **views.py**: Contains all view classes responsible for rendering the display.
4. **controllers.py**: Manages switching between different views.
5. **models.py**: Contains data models for Channel and Alarm.
6. **icons.py**: icons used for display
7. **constants.py**: constants
8. **hardware.py**: Handles hardware-specific initializations and interactions (GPIO setup and display initialization).
9. **plant_logging.py**: all the logic for writing the logfiles


The automated plant monitoring system
