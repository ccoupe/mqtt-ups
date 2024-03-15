#!/bin/bash
nm-online
source /home/ccoupe/sb-env/bin/activate
NODE=`hostname`
cd /usr/local/lib/mqttups
python3 mqttups.py -d2 -c ${NODE}.json
