#!/usr/bin/python
# -*- coding: utf-8 -*-

# import requests

import json
import datetime
import time
import urllib
import django.utils.simplejson as jsonUtil
import requests

STAT_BASE_URL = \
    'http://tac.mit.edu/E14_displays/get_controller_data.aspx?floor='
DOPPEL_BASE_URL = 'http://localhost:8000/api/'
DOPPEL_SITE_URL = DOPPEL_BASE_URL + 'sites/18'

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
        unique_devices[(device['name'], device['floor'], device['building'], device['room'])] = listSensorsHref

        # loop through the sensors in this device and add them to the unique_sensor dictionary
        for sensor in listSensors:
            unique_sensors[(device['name'], sensor['metric'])] = sensor['history']['_href']

    # scrape data per floor
    for floor in range(1, 7):
        url = STAT_BASE_URL + str(floor)
        floorData = requests.get(url)
        now = datetime.datetime.now()

        # sort of a debug tool for now to make sure we don't post repeated unique devices
        printDBStatement = True

        # loop through each device and check to see if we already have it in doppel2
        for therm in floorData.json():

            # parse the "name" field so that we can extract the building and room number
            name = therm['name']
            dataParsed = name.split('_')

            building = dataParsed[0]
            room = dataParsed[1]

            # add it to the dictionary
            therm['building'] = building
            therm['room'] = room

            # start building the device to post/check
            device_data = {
                'building': building,
                'floor': floor,
                'room': room,
                'name': name,
                }

            # unique device spec
            therm_device = (name, str(floor), building, room)
            
            # if we don't have the device in doppel2, POST it
            if therm_device not in unique_devices.keys():
                r = requests.post(listDevicesHref, data=json.dumps(device_data))
                printDBStatement = False
  
                sensorHref = r.json()["sensors"]["_href"]
                unique_devices[therm_device] = sensorHref

            # sensor parsing. specific to the data we poll in this script
            tempSensors = {}
            tempSensordata = {}

            sensor_temp_value = therm['temp']
            sensor_setpoint_value = therm['setpoint']

            sensor_metric_temp = 'temp'
            sensor_metric_setpoint = 'setpoint'

            tempSensors['temp'] = {
                'metric': sensor_metric_temp,
                'unit': 'celsius',
            }
            tempSensordata['temp'] = {
                'value': sensor_temp_value,
                'timestamp': str(now),
            }

            tempSensors['setpoint'] = {
                'metric': sensor_metric_setpoint,
                'unit': 'celsius',
            }
            tempSensordata['setpoint'] = {
                'value': sensor_setpoint_value,
                'timestamp': str(now),
            }

            for sensor in tempSensors.keys():
                # first get the device _href associated with the sensors. by now we should've 
                # added the device so the call to the unique_devices dictionary should be valid
                sensorHref = unique_devices[therm_device]
                uniqueSensor = (name, tempSensors[sensor]['metric'])

                if uniqueSensor not in unique_sensors.keys():
                    p = requests.post(sensorHref, data=json.dumps(tempSensors[sensor]))
                    sensorDataHref = p.json()['history']['_href']
                    unique_sensors[uniqueSensor] = sensorDataHref

                sensorDataHref = unique_sensors[uniqueSensor]

                # post the data to the historical data field
                requests.post(sensorDataHref, data=json.dumps(tempSensordata[sensor]))
                
        if printDBStatement:
            print 'All devices already on doppel DB on floor ' + str(floor)
