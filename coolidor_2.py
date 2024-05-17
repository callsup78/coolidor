#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Rewrite: David Smith 
# Version: 1.0a
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys, os.path, traceback, json
import time, rrdtool
import Adafruit_DHT
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(powerpin, GPIO.OUT)
GPIO.output(powerpin, 0) # set pin low
GPIO.setup(powerpin2, GPIO.OUT)
GPIO.output(powerpin2, 0) # set pin low
GPIO.setup(sensor_power, GPIO.OUT)
GPIO.output(sensor_power, 0) # set pin low

sensor = 22
sensor_power = 11 # BOARD pin 11 / gpio pin 17 handles sensor +power
pin = 4 # gpio pin 4 for sensor read pin
coolidor_file = 'coolidor.json'
powerpin = 16  # Raspi Z2W pin 16 GPIO # 22 - Power output pin to relay for Humidity
powerpin2 = 18 # Raspi Z2W pin 18 GPIO # 24 - Power output pin to relay for Humidity
hightemp_max = 72 # if we end up above 70, and we are trending up, turn off!!
hightemp = 68 # high temperature allowed, F - above this, turn on
lowtemp = 64 # low temperature allowed, F - below this, turn off
settemp = 66 # settemp is replacing high/low - if settemp were
highhumi_max = 72 # if we end up above 72, and we are trending up, turn off!!
highhumi = 70 # high humidity allowed, % - above this, turn off
lowhumi = 64 # low humidity allowed, % - below this, turn on
sethumi = 68 # sethumi is replacing high/low - if sethumi were
retries = 5 # default retries to get temp sensor data
output_mode = False # set default, false is off, true is on
no_actuate = False # 0 if disabled, 1 if enabled - if enabled, don't alter output state, just simulate.


def reset_sensor(sensor_power, offtime=10):
    print ('Resetting sensor power pin...')
    GPIO.output(sensor_power, 0) # set pin low
    time.sleep(offtime)
    GPIO.output(sensor_power, 1) # set pin high
    time.sleep(2)
    print ('Temp sensor reset complete.')

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
def get_temp(retries=5):
    humidity = None
    tempC = None
    while (tempC is None or humidity is None) and retries > 0:
        humidity, tempC = Adafruit_DHT.read(sensor, pin)
        retries -= 1
        time.sleep(2)
        print(('Retries: {}'.format(retries)))
        if retries == 0:
            return 0,0,False # return false if reading is invalid
        if humidity is not None:
            if humidity > 100: # bad read, try again
                humidity = None
                tempC = None
# Un-comment the line below to convert the temperature to Fahrenheit.
# temperature = temperature * 9/5.0 + 32
    tempF = tempC * 9/5.0 + 32
    return tempF, humidity, True # true if reading is valid


# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).  
# If this happens try again!
#if humidity is not None and temperature is not None:
#	print 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
#else:
#	print 'Failed to get reading. Try again!'
#	sys.exit(1)

def set_output(hightemp, lowtemp, current_temp, highhumi, lowhumi, current_humi, no_actuate):
    if current_temp > hightemp:
        if not no_actuate:
            GPIO.output(powerpin, 1) # set pin high
        output = True
    elif current_temp < lowtemp:
        if not no_actuate:
            GPIO.output(powerpin, 0) # set pin low
        output = False
    else:
        if int(GPIO.input(powerpin)) == 0:
            output = False
        else:
            output = True 
    print(('Set output: {} - No_Actuate: {}'.format(output, no_actuate)))
    return output

def main_run():
    reset_sensor(sensor_power)
    reset_count = 0
    output_mode = False
    no_actuate = False
    while True:
        if os.path.isfile(coolidor_file): # override temp from command line
            with open(coolidor_file,'r') as f:
                config_data = json.load(f)
                temp_override = float(config_data['temp_override'].strip())
                #hightemp = int(config_data['hightemp'].strip())
                #lowtemp = int(config_data['lowtemp'].strip())
                settemp = float(config_data['settemp'].strip())
                temp_variation = float(config_data['temp_variation'].strip())
                lowtemp = settemp - temp_variation
                hightemp = settemp + temp_variation
                hightemp_max = int(config_data['hightemp_max'].strip())
                sethumi = float(config_data['sethumi'].strip()) #adding for humidity control
                humi_override = float(config_data['humi_override'].strip()) #adding for humidity control
                humi_variation = float(config_data['humi_variation'].strip()) #adding for humidity control
                lowhumi = sethumi - humi_variation #adding for humidity control
                highhumi = sethumi + humi_variation #adding for humidity control
                highhumi_max = int(config_data['highhumi_max'].strip()) #adding for humidity control
                retries = int(config_data['retries'].strip())
                looptime = int(config_data['looptime'].strip())
                rrdfile = str(config_data['rrdfile'].strip())
                no_actuate = config_data['no_actuate']
                #
                #if int(GPIO.input(statuspin)) == 1:
                #    no_actuate = True
                else:
                    no_actuate = False
                #
                if temp_override != 0:
                    humidity = 0
                    valid_temp = True
                    tempF = temp_override
                else:
                    valid_temp = False
            f.closed
        #
        if not valid_temp:
            tempF, humidity, valid_temp = get_temp(retries)
            tempF = tempF + float(config_data['temp_adjust'].strip())
        if valid_temp:
            print(('TemperatureF: {} - Humidity: {}'.format(tempF,humidity)))
            print(('Set Temp: {} - HighF: {} - LowF: {} - HighF Max: {} - OverrideF: {} - Adjust: {} - Output: {}'.format(settemp, hightemp,lowtemp,hightemp_max, temp_override, float(config_data['temp_adjust'].strip()), str(output_mode))))
            output_mode = set_output(hightemp, lowtemp, tempF, no_actuate)
            #
            # update rrdtool
            if output_mode:
                fridgemode = lowtemp
            else:
                fridgemode = hightemp
            ret = rrdtool.update(rrdfile, 'N:%.2f:%.2f:%.2f' %(tempF,fridgemode,humidity));
            #
            time.sleep(looptime)
        else:
            reset_count += 1
            print(('Failed to get a valid temp reading.\nReset Count: {}\n'.format(reset_count)))
            GPIO.output(powerpin, 0) # turn off fridge since we failed to read temp
            reset_sensor(sensor_power)
        #

if __name__ == '__main__':
    try:
        main_run()
    except:
        GPIO.output(powerpin, 0) # set pin low
        GPIO.cleanup()
        traceback.print_exc()
