import time
import datetime
import asyncio
import os
import logging
import sys

import pandas as pd
from adafruit import SGP30, TSL2591
from sensirion import SPS30, SCD30
from spec_dgs import DGS_NO2, DGS_CO
import management as mgmt


async def main(beacon="00"):
    sensor_classes = {
        "sgp": SGP30,
        "tsl": TSL2591,
        "sps": SPS30,
        "scd": SCD30,
        "dgs_co": DGS_CO,
        "dgs_no2": DGS_NO2,
    }

    sensors = {}

    for name, sens in sensor_classes.items():
        try:
            sensor = sens()
            sensors.update({name: sensor})
        except:
            pass

    manually_enabled_sensors = list(set(sensors) & set(["tsl", "sps", "scd"]))
    time.sleep(1)
    log.info(f"Successfully created: {sensors}")
    log.info("Attempting scans")

    starttime = time.time()  # Used for preventing time drift
    loop = True
    while loop:
        start_time = time.time()  # Used for measuring measurement cycle time

        # Turn on all sensors before starting scans
        for manual_sensor in manually_enabled_sensors:
            try:
                sensors[manual_sensor].enable()
            except:
                pass

        # Wait for sensors to come online
        time.sleep(0.1)

        data = {}

        async def scan(name):
            df = pd.DataFrame(
                [
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                ]
            )
            log.info("\nScan results for " + name)
            log.info(df)
            data[name] = df.median()
            log.info(data[name])

        # Perform all scans
        await asyncio.gather(*[scan(name) for name in sensors])

        # Disable sensors until next measurement interval
        for manual_sensor in manually_enabled_sensors:
            try:
                sensors[manual_sensor].disable()
            except:
                pass

        # Write data to csv file
        date = datetime.datetime.now()
        timestamp = pd.Series({"Timestamp": date.strftime("%Y-%m-%d %H:%M:%S")})
        df = pd.concat([timestamp, *data.values()]).to_frame().T.set_index("Timestamp")
        df = df.rename(
            columns={
                "TC": "Temperature [C]",
                "RH": "Relative Humidity",
                "pm_n_0p5": "PM_N_0p5",
                "pm_n_1": "PM_N_1",
                "pm_n_2p5": "PM_N_2p5",
                "pm_n_4": "PM_N_4",
                "pm_n_10": "PM_N_10",
                "pm_c_1": "PM_C_1",
                "pm_c_2p5": "PM_C_2p5",
                "pm_c_4": "PM_C_4",
                "pm_c_10": "PM_C_10",
            }
        )
        filename = f'/home/pi/DATA/b{beacon}_{date.strftime("%Y-%m-%d")}.csv'

        log.info(df)
        try:
            if os.path.isfile(filename):
                df.to_csv(filename, mode="a", header=False)
                log.info(f"Data appended to {filename}")
            else:
                df.to_csv(filename)
                log.info(f"Data written to {filename}")
        except:
            pass

        # mgmt.data_mgmt(data)
        elapsed_time = time.time() - start_time
        log.info(f"{elapsed_time} \n\n")
        time.sleep(5)
        # time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        # loop = False


def setup_logger(level=logging.WARNING):
    
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.propagate = False
    if (log.hasHandlers()):
        log.handlers.clear()
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(message)s")
    sh.setFormatter(formatter)
    log.addHandler(sh)
    return log


if __name__ == "__main__":
    log = setup_logger(logging.INFO)
    asyncio.run(main(beacon="test"))
