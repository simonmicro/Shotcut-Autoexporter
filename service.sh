#!/usr/bin/env bash
notify-send --urgency=normal 'Exporter started...'
cd $(dirname $0)
while true; do
    ./exporter.py;
    echo 
    notify-send --urgency=critical 'Exporter crashed - restarting...'
    sleep 1;
done
