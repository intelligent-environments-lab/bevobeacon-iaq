# Sensor modules
from board import SCL, SDA
from busio import I2C
import dgs
import pigpio
import adafruit_sgp30 as sgp30
import adafruit_tsl2591 as tsl2591

import time

def checkAdafruit(sensor_name="sgp30"):
	"""
	Checks connection to Adafruit sensors
	"""
	# creating i2c bus
	i2c = I2C(SCL, SDA)

	if sensor_name == "sgp30":
		sgp = sgp30.Adafruit_SGP30(i2c)
		print("Connected to device at")
	elif sensor_name == "tsl2591":
		tsl = tsl2591.TSL2591(i2c)
		print("Connected to device at")
	else:
		print(f"Sensor {sensor_name} does not exist.")

	print(i2c.scan())

def checkDGS(dev_no=0):
	"""
	Checks connection to DGS sensors
	"""
	c, _, _ = dgs.takeMeasurement(f"/dev/ttyUSB{dev}")
	if c != -100:
		print("\tDATA READ")

def checkSensirion(address=0x61, bus=1, n=3):
	"""
	Checks connection to Sensirion sensors

	Inputs:
	- address: address of the sensor
	- bus: i2c bus address
	- n: number of bytes to read


	"""
	PIGPIO_HOST = '127.0.0.1'
	pi = pigpio.pi(PIGPIO_HOST)

	h = pi.i2c_open(bus, address)
	print("Connected to device at", address)
	count, data = pi.i2c_read_device(h, n)
	print("Data read")

def main():

	# getting the adafruit sensors
	for sensor in ["sgp30","tsl2591"]:
		time.sleep(0.5)
		checkAdafruit(sensor)

	# getting DGS sensors
	for dev in [0,1]:
		time.sleep(0.5)
		checkDGS(dev)

	# getting sensirion sensors
	for address in [0x61,0x69]:
		time.sleep(0.5)
		checkSensirion(address=address)

if __name__ == '__main__':
    main()
