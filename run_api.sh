#!/bin/sh

export FLASK_APP=route.py

if [ -f "/etc/ditas/due.json" ]; then
/bin/cp /etc/ditas/due.json ./conf/conf.json
/bin/cp /etc/ditas/blueprint.json ./conf/blueprint.json
fi

ls .

flask run --host=0.0.0.0 &
python main.py
