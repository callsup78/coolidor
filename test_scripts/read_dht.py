
# i2c read DHT20 module
# get i2c address via running: sudo i2cdetect -y 0
# version 1.0b

import time
import smbus

address = 0x38 #Put your device's address here

i2cbus = smbus.SMBus(1)
time.sleep(0.5)

data = i2cbus.read_i2c_block_data(address,0x71,1)
if (data[0] | 0x08) == 0:
  print('Initialization error')

i2cbus.write_i2c_block_data(address,0xac,[0x33,0x00])
time.sleep(0.1)

data = i2cbus.read_i2c_block_data(address,0x71,7)

temp_raw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
temperature = 200*float(temp_raw)/2**20 - 50

humi_raw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
humidity = 100*float(humi_raw)/2**20

print(temperature)
print(humidity)
