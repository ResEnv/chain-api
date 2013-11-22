#!/usr/bin/python
# -*- coding: utf-8 -*-

# import requests

import json
import datetime
import time
import urllib
import django.utils.simplejson as jsonUtil
import requests

url = \
    'http://doppler.media.mit.edu:1202'
DOPPEL_BASE_URL = 'http://localhost:8000/api/'
DOPPEL_SITE_URL = DOPPEL_BASE_URL + 'sites/3'

# Strategy:
# get a list of devices/sensors from doppel2
# get a list of readings from tidmarsh
# store the timestamp
# for reading in readings:
#   if the device from the reading isn't in doppel2:
#       build the JSON for the device (including sensors) and post it
#   if the device doesn't have the right sensors:
#       create the sensors on the device (post)
#   add the timestamped sensor data to the sensor

if __name__ == '__main__':

    site = requests.get(DOPPEL_SITE_URL)

    # set the _href for the site to post devices to. then set the list of devices from the site request
    # use a link if no embedded resource is provided.
    listDevicesHref = site.json()['devices']['_href']
    if (site.json()['devices']).get('data') != None:
        listDevices = site.json()['devices']['data']
    else:
        listDevices = requests.get(listDevicesHref).json()['data']

    # get the list of devices from doppel2 and store key:value as device_unique_properties:device_href
    unique_devices = {} # (name, building, floor, room): _href
    unique_sensors = {} # ('device', 'metric'): _href

    for device in listDevices:
        # get the list of sensors for each device and the _href to post. 
        # use a link if no embedded resource is provided.
        listSensorsHref = device['sensors']['_href']
        if (device['sensors']).get('data') != None:
            listSensors = device['sensors']['data']
        else:
            listSensors = requests.get(listSensorsHref).json()['data']

        # create the a unique device from each device in the server and store it along with 
        # the corresponding _href for sensor posting
        unique_devices[device['name']] = listSensorsHref

        # loop through the sensors in this device and add them to the unique_sensor dictionary
        for sensor in listSensors:
            unique_sensors[(device['name'], sensor['metric'])] = sensor['history']['_href']

    data = requests.get(url)
    now = datetime.datetime.now()

    # create units dict
    unitsDict = {
        "sht_humidity" : "percent",
        "bmp_pressure" : "hPa",
        "battery_voltage" : "volts",
        "illuminance" : "lux",
        "sht_temperature" : "celsius",
        "fault_charge" : "boolean",
        "charge" : "boolean",
        "bmp_temperature" : "celsius"
    }

    for device in data.json():

        name = device['src']

        # start building the device to post/check
        '''
		Example data where "src" is the device name, and the rest are sensor Metrics.
        
        Units:
        illuminance: lux
        pressure: hPa
        temperature: celsius
        battery: volts
		{
            "src": "0x8110", 
            "via": "0x0000", 
            "sht_humidity": 15.9, 
            "bmp_pressure": 911.62, 
            "battery_voltage": 4.62, 
            "illuminance": 413, 
            "sht_temperature": 25.32, 
            "charge_flags": {
                "fault": false, 
                "charge": false
            }, 
    	  "bmp_temperature": 54.6
		}
        '''
        device_data = {
            'name': name,
        }

        # unique device spec
        unique_device = name
        
        # if we don't have the device in doppel2, POST it
        if unique_device not in unique_devices.keys():
            r = requests.post(listDevicesHref, data=json.dumps(device_data))

            sensorHref = r.json()["sensors"]["_href"]
            unique_devices[unique_device] = sensorHref

        for sensor in unitsDict:

            if sensor in ["charge_fault", "charge"]:
                value = device.get("charge_flags")[sensor]
            else:
                value = device.get(sensor)

            tempSensordata = {
                'value' : value,
                'timestamp': str(now)
            }

            # first get the device _href associated with the sensors. by now we should've 
            # added the device so the call to the unique_devices dictionary should be valid
            sensorHref = unique_devices[unique_device]
            uniqueSensor = (name, sensor)

            if uniqueSensor not in unique_sensors.keys():
                unit = unitsDict.get(sensor)
                if unit == None:
                    # default to a value and must go find it
                    unit = "NO UNIT FOUND"

                sensorObject = {
                    'metric' : sensor,
                    'unit' : unit
                }
                p = requests.post(sensorHref, data=json.dumps(sensorObject))
                sensorDataHref = p.json()['history']['_href']
                unique_sensors[uniqueSensor] = sensorDataHref

            sensorDataHref = unique_sensors[uniqueSensor]

            # post the data to the historical data field
            requests.post(sensorDataHref, data=json.dumps(tempSensordata))
