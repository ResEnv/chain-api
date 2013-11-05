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
DOPPEL_BASE_URL = "http://localhost:8000/api/"
DOPPEL_SITE_URL = DOPPEL_BASE_URL + "sites/1/"

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

    site_id = "1" # for testing purposes
    listDevices = requests.get(DOPPEL_BASE_URL + "devices/?site_id=" + site_id)

    unique_sensors = {} # {'device': 'metric'}
    # get the list of devices from doppel2 and store key:value as device_name:device_floor
    unique_devices = {}
    for device in listDevices.json()['data']:
        # get the list of sensors for each device
        device_id = device["_href"].split("/devices/")[1]
        listSensors = requests.get(DOPPEL_BASE_URL + "sensors/?device_id=" + device_id)

        for sensor in listSensors.json()['data']:
            if not unique_sensors.has_key(device["name"]):
                unique_sensors[device["name"]] = sensor["metric"]
            else:
                unique_sensors[device["name"]] += sensor["metric"]

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
            doPost = False

            # if we don't, POST it
            if unique_devices.has_key(therm["name"]):
                if therm["floor"] in unique_devices[therm["name"]] :
                    print "Device " + therm["name"] + " already in the doppel2 database" 
                else:
                    doPost = True

            if not unique_devices.has_key(therm["name"]) or doPost:
                r = requests.post(DOPPEL_BASE_URL + "devices/?site_id=" + site_id, data=data)
                
            name = therm["name"] # names look like 'E14_Rm189'
            floor = therm["floor"] # floor is an int

            temp_sensor = therm["temp"]
            setpoint_sensor = therm["setpoint"]
            sensor_data = json.dumps({"temp": temp_sensor, "setpoint": setpoint_sensor, "metric": "temperature", "unit":"celcius", "metric_id":"1"})
            
            devices = listDevices.json()['data']
            for device in devices:
                if device["name"] == therm["name"]:
                    device_id = device["_href"].split("/devices/")[1]

            if True:
                requests.post(DOPPEL_BASE_URL + "sensors/?device_id=" + device_id, data=sensor_data)