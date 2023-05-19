#! /bin/bash
cp -a /home/ccoupe/Projects/iot/ups/* /usr/local/lib/mqttups
systemctl restart mqttups
