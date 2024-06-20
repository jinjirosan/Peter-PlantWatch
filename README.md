# Peter PlantWatch

My daughter planted sunflower seeds in class today to learn about the different stages of growth and how to care for plants. After a couple of weeks all the kids brought the pots home with the assignment to water them and measure size every week.

I thought, why not combine that with coding, IoT and automation because well we can .. and --> lazy :-)

As every device needs a name we've decided on Peter PlantWatch.

## The project

It started with a Pi Zero W and the Pimoroni Grow HAT but we extended the platform with small aquarium pumps, a BME280 temp/humidity sensor, a camera to take daily snapshots, writing the metrics to a logfile and offloading those metrics to my Splunk back-end for dashboarding.

## Files

We refined the code and split it into modular pieces to be able to easily extend functionality while we're building the project further.

```bash
PeterPlantwatch/
├── main.py  (Entry point for the application. Initializes hardware, loads configuration, and runs the main loop.)
├── config.py
├── views.py
├── controllers.py
├── models.py
├── icons.py
├── constants.py
├── hardware.py
└── plant_logging.py
```

The automated plant monitoring system
