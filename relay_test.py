import RPi.GPIO as GPIO         # Import Raspberry Pi GPIO library
from time import sleep          # Import the sleep function

temp_pin = 23                      # Relay GPIO Pin
humidity_pin = 24

GPIO.setmode(GPIO.BCM)          # Use GPIO pin number
GPIO.setwarnings(False)         # Ignore warnings in our case
GPIO.setup(temp_pin, GPIO.OUT)    # GPIO pin as output pin
GPIO.setup(humidity_pin, GPIO.OUT)

while True:                          # Endless Loop
    GPIO.output(temp_pin, GPIO.HIGH)   # Turn on
    GPIO.output(humidity_pin, GPIO.LOW)
    print("Cooling On, Humidity Off")                    # Prints state to console
    sleep(2)                         # Pause 1 second
    GPIO.output(temp_pin, GPIO.LOW)    # Turn off
    GPIO.output(humidity_pin, GPIO.HIGH)
    print("Cooling Off, Humidity On")                   # Prints state to console
    sleep(2)                         # Pause 1 second