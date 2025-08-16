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
    time.sleep(offtime)
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
    return current_temp, humidity, True # true if reading is valid

def set_output(hightemp, lowtemp, current_temp,
               highhumi, lowhumi, humidity,
               no_actuate):
    temp_output = False
    humi_output = False

    # --- Temperature control ---
    if current_temp > hightemp:
        if not no_actuate:
            GPIO.output(temp_pin, GPIO.HIGH)  # turn ON fridge/cooler
        temp_output = True
    elif current_temp < lowtemp:
        if not no_actuate:
            GPIO.output(temp_pin, GPIO.LOW)   # turn OFF fridge/cooler
        temp_output = False
    else:
        temp_output = bool(GPIO.input(temp_pin))

    # --- Humidity control ---
    if humidity > highhumi:
        if not no_actuate:
            GPIO.output(humidity_pin, GPIO.HIGH)  # turn ON humidifier
        humi_output = True
    elif humidity < lowhumi:
        if not no_actuate:
            GPIO.output(humidity_pin, GPIO.LOW)   # turn OFF humidifier
        humi_output = False
    else:
        humi_output = bool(GPIO.input(humidity_pin))

    print(f"[OUTPUT] Temp: {temp_output}, Humidity: {humi_output}, No_Actuate={no_actuate}")
    return temp_output, humi_output

def main_run():
    reset_sensor(sensor_power)
    reset_count = 0
    valid_temp = False
    temp_override = 0
    humi_override = 0
    looptime = 60
    rrdfile = "/default/path.rrd"

    while True:
        if os.path.isfile(coolidor_file):
            with open(coolidor_file, 'r') as f:
                config_data = json.load(f)

            temp_override = float(config_data.get('temp_override', 0))
            settemp = float(config_data.get('settemp', 66))
            temp_variation = float(config_data.get('temp_variation', 2))
            lowtemp = settemp - temp_variation
            hightemp = settemp + temp_variation
            hightemp_max = int(config_data.get('hightemp_max', 72))

            sethumi = float(config_data.get('sethumi', 68))
            humi_override = float(config_data.get('humi_override', 0))
            humi_variation = float(config_data.get('humi_variation', 2))
            lowhumi = sethumi - humi_variation
            highhumi = sethumi + humi_variation
            highhumi_max = int(config_data.get('highhumi_max', 72))

            retries = int(config_data.get('retries', 5))
            looptime = int(config_data.get('looptime', 60))
            rrdfile = str(config_data.get('rrdfile', "/default/path.rrd"))
            no_actuate = str(config_data.get('no_actuate', "0")).lower() in ["1", "true", "yes"]

            if temp_override != 0 or humi_override != 0:
                current_temp = temp_override if temp_override != 0 else 0
                humidity = humi_override if humi_override != 0 else 0
                valid_temp = True
            else:
                valid_temp = False
        else:
            # defaults if config file missing or read failure
            settemp = 66
            lowtemp = 64
            hightemp = 68
            hightemp_max = 72
            sethumi = 68
            lowhumi = 64
            highhumi = 70
            highhumi_max = 72
            retries = 5

        if not valid_temp:
            current_temp, humidity, valid_temp = get_temp(retries)

        if valid_temp:
            print(f"TemperatureF: {current_temp} - Humidity: {humidity}")
            print(f"Set Temp: {settemp} - HighF: {hightemp} - LowF: {lowtemp} "
                  f"- HighF Max: {hightemp_max} - OverrideF: {temp_override} - Output: {output_mode}")

            temp_output, humi_output = set_output(hightemp, lowtemp, current_temp,
                                      highhumi, lowhumi, humidity, no_actuate)

            fridgemode = lowtemp if temp_output else hightemp
            humidmode = lowhumi if humi_output else highhumi
            
            try:
                rrdtool.update(rrdfile, f'N:{current_temp:.2f}:{fridgemode:.2f}:{humidity:.2f}:{humidmode:.2f}')
            except rrdtool.OperationalError as e:
                print(f"RRD update failed: {e}")

            time.sleep(looptime)
        else:
            reset_count += 1
            print(f"Failed to get valid temp reading. Reset Count: {reset_count}")
            GPIO.output(temp_pin, GPIO.LOW)
            GPIO.output(humidity_pin, GPIO.LOW)
            reset_sensor(sensor_power)

if __name__ == '__main__':
    try:
        main_run()
    except Exception:
        GPIO.output(temp_pin, GPIO.LOW)
        GPIO.output(humidity_pin, GPIO.LOW)
        traceback.print_exc()
    finally:
        GPIO.cleanup()


