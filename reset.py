import RPi.GPIO as GPIO         # Import Raspberry Pi GPIO library
from time import sleep          # Import the sleep function

temp_pin = 23                      # Relay GPIO Pin
humidity_pin = 24

GPIO.setmode(GPIO.BCM)          # Use GPIO pin number
GPIO.setwarnings(False)         # Ignore warnings in our case
GPIO.setup(temp_pin, GPIO.OUT)    # GPIO pin as output pin
GPIO.setup(humidity_pin, GPIO.OUT)

while True:
    GPIO.output(temp_pin, GPIO.LOW)
    GPIO.output(humidity_pin, GPIO.LOW)
    print("Forcing Cooling Off, Forcing Humidity Off")
    sleep(2)
    break