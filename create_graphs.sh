#!/bin/bash
DIR="/home/pi/"
rrd_data="fridge_temp.rrd"
png_dir="/var/www/html/plot/"
 
#set to C if using Celsius
TEMP_SCALE="F"
 
#define the desired colors for the graphs
INTEMP_COLOR="#CC0000"
MIDTEMP_COLOR="#33cc33"
OUTTEMP_COLOR="#0000FF"
HUMID_COLOR="#00ccff"
 
#hourly
rrdtool graph $png_dir/temp_hourly.png --right-axis 1:0 -w 800 -h 200 --start -12h \
DEF:tempavg=$DIR/$rrd_data:temp:AVERAGE:step=6000 \
LINE2:tempavg$MIDTEMP_COLOR:"Fridge Avg [deg $TEMP_SCALE]" \
DEF:temp=$DIR/$rrd_data:temp:AVERAGE \
LINE4:temp$INTEMP_COLOR:"Temp [deg $TEMP_SCALE]" \
DEF:outtemp=$DIR/$rrd_data:outtemp:AVERAGE \
LINE1:outtemp$OUTTEMP_COLOR:"Fridge Tgt [deg $TEMP_SCALE]" \
DEF:humidity=$DIR/$rrd_data:humidity:AVERAGE \
LINE1:humidity$HUMID_COLOR:"Humidity [%]\n" \
GPRINT:temp:LAST:" Current Temp\:%8.2lf %s"  \
GPRINT:temp:AVERAGE:"Average Temp\:%8.2lf %s"  \
GPRINT:temp:MAX:"Maximum Temp\:%8.2lf %s\n" \
GPRINT:humidity:LAST:"Current Humidity\:%8.2lf %s"  \
GPRINT:humidity:AVERAGE:"Average Humidity\:%8.2lf %s"  \
GPRINT:humidity:MAX:"Maximum Humidity\:%8.2lf %s\n"
 
#daily
rrdtool graph $png_dir/temp_daily.png --right-axis 1:0 -w 800 -h 200 --start -1d \
DEF:tempavg=$DIR/$rrd_data:temp:AVERAGE:step=6000 \
LINE2:tempavg$MIDTEMP_COLOR:"Fridge Avg [deg $TEMP_SCALE]" \
DEF:temp=$DIR/$rrd_data:temp:AVERAGE \
LINE4:temp$INTEMP_COLOR:"Temp [deg $TEMP_SCALE]" \
DEF:outtemp=$DIR/$rrd_data:outtemp:AVERAGE \
LINE1:outtemp$OUTTEMP_COLOR:"Fridge Tgt [deg $TEMP_SCALE]" \
DEF:humidity=$DIR/$rrd_data:humidity:AVERAGE \
LINE1:humidity$HUMID_COLOR:"Humidity [%]\n" \
GPRINT:temp:LAST:" Current Temp\:%8.2lf %s"  \
GPRINT:temp:AVERAGE:"Average Temp\:%8.2lf %s"  \
GPRINT:temp:MAX:"Maximum Temp\:%8.2lf %s\n" \
GPRINT:humidity:LAST:"Current Humidity\:%8.2lf %s"  \
GPRINT:humidity:AVERAGE:"Average Humidity\:%8.2lf %s"  \
GPRINT:humidity:MAX:"Maximum Humidity\:%8.2lf %s\n"
 
#weekly
rrdtool graph $png_dir/temp_weekly.png --right-axis 1:0 -w 800 -h 200 --start -1w \
DEF:tempavg=$DIR/$rrd_data:temp:AVERAGE:step=6000 \
LINE2:tempavg$MIDTEMP_COLOR:"Fridge Avg [deg $TEMP_SCALE]" \
DEF:temp=$DIR/$rrd_data:temp:AVERAGE \
DEF:outtemp=$DIR/$rrd_data:outtemp:AVERAGE \
LINE4:temp$INTEMP_COLOR:"Temp [deg $TEMP_SCALE]" \
LINE1:outtemp$OUTTEMP_COLOR:"Fridge Tgt [deg $TEMP_SCALE]" \
DEF:humidity=$DIR/$rrd_data:humidity:AVERAGE \
LINE1:humidity$HUMID_COLOR:"Humidity [%]\n" \
GPRINT:temp:LAST:"Current Temp\:%8.2lf %s"  \
GPRINT:temp:AVERAGE:"Average Temp\:%8.2lf %s"  \
GPRINT:temp:MAX:"Maximum Temp\:%8.2lf %s\n" \
GPRINT:humidity:LAST:"Current Humidity\:%8.2lf %s"  \
GPRINT:humidity:AVERAGE:"Average Humidity\:%8.2lf %s"  \
GPRINT:humidity:MAX:"Maximum Humidity\:%8.2lf %s\n"
 
#monthly
rrdtool graph $png_dir/temp_monthly.png --right-axis 1:0 -w 800 -h 200 --start -1m \
DEF:tempavg=$DIR/$rrd_data:temp:AVERAGE:step=6000 \
LINE2:tempavg$MIDTEMP_COLOR:"Fridge Avg [deg $TEMP_SCALE]" \
DEF:temp=$DIR/$rrd_data:temp:AVERAGE \
DEF:outtemp=$DIR/$rrd_data:outtemp:AVERAGE \
LINE4:temp$INTEMP_COLOR:"Temp [deg $TEMP_SCALE]" \
LINE1:outtemp$OUTTEMP_COLOR:"Fridge Tgt [deg $TEMP_SCALE]" \
DEF:humidity=$DIR/$rrd_data:humidity:AVERAGE \
LINE1:humidity$HUMID_COLOR:"Humidity [%]\n" \
GPRINT:temp:LAST:" Current Temp\:%8.2lf %s"  \
GPRINT:temp:AVERAGE:"Average Temp\:%8.2lf %s"  \
GPRINT:temp:MAX:"Maximum Temp\:%8.2lf %s\n" \
GPRINT:humidity:LAST:"Current Humidity\:%8.2lf %s"  \
GPRINT:humidity:AVERAGE:"Average Humidity\:%8.2lf %s"  \
GPRINT:humidity:MAX:"Maximum Humidity\:%8.2lf %s\n"


#yearly
rrdtool graph $png_dir/temp_yearly.png --right-axis 1:0 -w 800 -h 200 --start -1y \
DEF:tempavg=$DIR/$rrd_data:temp:AVERAGE:step=6000 \
LINE2:tempavg$MIDTEMP_COLOR:"Fridge Avg [deg $TEMP_SCALE]" \
DEF:temp=$DIR/$rrd_data:temp:AVERAGE \
DEF:outtemp=$DIR/$rrd_data:outtemp:AVERAGE \
LINE4:temp$INTEMP_COLOR:"Temp [deg $TEMP_SCALE]" \
LINE1:outtemp$OUTTEMP_COLOR:"Fridge Tgt [deg $TEMP_SCALE]" \
DEF:humidity=$DIR/$rrd_data:humidity:AVERAGE \
LINE1:humidity$HUMID_COLOR:"Humidity [%]\n" \
GPRINT:temp:LAST:" Current Temp\:%8.2lf %s"  \
GPRINT:temp:AVERAGE:"Average Temp\:%8.2lf %s"  \
GPRINT:temp:MAX:"Maximum Temp\:%8.2lf %s\n" \
GPRINT:humidity:LAST:"Current Humidity\:%8.2lf %s"  \
GPRINT:humidity:AVERAGE:"Average Humidity\:%8.2lf %s"  \
GPRINT:humidity:MAX:"Maximum Humidity\:%8.2lf %s\n"
 
