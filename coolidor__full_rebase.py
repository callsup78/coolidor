import time
import json
import sys
import board
import digitalio
import adafruit_dht

# logging
class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass

class ErrorLogger(object):
    def __init__(self, filename):
        self.terminal = sys.stderr
        self.log = open(filename, "a")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass

# Redirect logging outputs
sys.stdout = Logger("coolidor.log")     # normal log data
sys.stderr = ErrorLogger("coolidor.err")  # error log data

# --- Pin assignments ---
sensor_pin = board.D4       # GPIO4 equivalent
sensor_power_pin = board.D17
temp_pin = board.D23
humidity_pin = board.D24

coolidor_file = "coolidor.json"

# --- Defaults ---
settemp = 66
lowtemp = 64
hightemp = 68
hightemp_max = 72
sethumi = 68
lowhumi = 64
highhumi = 70
highhumi_max = 72
retries = 5
looptime = 60
no_actuate = False

# --- Outputs ---
temp_out = digitalio.DigitalInOut(temp_pin)
temp_out.direction = digitalio.Direction.OUTPUT
temp_out.value = False

humi_out = digitalio.DigitalInOut(humidity_pin)
humi_out.direction = digitalio.Direction.OUTPUT
humi_out.value = False

sensor_power = digitalio.DigitalInOut(sensor_power_pin)
sensor_power.direction = digitalio.Direction.OUTPUT
sensor_power.value = False

# DHT22 (sensor=22)
dht_device = adafruit_dht.DHT22(sensor_pin)

# Reset Sensor function
def reset_sensor(offtime=10):
    print("Resetting sensor...")
    sensor_power.value = False
    time.sleep(offtime)
    sensor_power.value = True
    time.sleep(offtime)
    print("Sensor reset complete.")

# get_temp function
def get_temp(retries=5):
    for attempt in range(retries):
        try:
            tempC = dht_device.temperature
            humidity = dht_device.humidity
            if tempC is not None and humidity is not None and humidity <= 100:
                current_temp = tempC * 9 / 5.0 + 32
                return current_temp, humidity, True
        except RuntimeError as e:
            print(f"Retry {attempt+1}/{retries} failed: {e}")
        time.sleep(2)
    return 0, 0, False

#set output function
def set_output(hightemp, lowtemp, current_temp,
               highhumi, lowhumi, humidity,
               no_actuate):
    temp_output = False
    humi_output = False

    # Temperature
    if current_temp > hightemp:
        if not no_actuate:
            temp_out.value = True
        temp_output = True
    elif current_temp < lowtemp:
        if not no_actuate:
            temp_out.value = False
        temp_output = False
    else:
        temp_output = temp_out.value

    # Humidity
    if humidity > highhumi:
        if not no_actuate:
            humi_out.value = True
        humi_output = True
    elif humidity < lowhumi:
        if not no_actuate:
            humi_out.value = False
        humi_output = False
    else:
        humi_output = humi_out.value

    print(f"[OUTPUT] Temp: {temp_output}, Humidity: {humi_output}, No_Actuate={no_actuate}")
    return temp_output, humi_output


def main_run():
    reset_sensor()
    reset_count = 0

    while True:
        # Load config if present
        try:
            with open(coolidor_file, "r") as f:
                config = json.load(f)

            temp_override = float(config.get("temp_override", 0))
            settemp = float(config.get("settemp", 66))
            temp_variation = float(config.get("temp_variation", 2))
            lowtemp = settemp - temp_variation
            hightemp = settemp + temp_variation
            hightemp_max = int(config.get("hightemp_max", 72))

            sethumi = float(config.get("sethumi", 68))
            humi_override = float(config.get("humi_override", 0))
            humi_variation = float(config.get("humi_variation", 2))
            lowhumi = sethumi - humi_variation
            highhumi = sethumi + humi_variation
            highhumi_max = int(config.get("highhumi_max", 72))

            retries = int(config.get("retries", 5))
            looptime = int(config.get("looptime", 60))
            no_actuate = str(config.get("no_actuate", "0")).lower() in ["1", "true", "yes"]

        except Exception as e:
            print("Config not found, using defaults.", e)
            temp_override = 0
            humi_override = 0

        if temp_override != 0 or humi_override != 0:
            current_temp = temp_override if temp_override != 0 else 0
            humidity = humi_override if humi_override != 0 else 0
            valid_temp = True
        else:
            current_temp, humidity, valid_temp = get_temp(retries)

        if valid_temp:
            print(f"TempF: {current_temp:.1f}  Humidity: {humidity:.1f}")
            temp_output, humi_output = set_output(hightemp, lowtemp, current_temp,
                                                  highhumi, lowhumi, humidity,
                                                  no_actuate)
        else:
            reset_count += 1
            print(f"Failed to read sensor. Reset Count={reset_count}")
            temp_out.value = False
            humi_out.value = False
            reset_sensor()

        time.sleep(looptime)


# --- Main ---
try:
    main_run()
except Exception as e:
    print("Fatal error:", e)
    temp_out.value = False
    humi_out.value = False
