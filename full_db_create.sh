#!/bin/bash
DB_FILE="coolidor.rrd"

if [ -f "$DB_FILE" ]; then
    echo "$DB_FILE already exists. Delete it first if you want a fresh DB."
    exit 1
fi

rrdtool create "$DB_FILE" \
    --step 60 \
    DS:temperature:GAUGE:120:-40:100 \
    DS:humidity:GAUGE:120:0:100 \
    RRA:AVERAGE:0.5:1:1440 \
    RRA:AVERAGE:0.5:5:2016 \
    RRA:AVERAGE:0.5:30:1488 \
    RRA:AVERAGE:0.5:120:2190 \
    RRA:MIN:0.5:5:2016 \
    RRA:MIN:0.5:30:1488 \
    RRA:MIN:0.5:120:2190 \
    RRA:MAX:0.5:5:2016 \
    RRA:MAX:0.5:30:1488 \
    RRA:MAX:0.5:120:2190

echo "$DB_FILE created successfully."
