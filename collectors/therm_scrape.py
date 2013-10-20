#!/usr/bin/python
#import requests
import json
import datetime
import time
import urllib


STAT_BASE_URL = \
    "http://tac.mit.edu/E14_displays/get_controller_data.aspx?floor="
DOPPEL_BASE_URL = "http://localhost:8000/api/"
DOPPEL_SITE_URL = DOPPEL_BASE_URL + "sites/3/"


# Strategy:
# get a list of devices/sensors from doppel2
# get a list of readings from tac.mit.edu
# store the timestamp
# for reading in readings:
#   if the device from the reading isn't in doppel2:
#       build the JSON for the device (including sensors) and post it
#   if the device doesn't have the right sensors:
#       create the sensors on the device (post)
#   add the timestamped sensor data to the sensor

if __name__ == "__main__":
    while True:
        for floor in range(1, 7):
            url = STAT_BASE_URL + str(floor)
            data = json.load(urllib.urlopen(url))
            now = datetime.datetime.now()
            """each datapoint is a json object that looks like
            {
            "name": "E14_Rm189",
            "floor": "1",
            "temp": "68.02",
            "setpoint": "68"
            }"""
            for therm in data:
                pass
#                name = therm["name"] # names look like 'E14_Rm189'
#                temp_sensor = lookup_sensor(s, name, "temperature")
#                setpoint_sensor = lookup_sensor(s, name,
#                                                "temperature_setpoint")
#                s.add(StaticSample(now, therm["temp"], temp_sensor))
#                s.add(StaticSample(now, therm["setpoint"],
#                                   setpoint_sensor))
        time.sleep(30)
