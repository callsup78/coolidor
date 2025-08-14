import sys, os.path, traceback, json
import time, rrdtool
import Adafruit_DHT
import RPi.GPIO as GPIO

sensor = 22
sensor_power = 17 # BOARD pin 11 / gpio pin 17 handles sensor +power
pin = 4 # gpio pin 4 for sensor read pin
coolidor_file = 'coolidor.json'
temp_pin = 23  # Raspi Z2W pin 16 GPIO # 23 - Power output pin to relay for Temp
humidity_pin = 24 # Raspi Z2W pin 18 GPIO # 24 - Power output pin to relay for Humidity
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

GPIO.setmode(GPIO.BCM)
GPIO.setup(temp_pin, GPIO.OUT)
GPIO.output(temp_pin, GPIO.LOW) # set pin low
GPIO.setup(humidity_pin, GPIO.OUT)
GPIO.output(humidity_pin, GPIO.LOW) # set pin low
GPIO.setup(sensor_power, GPIO.OUT)
GPIO.output(sensor_power, GPIO.LOW) # set pin low

def reset_sensor(sensor_power, offtime=10):
    print ('Resetting sensor power pin...')
    GPIO.output(sensor_power, GPIO.LOW) # set pin low
    time.sleep(offtime)
    GPIO.output(sensor_power, 1) # set pin high
    time.sleep(2)
    print ('Temp sensor reset complete.')

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
    if tempC is None or humidity is None:
        return 0, 0, False
    current_temp = tempC * 9/5.0 + 32
   # humidity = current_humi
    return current_temp, humidity, True # true if reading is valid

def set_output(hightemp, lowtemp, current_temp, highhumi, lowhumi, humidity, no_actuate):
    output = False
    if current_temp > hightemp or humidity > highhumi:
        if not no_actuate:
            GPIO.output(temp_pin, GPIO.HIGH)
        output = True
    elif current_temp < lowtemp or humidity < lowhumi:
        if not no_actuate:
            GPIO.output(temp_pin, GPIO.LOW)
        output = False
    else:
        output = bool(GPIO.input(temp_pin))
    print(f"Set output: {output} - No_Actuate: {no_actuate}")
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
                no_actuate = bool(config_data.get('no_actuate', False))
                
                # else:
                #     no_actuate = False
                if temp_override != 0:
                    humidity = 0
                    valid_temp = True
                    current_temp = temp_override
                else:
                    valid_temp = False
           # f.closed
        if not valid_temp:
            current_temp, humidity, valid_temp = get_temp(retries)
            current_temp = current_temp + float(config_data['temp_adjust'].strip())
        if valid_temp:
            print(('TemperatureF: {} - Humidity: {}'.format(current_temp,humidity)))
            print(('Set Temp: {} - HighF: {} - LowF: {} - HighF Max: {} - OverrideF: {} - Adjust: {} - Output: {}'.format(settemp, hightemp,lowtemp,hightemp_max, temp_override, float(config_data['temp_adjust'].strip()), str(output_mode))))
            # print(('Set Humidity: {} - High Humidity: {} - Low Humidity: {} - High Humidity Max: {} - Override Humidity: {} - Adjust: {} - Output: {}'.format(sethumi, highhumi,lowhumi,highhumi_max, humi_override, float(config_data['humi_adjust'].strip()), str(output_mode)))) 
            output_mode = set_output(hightemp, lowtemp, current_temp, highhumi, lowhumi, humidity, no_actuate)
            if output_mode:
                fridgemode = lowtemp
            else:
                fridgemode = hightemp
            try:
                ret = rrdtool.update(rrdfile, f'N:{current_temp:.2f}:{fridgemode:.2f}:{humidity:.2f}')
            except rrdtool.OperationalError as e:
                print(f"RRD update failed: {e}")            
            time.sleep(looptime)
        else:
            reset_count += 1
            print(('Failed to get a valid temp reading.\nReset Count: {}\n'.format(reset_count)))
            GPIO.output(temp_pin, GPIO.LOW) # turn off fridge since we failed to read temp
            reset_sensor(sensor_power)

if __name__ == '__main__':
    config_data = {}
    valid_temp = False
    temp_override = 0
    humi_override = 0
    looptime = 60
    rrdfile = "/default/path.rrd"
    try:
        main_run()
    except:
        GPIO.output(temp_pin, GPIO.LOW) # set pin low
        GPIO.cleanup()
        traceback.print_exc()

