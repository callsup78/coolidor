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
powerpin = 16  # BOARD pin 16, BCM pin 23 # output power pin
statuspin = 18  # BOARD pin 18, BCM pin 24 # control pin to smartthings enable/disable actuate
GPIO.setup(powerpin, GPIO.OUT)
GPIO.output(powerpin, 0) # set pin low
GPIO.setup(statuspin, GPIO.OUT)
GPIO.output(statuspin, 0) # set pin low

coolidor_file = 'coolidor.json'
hightemp_max = 72 # if we end up above 70, and we are trending up, turn off!!
hightemp = 68 # high temperature allowed, F - above this, turn on
lowtemp = 64 # low temperature allowed, F - below this, turn off
settemp = 66 # settemp is replacing high/low - if settemp were
# 60, then lowtemp should be 60, and hightemp would be +2 /62. This gives an avg temp of 60.
retries = 5 # default retries to get temp sensor data
output_mode = False # set default, false is off, true is on
no_actuate = False # 0 if disabled, 1 if enabled - if enabled, don't alter output state, just simulate.
#
# Parse command line parameters.
#sensor_args = { '11': Adafruit_DHT.DHT11,
#				'22': Adafruit_DHT.DHT22,
#				'2302': Adafruit_DHT.AM2302 }
#if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
#	sensor = sensor_args[sys.argv[1]]
#	pin = sys.argv[2]
#else:
#	print 'usage: sudo ./Adafruit_DHT.py [11|22|2302] GPIOpin#'
#	print 'example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4'
#	sys.exit(1)

sensor = 22
sensor_power = 11 # BOARD pin 11 / gpio pin 17 handles sensor +power
#sensor = 11
pin = 4 # gpio pin 4 for sensor read pin
GPIO.setup(sensor_power, GPIO.OUT)
GPIO.output(sensor_power, 0) # set pin low

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
    tempF = tempC * 9/5.0 + 32
    return tempF, humidity, True # true if reading is valid

# Un-comment the line below to convert the temperature to Fahrenheit.
# temperature = temperature * 9/5.0 + 32

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).  
# If this happens try again!
#if humidity is not None and temperature is not None:
#	print 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
#else:
#	print 'Failed to get reading. Try again!'
#	sys.exit(1)

def set_output(hightemp, lowtemp, current_temp, no_actuate):
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
    #while True:
    #    if os.path.isfile(coolidor_file): # override temp from command line
    #        with open(coolidor_file,'r') as f:
    #            config_data = json.load(f)
    #            temp_override = float(config_data['temp_override'].strip())
    #            #hightemp = int(config_data['hightemp'].strip())
    #            #lowtemp = int(config_data['lowtemp'].strip())
    #            settemp = float(config_data['settemp'].strip())
    #            temp_variation = float(config_data['temp_variation'].strip())
    #            lowtemp = settemp - temp_variation
    #            hightemp = settemp + temp_variation
    #            hightemp_max = int(config_data['hightemp_max'].strip())
    #            retries = int(config_data['retries'].strip())
    #            looptime = int(config_data['looptime'].strip())
    #            rrdfile = str(config_data['rrdfile'].strip())
    #            no_actuate = config_data['no_actuate']
                #
    #            if int(GPIO.input(statuspin)) == 1:
    #                no_actuate = True
    #            else:
    #                no_actuate = False
                #
    #            if temp_override != 0:
    #                humidity = 0
    #                valid_temp = True
    #                tempF = temp_override
    #            else:
    #                valid_temp = False
    #        f.closed
        #
    #    if not valid_temp:
    #        tempF, humidity, valid_temp = get_temp(retries)
    #        tempF = tempF + float(config_data['temp_adjust'].strip())
    #    if valid_temp:
    #        print(('TemperatureF: {} - Humidity: {}'.format(tempF,humidity)))
    #        print(('Set Temp: {} - HighF: {} - LowF: {} - HighF Max: {} - OverrideF: {} - Adjust: {} - Output: {}'.format(settemp, hightemp,lowtemp,hightemp_max, temp_override, float(config_data['temp_adjust'].strip()), str(output_mode))))
    #        output_mode = set_output(hightemp, lowtemp, tempF, no_actuate)
            #
            # update rrdtool
    #        if output_mode:
    #            fridgemode = lowtemp
    #        else:
    #            fridgemode = hightemp
    #        ret = rrdtool.update(rrdfile, 'N:%.2f:%.2f:%.2f' %(tempF,fridgemode,humidity));
            #
    #        time.sleep(looptime)
    #    else:
    #        reset_count += 1
    #        print(('Failed to get a valid temp reading.\nReset Count: {}\n'.format(reset_count)))
    #        GPIO.output(powerpin, 0) # turn off fridge since we failed to read temp
    #        reset_sensor(sensor_power)
        #

if __name__ == '__main__':
    try:
        main_run()
    except:
        GPIO.output(powerpin, 0) # set pin low
        GPIO.cleanup()
        traceback.print_exc()
