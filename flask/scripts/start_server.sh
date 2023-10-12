#!/bin/bash

DIR="/home/ubuntu/server/"
GUNICORN="${DIR}venv/bin/gunicorn"
APP="wsgi:app"
PID="pid_file"
ADDRESS="0.0.0.0:80"
WRK_COUNT=5
LOGS="${DIR}gunicorn.log"

sudo "$GUNICORN" --chdir $DIR --workers $WRK_COUNT --bind $ADDRESS --pid $PID --daemon --access-logfile $LOGS $APP