#!/usr/bin/env python3
# modified by Cecil Coupe from code at https://github.com/K-MTG/ups_shutdown
# Thanks! 
import paho.mqtt.client as mqtt
import sys
import json
import argparse
import warnings
from datetime import datetime
import time
import socket

from lib.Settings import Settings
from lib.Homie_MQTT import Homie_MQTT
import requests
from nut2 import PyNUTClient

# globals
settings = None
hmqtt = None
debug_level = 1
use_syslog = False

def log(msg, level=2):
  global debug_level
  if level > debug_level:
    return
  (dt, micro) = datetime.now().strftime('%H:%M:%S.%f').split('.')
  dt = "%s.%03d" % (dt, int(micro) / 1000)
  logmsg = "%-14.14s%-60.60s" % (dt, msg)
  print(logmsg, flush=True)
 
def shutdown_hubitat(settings):
  ip = settings.hubitat_ip 
  login_data = {  # Hubitat Login Credentials
      'username': settings.hubitat_user,
      'password': settings.hubitat_pw
  }

  with requests.Session() as s:
    try:
      s.get('http://%s/login' % (ip), timeout=5)
      s.post('http://%s/login' % (ip), data=login_data, timeout=5)
      s.post('http://%s/hub/shutdown' % (ip), timeout=5)
      print("Shutdown Command Sent")
    except:
      print("Shutdown Failed")

# process cmdline arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, type=str,
	help="path and name of the json configuration file")
ap.add_argument("-d", "--debug", action='store', type=int, default='3',
  nargs='?', help="debug level, default is 3")
args = vars(ap.parse_args())
# fix debug levels
if args['debug'] == None:
  debug_level = 3
else:
  debug_level = args['debug']
  
settings = Settings(args["conf"], 
                    None,
                    log)
hmqtt = Homie_MQTT(settings)
settings.print()

  
# Now we loop forever
unresp = 0
while True:
  # get the ups data
  status = {}
  try:
    with PyNUTClient() as s:
      status = s.list_vars(settings.nut_ups)
  except:
      pass

  # did we get good values?
  if 'ups.status' not in status or 'battery.charge' not in status or 'battery.runtime' not in status:
    unresp += 1
    if unresp > 5:
      # Send warning to MQTT topic?
      hmqtt.send_pwr_state(status, True)
      log("Can't Reach UPS")
      unresp = 0
      time.sleep(60)
      continue
      
  # reset warning loop when we get a good status
  unresp = 0
  # if On Battery (aka not 'OL')
  if status['ups.status'] != 'OL':
    chg = int(status['battery.charge'])
    tmo = int(status['battery.runtime'])
    if chg <= settings.hubitat_pwr_perc or tmo <= settings.hubitat_pwr_min * 60:
      # pwr off hubitat
      if settings.hubitat_ip:
        shutdown_hubitat(settings)
      log("Hubitat Shutdown")
      
    # send status and warning to MQTT
    log("Running low!!!")
    hmqtt.send_pwr_state(status, True)
    # don't sleep too long running on battery
    time.sleep(60)
    continue
    
  # we got here if everything is normal
  hmqtt.send_pwr_state(status, False)
  time.sleep(settings.mqtt_send_min * 60)
  
