import asyncio
import time
import numpy as np

# Raspberry PI board libraries
from board import SCL, SDA
from busio import I2C

# Sensor libraries
import adafruit_sgp30
import adafruit_tsl2591


class SGP30:
    """ Located within SVM30"""

    def __init__(self) -> None:
        i2c = I2C(SCL, SDA)
        try:
            sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
            sgp30.iaq_init()
        except Exception:
            raise Exception("SGP30 sensor not found")
        self.sgp30 = sgp30

    async def scan(self):
        # print('spg scan start')
        try:
            # Retrieve sensor scan data
            eCO2, TVOC = self.sgp30.iaq_measure()
        except:
            print("Error reading from SGP30")
            eCO2 = np.nan
            TVOC = np.nan
        # print('spg scan end')
        # Return data
        data = {"TVOC": TVOC, "eCO2": eCO2}
        return data


class TSL2591:
    def __init__(self) -> None:
        i2c = I2C(SCL, SDA)
        try:
            tsl = adafruit_tsl2591.TSL2591(i2c)
        except Exception as inst:
            raise Exception("TSL2591 sensor not found")
        # set gain and integration time; gain 0 = 1x & 1 = 16x. Integration time of 1 = 101ms
        tsl.gain = 0
        tsl.integration_time = 1  # 101 ms intergration time.
        self.tsl = tsl

    async def scan(self):
        # print('tsl scan start')
        try:
            tsl = self.tsl
            # enable sensor and wait a sec for it to get going
            tsl.enabled = True
            await asyncio.sleep(1)

            # Retrieve sensor scan data
            lux = tsl.lux
            visible = tsl.visible
            infrared = tsl.infrared
            # Check for complete darkness
            if lux == None:
                lux = 0
            # Disable the sensor and end process
            tsl.enabled = False
            await asyncio.sleep(0.1)
        except:
            lux = np.nan
            visible = np.nan
            infrared = np.nan
        # Return data
        # print('tsl scan end')
        data = {"Visible": visible, "Infrared": infrared, "Lux": lux}
        return data