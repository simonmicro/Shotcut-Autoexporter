#!/usr/bin/env bash
while true; do
    ./exporter.py;
    echo 'Exporter crashed - restarting...'
    sleep 1;
done
