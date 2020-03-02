# MQTT UPS Monitor
git clone, cd.
sudo pip3 install paho-mqtt nut2
pi@pi4:~ $ sudo mkdir -p /usr/local/lib/mqttups
pi@pi4:~ $ sudo cp -r ~/Projects/iot/ups/* /usr/local/lib/mqttups/
pi@pi4:~ $ cd /usr/local/lib/mqttups/
pi@pi4:/usr/local/lib/mqttups $ sudo -s
root@pi4:/usr/local/lib/mqttups# vi mqttups.sh
root@pi4:/usr/local/lib/mqttups# vi pi4.json 
root@pi4:/usr/local/lib/mqttups# ./mqttups.sh 
  ^C
root@pi4:/usr/local/lib/mqttups# cp mqttups.sh /usr/local/bin/
root@pi4:/usr/local/lib/mqttups# cp mqttups.service /etc/systemd/system
root@pi4:/usr/local/lib/mqttups# systemctl enable mqttups
root@pi4:/usr/local/lib/mqttups# systemctl start mqttups

