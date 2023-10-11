#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install -r /home/ubuntu/requirements.txt
python3 /home/ubuntu/app.py &