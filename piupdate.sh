#! /bin/bash
cp -a /home/pi/Projects/iot/ups/* /usr/local/lib/mqttups
systemctl restart mqttups
