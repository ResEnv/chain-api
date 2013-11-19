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
DOPPEL_SITE_URL = DOPPEL_BASE_URL + 'sites/10'

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
    listDevicesHref = site.json()['devices']['_href']
    listDevices = site.json()['devices']['data']


    # get the list of devices from doppel2 and store key:value as device_name:device_floor
    unique_devices = {} # building, floor, and room
    unique_sensors = {} # 'device' and 'metric'

    for device in listDevices:
        # get the list of sensors for each device and the _href to post
        listSensorsHref = device['sensors']['_href']
        listSensors = requests.get(listSensorsHref).json()['data']

        # create the a unique device from each device in the server and store it along with 
        # the corresponding _href for sensor posting
        unique_devices[device['name']] = [device['floor'] + device['building'] + device['room'] + listSensorsHref]

        # loop through the sensors in this device and add them to the unique_sensor dictionary
        for sensor in listSensors:
            unique_sensor = [sensor['metric']]

            if unique_sensors.get(device['name']) != None:
                if unique_sensor not in unique_sensors.get(device['name']):
                    unique_sensors[device['name']] += unique_sensor

            else:
                unique_sensors[device['name']] = unique_sensor


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

            # default to no post unless we do not find the device in the unique_devices dict
            doDevicePost = False

            # unique device spec
            therm_device = str(device_data['floor']) + device_data['building'] + device_data['room']
            
            # if we don't have the device in doppel2, POST it
            if unique_devices.get(name) != None:
                if therm_device not in unique_devices.get(therm['name'])[0]:
                    ## TODO: add to unique_devices. can't right now because no way to get device _href without having posted it already
                    
                    ## deviceHref = unique_devices[name][1]
                    ## unique_devices[name] += [therm_device] + [deviceHref]
                    
                    doDevicePost = True

            if unique_devices.get(name) == None or doDevicePost:
                r = requests.post(listDevicesHref, data=json.dumps(device_data))
                printDBStatement = False
                ## TODO: like the one above
                ## unique_devices[name] = [therm_device] + [deviceHref]

            # sensor parsing. specific to the data we poll in this script
            tempSensors = {}

            sensor_temp_value = therm['temp']
            sensor_setpoint_value = therm['setpoint']

            sensor_metric_temp = 'temp'
            sensor_metric_setpoint = 'setpoint'

            tempSensors['temp'] = {
                'metric': sensor_metric_temp,
                'unit': 'celsius',
                'value': sensor_temp_value,
                'timestamp': str(now),
                }
            tempSensors['setpoint'] = {
                'metric': sensor_metric_setpoint,
                'unit': 'celsius',
                'value': sensor_setpoint_value,
                'timestamp': str(now),
                }

            ## TODO: once we can add the right _href above, enable this once again
            # for sensor in tempSensors.keys():
            #     # first get the device _href associated with the sensors. by now we should've 
            #     # added the device so the call to the unique_devices dictionary should be valid
            #     deviceHref = unique_devices[name][1]

            #     if unique_sensors.get(name) == None:
            #         requests.post(deviceHref,
            #                       data=json.dumps(tempSensors[sensor]))
            #     elif tempSensors[sensor]['metric'] not in unique_sensors.get(name):
            #         requests.post(deviceHref,
            #                       data=json.dumps(tempSensors[sensor]))

        if printDBStatement:
            print 'All devices already on doppel DB on floor ' + str(floor)
