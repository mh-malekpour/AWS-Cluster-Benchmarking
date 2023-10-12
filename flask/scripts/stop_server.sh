#!/bin/bash

PID="/home/ubuntu/server/pid_file"

if [[ -e $PID ]]; then
  sudo kill "$(cat $PID)"
else
  sudo pkill -f gunicorn
fi
