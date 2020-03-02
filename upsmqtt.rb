#!/usr/bin/env ruby
require 'json'
require 'yaml'
blob = `upsc apc@localhost`.chop
yml = YAML.load(blob)
fo = open("/tmp/ups.json", 'w')
fo.puts yml.to_json
fo.close
`mosquitto_pub -h 192.168.1.7 -t ups/office/pi4/json -r -f /tmp/ups.json`
