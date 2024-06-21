#!/bin/bash
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
# Description        : automation to put all the files in the correct spot on the Raspberry
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
# deploy.py : v1-1.1 (stable) - refactor C1.0.0

# Define directories
REPO_DIR="/home/pi/github/Peter-PlantWatch"
DEPLOY_DIR="/usr/share/peterplantwatch"

# Navigate to the repository directory
cd $REPO_DIR
if [ $? -ne 0 ]; then
  echo "Error: Unable to navigate to repository directory."
  exit 1
fi

# Pull the latest changes from the main branch with rebase
git pull origin main --rebase
if [ $? -ne 0 ]; then
  echo "Error: Git pull failed."
  exit 1
fi

# Remove existing Python files in the deploy directory
rm -rf $DEPLOY_DIR/*.py
if [ $? -ne 0 ]; then
  echo "Error: Unable to remove old files in deploy directory."
  exit 1
fi

# Copy new Python files to the deploy directory
cp $REPO_DIR/*.py $DEPLOY_DIR/
if [ $? -ne 0 ]; then
  echo "Error: Unable to copy new files to deploy directory."
  exit 1
fi

# Navigate to the deploy directory
cd $DEPLOY_DIR
if [ $? -ne 0 ]; then
  echo "Error: Unable to navigate to deploy directory."
  exit 1
fi

# Make the Python files executable
chmod +x $DEPLOY_DIR/*.py
if [ $? -ne 0 ]; then
  echo "Error: Unable to set executable permission on Python files."
  exit 1
fi

echo "Deployment completed successfully."
