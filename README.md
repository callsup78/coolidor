## Project to replace the failing control board of a Whynter CHC-421HC cigar humidifier, utilizing a Raspberry Pi Zero 2 W, a pre-built relay contol box, and an AdaFruit DHT22 sensor.
  
  


### Sources:

### Hardware:  

<a href="https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/">Raspberry Pi Zero 2 W</a>  
<a href="https://www.adafruit.com/product/5183">AdaFruit DHT-22 Sensor</a>  
<a href="https://www.amazon.com/dp/B08BNJMNXT"> Low cost 10a Relay</a>  
<a href="https://www.amazon.com/dp/B019GUOV40"> Mean Well 5v 35w Power Supply</a>


### Software:
Sources pulled from mutple projects relating to Pi OS, an Adafruit DHT-22 Sensor and the following  
Python packages: time, json, sys, board, digitalio, adafruit_dht.   


### Install:
Note: * I utilzied a Standard Raspberry Pi image (Bookworm) and the pi-imager software for this as my starting point.

sudo apt-get update  
sudo apt-get upgrade  
sudo apt-get install git  
sudo apt-get install gcc-aarch64-linux-gnu build-essential python3-dev libssl-dev libffi-dev  
python3 -m venv --system-site-packages myenv  
source myenv/bin/activate  
run script - wait for errors. There will likely be errors. muahahahaha  
