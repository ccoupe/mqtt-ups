#!/bin/bash
source /home/ccoupe/miniconda3/etc/profile.d/conda.sh
eval "$(conda shell.bash hook)"
conda activate py3
cd /usr/local/lib/mqttups
/usr/bin/python3 mqttups.py -d2 -c bronco.json
