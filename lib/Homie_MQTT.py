#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import sys
import json

from datetime import datetime
import time,threading, sched

import time

class Homie_MQTT:

  def __init__(self, settings):
    self.settings = settings
    self.log = settings.log
 
    # init server connection
    self.client = mqtt.Client(settings.mqtt_client_name, False)
    #self.client.max_queued_messages_set(3)
    hdevice = self.hdevice = self.settings.homie_device  # "device_name"
    hlname = self.hlname = self.settings.homie_name     # "Display Name"
    # beware async timing with on_connect
    self.client.on_connect = self.on_connect
    self.client.on_subscribe = self.on_subscribe
    self.client.on_message = self.on_message
    self.client.on_disconnect = self.on_disconnect
    rc = self.client.connect(settings.mqtt_server, settings.mqtt_port)
    if rc != mqtt.MQTT_ERR_SUCCESS:
        print("network missing?")
        exit()
    self.client.loop_start()
      
    # short cuts to stuff we really care about
    self.source_pub = "homie/"+hdevice+"/sensor/source"
    self.level_pub = "homie/"+hdevice+"/sensor/level"
    self.runtime_pub = "homie/"+hdevice+"/sensor/runtime"
    self.json_pub = "homie/"+hdevice+"/sensor/json"

    print("Homie_MQTT __init__")
    self.create_topics(hdevice, hlname)
    
  def create_topics(self, hdevice, hlname):
    print("Begin topic creation")
    # create topic structure at server - these are retained! 
    self.publish_structure("homie/"+hdevice+"/$homie", "3.0.1")
    self.publish_structure("homie/"+hdevice+"/$name", hlname)
    self.publish_structure("homie/"+hdevice+"/$state", "ready")
    self.publish_structure("homie/"+hdevice+"/$mac", self.settings.macAddr)
    self.publish_structure("homie/"+hdevice+"/$localip", self.settings.our_IP)
    self.publish_structure("homie/"+hdevice+"/$nodes", "sensor")
    # sensor node, type = ups
    self.publish_structure("homie/"+hdevice+"/sensor/$name", hlname)
    self.publish_structure("homie/"+hdevice+"/sensor/$type", "ups")
    self.publish_structure("homie/"+hdevice+"/sensor/$properties","source,level,runtime,json")
    # Property of 'source' = [mains, battery]
    self.publish_structure("homie/"+hdevice+"/sensor/source/$name", hlname)
    self.publish_structure("homie/"+hdevice+"/sensor/source/$datatype", "string")
    self.publish_structure("homie/"+hdevice+"/sensor/source/$settable", "false")
    self.publish_structure("homie/"+hdevice+"/sensor/source/$retained", "true")
    # Property of 'level' = 0..100 %implied
    self.publish_structure("homie/"+hdevice+"/sensor/level/$name", hlname)
    self.publish_structure("homie/"+hdevice+"/sensor/level/$datatype", "integer")
    self.publish_structure("homie/"+hdevice+"/sensor/level/$format", "0:100")
    self.publish_structure("homie/"+hdevice+"/sensor/level/$settable", "false")
    self.publish_structure("homie/"+hdevice+"/sensor/level/$retained", "true")
    # Property of 'runtime' = 0..1440 minutes
    self.publish_structure("homie/"+hdevice+"/sensor/runtime/$name", hlname)
    self.publish_structure("homie/"+hdevice+"/sensor/runtime/$datatype", "integer")
    self.publish_structure("homie/"+hdevice+"/sensor/runtime/$format", "0:1440")
    self.publish_structure("homie/"+hdevice+"/sensor/runtime/$settable", "false")
    self.publish_structure("homie/"+hdevice+"/sensor/runtime/$retained", "true")
    # Property of 'json' = 0..100 minutes
    self.publish_structure("homie/"+hdevice+"/sensor/json/$name", hlname)
    self.publish_structure("homie/"+hdevice+"/sensor/json/$datatype", "integer")
    self.publish_structure("homie/"+hdevice+"/sensor/json/$settable", "false")
    self.publish_structure("homie/"+hdevice+"/sensor/json/$retained", "true")
   # Done with structure. 

    print("homie topics created")
    # nothing else to publish 
    
  def publish_structure(self, topic, payload):
    self.client.publish(topic, payload, qos=1, retain=True)
    
  def on_subscribe(self, client, userdata, mid, granted_qos):
    print("Subscribed to %s" % self.hurl_sub)

  def on_message(self, client, userdata, message):
    global settings
    topic = message.topic
    payload = str(message.payload.decode("utf-8"))
    print("on_message ", topic, " ", payload)
    
  def isConnected(self):
    return self.mqtt_connected

  def on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      print("Connecting to %s" % self.mqtt_server_ip)
    else:
      print("Failed to connect:", rc)
       
  def on_disconnect(self, client, userdata, rc):
    self.mqtt_connected = False
    log("mqtt reconnecting")
    self.client.reconnect()
      
  def send_pwr_state(self, status, warning):
    st = 'mains'
    if status['ups.status'] == 'OB':
      st = 'battery'
    self.client.publish(self.source_pub, st, qos=1, retain=False)
    self.client.publish(self.level_pub, status['battery.charge'], qos=1, retain=False)
    self.client.publish(self.runtime_pub, status['battery.runtime'], qos=1, retain=False)
    # json
    self.client.publish(self.json_pub, json.dumps(status), qos=1, retain=False)
    print(status)
  
