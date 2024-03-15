# Makefile for restart-node
PRJ=mqttups
DESTDIR=/usr/local/lib/$(PRJ)
SRCDIR=$(HOME)/Projects/iot/$(PRJ)
LAUNCH=$(PRJ).sh
SERVICE=$(PRJ).service

NODE := $(shell hostname)
SHELL := /bin/bash 

$(HOME)/sb-env:
	sudo apt install -y python3-venv
	python3 -m venv $(HOME)/sb-env
	( \
	set -e ;\
	source $(HOME)/sb-env/bin/activate; \
	pip install -r $(SRCDIR)/requirements.txt; \
	)

$(DESTDIR):
	sudo mkdir -p ${DESTDIR}
	sudo mkdir -p ${DESTDIR}/lib	
	sudo cp  ${SRCDIR}/Makefile ${DESTDIR}
	sudo cp  ${SRCDIR}/requirements.txt ${DESTDIR}
	sudo cp  ${SRCDIR}/${LAUNCH} ${DESTDIR}
	sudo cp  ${SRCDIR}/${SERVICE} ${DESTDIR}
	sudo cp  ${SRCDIR}/*.json ${DESTDIR}
	sudo chown -R ${USER} ${DESTDIR}
	sudo chmod +x ${DESTDIR}/${LAUNCH}
	sudo cp ${DESTDIR}/${SERVICE} /etc/systemd/system
	sudo systemctl enable ${SERVICE}
	sudo systemctl daemon-reload
	sudo systemctl restart ${SERVICE}
	
update: 
	cp ${SRCDIR}/${PRJ}.py ${DESTDIR}
	cp ${SRCDIR}/lib/Settings.py ${DESTDIR}/lib
	cp ${SRCDIR}/lib/Homie_MQTT.py ${DESTDIR}/lib

install: $(HOME)/sb-env $(DESTDIR) update

