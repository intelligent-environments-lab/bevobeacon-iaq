#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2018 UnravelTEC
# Michael Maier <michael.maier+github@unraveltec.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# If you want to relicense this code under another license, please contact info+github@unraveltec.com.

# hints from https://www.raspberrypi.org/forums/viewtopic.php?p=600515#p600515

from __future__ import print_function

# This module uses the services of the C pigpio library. pigpio must be running on the Pi(s) whose GPIO are to be manipulated. 
# cmd ref: http://abyz.me.uk/rpi/pigpio/python.html#i2c_write_byte_data
import pigpio # aptitude install python-pigpio
import time
from datetime import datetime
import csv
import struct
import sys
import crcmod # aptitude install python-crcmod

def takeMeasurement(pi_in,h_in):
	'''
	Gets some values
	'''

	global f_crc8
	global pi
	global h

	pi = pi_in
	h = h_in

	co2 = 0.0
	t = 0.0
	rh = 0.0

	def eprint(*args, **kwargs):
		print(*args, file=sys.stderr, **kwargs)

	def read_n_bytes(n):

	  try:
		(count, data) = pi.i2c_read_device(h, n)
	  except:
	    	eprint("error: i2c_read failed")
	    	exit(1)

	  if count == n:
	    	return data
	  else:
	    	eprint("error: read measurement interval didnt return " + str(n) + "B")
	    	return False

	def i2cWrite(data):
	  try:
	    	pi.i2c_write_device(h, data)
	  except:
		eprint("error: i2c_write failed")
		return -1
	  return True


	def read_meas_interval():
		ret = i2cWrite([0x46, 0x00])
		if ret == -1:
			return -1

		try:
			(count, data) = pi.i2c_read_device(h, 3)
		except:
			eprint("error: i2c_read failed")
			exit(1)

		if count == 3:
			if len(data) == 3:
				interval = int(data[0])*256 + int(data[1])
				#print "measurement interval: " + str(interval) + "s, checksum " + str(data[2])
				return interval
			else:
				eprint("error: no array len 3 returned, instead " + str(len(data)) + "type: " + str(type(data)))
		else:
			"error: read measurement interval didnt return 3B"
	  
		return -1

	read_meas_result = read_meas_interval()
	if read_meas_result == -1:
		exit(1)

	if read_meas_result != 2:
	# if not every 2s, set it
		eprint("setting interval to 2")
		ret = i2cWrite([0x46, 0x00, 0x00, 0x02, 0xE3])
	  	if ret == -1:
	    		exit(1)
	  	read_meas_interval()


	#trigger cont meas
	# TODO read out current pressure value
	pressure_mbar = 972
	LSB = 0xFF & pressure_mbar
	MSB = 0xFF & (pressure_mbar >> 8)
	#print ("MSB: " + hex(MSB) + " LSB: " + hex(LSB))
	#pressure_re = LSB + (MSB * 256)
	#print("press " + str(pressure_re))
	pressure = [MSB, LSB]

	pressure_array = ''.join(chr(x) for x in [pressure[0], pressure[1]])
	#pressure_array = ''.join(chr(x) for x in [0xBE, 0xEF]) # use for testing crc, should be 0x92
	#print pressure_array

	f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)

	crc8 = f_crc8(pressure_array) # for pressure 0, should be 0x81
	# print "CRC: " + hex(crc8)
	i2cWrite([0x00, 0x10, pressure[0], pressure[1], crc8])

	count = 1
	for i in range(5):

		for j in range(10):
			#print('Looking for data - attempt:',j+1)
			ret = i2cWrite([0x02, 0x02])
			if ret == -1:
				exit(1)

			data = read_n_bytes(3)
			if data == False:
				time.sleep(0.1)
				continue

			if data[1] == 1:
				break
			else:
				time.sleep(0.2)

		#read measurement
		i2cWrite([0x03, 0x00])
		data = read_n_bytes(18)

		if data == False:
			exit(1)

		struct_co2 = struct.pack('>BBBB', data[0], data[1], data[3], data[4])
		temp_co2 = struct.unpack('>f', struct_co2)

		struct_T = struct.pack('>BBBB', data[6], data[7], data[9], data[10])
		temp_t = struct.unpack('>f', struct_T)

		struct_rH = struct.pack('>BBBB', data[12], data[13], data[15], data[16])
		temp_rh = struct.unpack('>f', struct_rH)
		
		if temp_co2[0] > 0:
			co2 += temp_co2[0]
			t += temp_t[0]
			rh += temp_rh[0]
			count += 1

			print("Concentration (ppm)")
			print("---------------------------------------")
			print("CO2: {0:.1f}".format(co2/(i+1)))
			print("Environmental Variables")
			print("---------------------------------------")
			print("T (C): {0:.1f}".format(t/(i+1)))
			print("RH (%): {0:.1f}".format(rh/(i+1)))
			print("---------------------------------------")

		#print("gas_ppm{sensor=\"SCD30\",gas=\"CO2\"} %f" % co2/(i+1))
		#print("temperature_degC{sensor=\"SCD30\"} %f" % t/(i+1))
		#print("humidity_rel_percent{sensor=\"SCD30\"} %f" % rh/(i+1))
		time.sleep(1)

	return t/count, rh/count, co2/count