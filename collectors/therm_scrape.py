#!/usr/bin/python
#import requests
import json
import datetime
import time
import urllib
import django.utils.simplejson as jsonUtil
import requests


STAT_BASE_URL = \
    "http://tac.mit.edu/E14_displays/get_controller_data.aspx?floor="
DOPPEL_BASE_URL = "http://localhost:8001/api/"
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

    site_id = "5" # for testing purposes
    listDevices = requests.get(DOPPEL_BASE_URL + "devices/?site_id=" + site_id)
        
    # get the list of devices from doppel2 and store key:value as device_name:device_floor
    unique_devices = {}
    for device in listDevices.json()['data']:
        if not unique_devices.has_key(device["name"]):
            unique_devices[device["name"]] = device["floor"]
        else:
            unique_devices[device["name"]] += device["floor"]

    # scrape data per floor
    for floor in range(1, 7):
        url = STAT_BASE_URL + str(floor)
        data = requests.get(url)
        now = datetime.datetime.now()

        """each datapoint is a json object that looks like
        [
        {
            "name": "E14_Rm100_1",
            "floor": "1",
            "temp": "73.19",
            "setpoint": "70.5062"
        }
        ]
        """

        # loop through each device and check to see if we already have it in doppel2 
        for therm in data.json():
            data = json.dumps(therm)

            # if we don't, POST it
            if unique_devices.has_key(therm["name"]):
                if therm["floor"] in unique_devices[therm["name"]] :
                    print "Device " + therm["name"] + " already in the DB" 
                else:
                    r = requests.post(DOPPEL_BASE_URL + "devices/?site_id=" + site_id, data=data)

            else:
                r = requests.post(DOPPEL_BASE_URL + "devices/?site_id=" + site_id, data=data)
                
            # name = therm["name"] # names look like 'E14_Rm189'
            # temp_sensor = lookup_sensor(s, name, "temperature")
            # setpoint_sensor = lookup_sensor(s, name, "temperature_setpoint")
            # s.add(StaticSample(now, therm["temp"], temp_sensor))
            # s.add(StaticSample(now, therm["setpoint"], setpoint_sensor))