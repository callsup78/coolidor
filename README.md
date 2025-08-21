
Project to replace the failing control board of a Whynter CHC-421HC cigar humidifier,
utilizing a Raspberry Pi Zero 2 W, a 2 relay contol board, and an i2c AdaFruit DHT20 sensor.




Sources:

Hardware:
Raspberry Pi Zero 2 W: https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/
AdaFruit DHT-20 Sensor: https://www.adafruit.com/product/5183

Software:
Sources pulled from mutple projects relating to Pi OS, DHT-20 Sensor, i2cdetect. 
Most Code proudly stolen rinsed and reused from wizards like Tony DiCola & David Smith.

Install:
* I utilzied a Standard Raspberry Pi image (Bookworm) for this.

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git
sudo apt-get install gcc-aarch64-linux-gnu build-essential python3-dev libssl-dev libffi-dev
sudo apt-get install rrdtool librrd-dev
python3 -m venv --system-site-packages myenv
source myenv/bin/activate
pip3 install rrdtool
pip3 install Adafruit_DHT --config-settings="--build-option=--force-pi"
run script - wait for errors. There will likely be errors. muahahahaha
