#!/bin/bash

# Use git as version control to receive updates when needed
sudo apt-get install git

# Clone the open-source dashboard code
cd /home/rogier/
git clone https://github.com/johanhendriks/olaf
git pull
sudo chmod ugo+x /home/rogier/olaf/dashboard_start.sh
sudo chown rogier /home/rogier/olaf/dashboard_start.sh
sudo chgrp rogier /home/rogier/olaf/dashboard_start.sh
sudo chmod ugo+x /home/rogier/olaf/rogierdashboard.py
sudo chown rogier /home/rogier/olaf/rogierdashboard.py
sudo chgrp rogier /home/rogier/olaf/rogierdashboard.py

# Install dependencies
sudo -u rogier pip install pandas
sudo apt-get install -y libatlas-base-dev
sudo -u rogier pip install plotly
sudo -u rogier pip install dash

# Install dashboard as a service
sudo cp /home/rogier/olaf/dashboard.service /etc/systemd/system/dashboard.service

# Load the service into duty
sudo systemctl daemon-reload
sudo systemctl enable dashboard.service
sudo systemctl restart dashboard.service

sudo reboot
