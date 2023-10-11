#!/bin/bash
# install.sh

# Update and install necessary tools
sudo apt-get update
sudo apt-get install -y python3-pip git

# Clone your flask app from GitHub
git clone https://github.com/mh-malekpour/AWS-Cluster-Benchmarking.git

# Navigate to the cloned directory
cd AWS-Cluster-Benchmarking

# Install the requirements
pip3 install -r flask/requirements.txt

# Run the Flask app
nohup python3 app.py &
