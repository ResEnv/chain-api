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
DOPPEL_SITE_URL = DOPPEL_BASE_URL + "sites/1"

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

    site = requests.get(DOPPEL_SITE_URL)
    listDevicesHref = site.json()['devices']['_href']
    listDevices = requests.get(listDevicesHref).json()['data']
    

    unique_sensors = {} # {'device': 'metric'}
    # get the list of devices from doppel2 and store key:value as device_name:device_floor
    unique_devices = {}
    for device in listDevices:
        # get the list of sensors for each device
        listSensorsHref = device['sensors']['_href']
        listSensors = requests.get(listSensorsHref).json()['data']

        for sensor in listSensors:
            unique_sensor = sensor["metric"]
            if unique_sensors.get(device["name"]) != None:
                if unique_sensor not in unique_sensors.get(device["name"]):
                    unique_sensors[device["name"]] += unique_sensor
            else:
                unique_sensors[device["name"]] = sensor["metric"]

        unique_device = device["floor"] + device["building"] + device["room"]
        if unique_devices.get(device["name"]) != None:
            if unique_device not in unique_devices.get(device["name"]):
                unique_devices[device["name"]] += unique_device
        else:
            unique_devices[device["name"]] = unique_device

    # scrape data per floor
    for floor in range(1, 7):
        url = STAT_BASE_URL + str(floor)
        floorData = requests.get(url)
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
        for therm in floorData.json():

            # parse the "name" field so that we can extract the building and room number
            name = therm["name"]
            dataParsed = name.split("_")

            building = dataParsed[0]
            room = dataParsed[1]

            # add it to the dictionary
            therm["building"] = building
            therm["room"] = room

            device_data = {"building": building, "floor": floor, "room" : room, "name" : name}

            doDevicePost = False
            printDBStatement = True
            # if we don't have the device in doppel2, POST it
            if unique_devices.get(name) != None:
                therm_device = device["floor"] + device["building"] + device["room"]
                if therm_device in unique_devices[therm["name"]] :
                    printDBStatement = False 
                else:
                    doDevicePost = True

            if unique_devices.get(name) == None or doDevicePost:
                r = requests.post(listDevicesHref, data=json.dumps(device_data))
                
            # sensor parsing
            tempSensors = {}

            sensor_temp_value = therm["temp"]
            sensor_setpoint_value = therm["setpoint"]

            sensor_metric_temp = "temp"
            sensor_metric_setpoint = "setpoint"

            tempSensors["temp"] = {"metric" : sensor_metric_temp, "value" : sensor_temp_value, "timestamp" : str(now)}
            tempSensors["setpoint"] = {"metric" : sensor_metric_setpoint, "value" : sensor_setpoint_value, "timestamp" : str(now)}

            for sensor in tempSensors.keys():
                if unique_sensors.get(name) == None:
                    requests.post(listSensorsHref, data=json.dumps(tempSensors[sensor]))
                
                elif tempSensors[sensor]["metric"] not in unique_sensors.get(name):
                    requests.post(listSensorsHref, data=json.dumps(tempSensors[sensor]))

        if printDBStatement:
            print "All devices already on doppel DB on floor " + str(floor)        
