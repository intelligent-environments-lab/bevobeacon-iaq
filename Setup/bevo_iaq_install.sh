#!/bin/bash

# Update package list
sudo apt-get update
sudo apt-get upgrade

# Install python 2 & 3
sudo apt-get install python
sudo apt-get install python3

# Install pip & pip3
sudo apt-get install python-pip -y # Python 2
sudo apt-get install python3-pip -y # Python 3

# Install pandas and numpy
apt install python3-pandas -y
apt install python3-numpy -y

# Install other packages
sudo apt-get install python-pigpio -y

# Replace pigpiod service file with bug free version
install -o root -g root -m 0644 systemd/pigpiod.service /lib/systemd/system/pigpiod.service
systemctl enable pigpiod
systemctl start pigpiod

# Write environment file for environment variables
# *** CODE HERE ***

# Set up locale, timezone, language
timedatectl set-timezone US/Central

# # Install Hamachi
# apt upgrade
# apt install lsb lsb-core
wget https://www.vpn.net/installers/logmein-hamachi_2.1.0.203–1_armhf.deb
dpkg -i logmein-hamachi_2.1.0.203–1_armhf.deb
# hamachi set-nick
# hamachi login
# hamachi attach hello@yoursite.com

# Reboot
sudo reboot
