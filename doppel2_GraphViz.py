#!/usr/bin/python
# -*- coding: utf-8 -*-

site5 = {
    '_type': 'resource-list',
    'meta': {'totalCount': 3},
    'data': [{
        'building': '',
        '_type': 'device',
        'description': '',
        'floor': '',
        'site': {'_href': 'http://localhost:8000/api/sites/5'},
        'name': 'Test Device 948869566',
        'room': '',
        'sensors': {
            '_type': 'resource-list',
            'meta': {'totalCount': 4},
            'data': [{
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1355',
                'metric': 'temperature',
                'device': {'_href': 'http://localhost:8000/api/devices/983'},
                'unit': 'celsius',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1355'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1356',
                'metric': 'pressure',
                'device': {'_href': 'http://localhost:8000/api/devices/983'},
                'unit': 'kPa',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1356'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1357',
                'metric': 'setpoint',
                'device': {'_href': 'http://localhost:8000/api/devices/983'},
                'unit': 'celsius',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1357'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1358',
                'metric': 'ambient light',
                'device': {'_href': 'http://localhost:8000/api/devices/983'},
                'unit': 'lux',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1358'
                            },
            }],
            '_href': 'http://localhost:8000/api/sensors/?device_id=983',
        },
        '_href': 'http://localhost:8000/api/devices/983',
    }, {
        'building': '',
        '_type': 'device',
        'description': '',
        'floor': '',
        'site': {'_href': 'http://localhost:8000/api/sites/5'},
        'name': 'Test Device 524913069',
        'room': '',
        'sensors': {
            '_type': 'resource-list',
            'meta': {'totalCount': 4},
            'data': [{
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1351',
                'metric': 'temperature',
                'device': {'_href': 'http://localhost:8000/api/devices/982'},
                'unit': 'celsius',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1351'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1352',
                'metric': 'pressure',
                'device': {'_href': 'http://localhost:8000/api/devices/982'},
                'unit': 'kPa',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1352'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1353',
                'metric': 'setpoint',
                'device': {'_href': 'http://localhost:8000/api/devices/982'},
                'unit': 'celsius',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1353'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1354',
                'metric': 'ambient light',
                'device': {'_href': 'http://localhost:8000/api/devices/982'},
                'unit': 'lux',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1354'
                            },
            }],
            '_href': 'http://localhost:8000/api/sensors/?device_id=982',
        },
        '_href': 'http://localhost:8000/api/devices/982',
    }, {
        'building': '',
        '_type': 'device',
        'description': '',
        'floor': '',
        'site': {'_href': 'http://localhost:8000/api/sites/5'},
        'name': 'Test Device 112916431',
        'room': '',
        'sensors': {
            '_type': 'resource-list',
            'meta': {'totalCount': 4},
            'data': [{
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1347',
                'metric': 'temperature',
                'device': {'_href': 'http://localhost:8000/api/devices/981'},
                'unit': 'celsius',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1347'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1348',
                'metric': 'pressure',
                'device': {'_href': 'http://localhost:8000/api/devices/981'},
                'unit': 'kPa',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1348'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1349',
                'metric': 'setpoint',
                'device': {'_href': 'http://localhost:8000/api/devices/981'},
                'unit': 'celsius',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1349'
                            },
            }, {
                '_type': 'sensor',
                '_href': 'http://localhost:8000/api/sensors/1350',
                'metric': 'ambient light',
                'device': {'_href': 'http://localhost:8000/api/devices/981'},
                'unit': 'lux',
                'history': {'_href': 'http://localhost:8000/api/sensordata/?sensor_id=1350'
                            },
            }],
            '_href': 'http://localhost:8000/api/sensors/?device_id=981',
        },
        '_href': 'http://localhost:8000/api/devices/981',
    }],
    '_href': 'http://localhost:8000/api/devices/?site_id=5',
}

import random

def createGraphVizPropertyDicts():
    ''' Creates the two property dictionaries for graph viz line
    properties.

    Returns them as a list'''

    tags = {'site': 'shape=box, style=filled, color="#2ca25f", fontsize=30',
            'device': 'shape=octagon, style=filled, color="#66c2a4", fontsize=30',
            'sensor': 'shape=hexagon, style=filled, color="#b2e2e2", fontsize=25'}
    relations = {
        'SITE': 'color=black, penwidth=1, fontsize=25, fontcolor="black',
        'CHILD': 'color=black, penwidth=1, fontsize=25, fontcolor="black"',
        'GROUP': 'color=red, penwidth=1, fontsize=25, fontcolor="red", dir="both"',
        'SITE': 'color=blue, penwidth=1, fontsize=25, fontcolor="blue"',
    }
    return [tags, relations]


def drawSensorTag(
    gvfile,
    sensorIndex,
    sensor,
    tags,
):
    ''' Given a sensor and its ID, write a tag line
    to the gvfile with the sensor ID as the tag number'''

    tags = tags
    (name, value, number) = sensor
    line = '  %d [label = "%s sensor# %s\\nvalue = %.2f", %s];\n' % (
        sensorIndex, name, number, value, tags['sensor'])
    gvfile.write(line)


def drawTags(gvfile, devices, tags):
    ''' Loop through each device and write tag lines
    to the gvfile for each device, followed by each sensor.
    Runtime of O(devices*sensors).'''

    tags = tags
    deviceIndex = 1
    sensorIndex = len(devices) + 1

    for device in devices:
        line = '  %d [label = "Device# %s", %s];\n' % (
            deviceIndex, device[0], tags['device'])
        gvfile.write(line)

        for sensor in device[1]:
            drawSensorTag(gvfile, sensorIndex, sensor, tags)
            sensorIndex += 1

        deviceIndex += 1


def drawSensorRelations(
    gvfile,
    deviceLen,
    deviceIndex,
    sensorIndex,
    sensors,
    relations,
):
    ''' Draw relations between devices and sensors,
    between sensors and their own grouped sensors,
    and between sensors and their parent site'''

    for sensor in sensors:
        line = '  %d -> %d [label = "CHILD", %s];\n' % (
            deviceIndex, sensorIndex, relations['CHILD'])
        gvfile.write(line)

        if sensorIndex < deviceLen * 5 - 3:
            line = '  %d -> %d [label = "GROUP", %s];\n' % (
                sensorIndex, sensorIndex, relations["GROUP"])
            gvfile.write(line)

        line = '  %d -> 0 [label = "SITE", %s];\n' % (
            sensorIndex, relations["SITE"])
        gvfile.write(line)

        sensorIndex += 1
    return sensorIndex


def drawRelations(gvfile, devices, relations):
    ''' Loop through each device and write relation lines
    to the gvfile for each device, followed by each sensor.
    Runtime of O(devices*sensors).'''

    relations = relations
    deviceIndex = 1
    deviceLen = len(devices)
    sensorIndex = deviceLen + 1
    for device in devices:
        line = '  0 -> %d [label = "CHILD", %s];\n' % (
            deviceIndex, relations["SITE"])
        gvfile.write(line)

        sensors = device[1]
        sensorIndex = drawSensorRelations(
            gvfile,
            deviceLen,
            deviceIndex,
            sensorIndex,
            sensors,
            relations,
        )

        deviceIndex += 1


def generate_graph(siteName, devices, filename):
    ''' Main file used to generate a gv file from a list of devices.
    This list is in the format:
    devices = [
        (deviceID, [
            (sensor1, value1, sensorID1),
            (sensor2, value2, sensorID2),
            (sensor3, value3, sensorID3),
            (sensor4, value4, sensorID4)
        ]),
        (deviceID2, [...])
    ]
    Right now, devices MUST have four different sensors each but
    this should be changed and made dynamic.

    The graph is a visual representation of a single Site with
    multiple devices each with four sensors. The relationships
    indlude hierarchical ones but this is NOT a DAG. It is an
    undirected graph.

    The runtime of this function is governed by two different double
    nested for loops to find each sensor for each device and write,
    first, its tag, and second, the relationships. A faster algorithm
    could certainly be implemented.
    '''

    (tags, relations) = createGraphVizPropertyDicts()
    gvfile = open(filename, 'w')
    line = 'digraph G {\n  0 [label = "Site: %s", %s];\n' % (
        siteName, tags["site"])

    gvfile.write(line)

    drawTags(gvfile, devices, tags)
    drawRelations(gvfile, devices, relations)

    gvfile.write('}\n')
    gvfile.close()


randomValueRanges = {
    'temperature': (20, 25),
    'pressure': (0.8, 1.2),
    'setpoint': (20, 25),
    'ambient light': (60, 100),
}


def getRandomValue(metric, valueRanges):
    '''Generates a random value in the range given
    per metric found in the randomValueRanges dict'''

    rangeValues = valueRanges[metric]
    rawValue = random.uniform(rangeValues[0], rangeValues[1])
    return round(rawValue, 2)


def createSensorListForDevice(sensors):
    ''' Creates a list of sensors in the format:
    [
        (sensor1, value1, sensorID1),
        (sensor2, value2, sensorID2),
        (sensor3, value3, sensorID3),
        (sensor4, value4, sensorID4)
    ]

    where the first value is the name of the sensor,
    the second is a value taken at random in the range
    provided by the dictionary randomValueRanges,
    and the last is the local ID of the sensor.

    Returns this list.
    '''

    sensorList = []
    for sensor in sensors:
        sensorNumber = sensor['_href'].split('sensors/')[-1]
        metric = sensor['metric']
        value = getRandomValue(metric, randomValueRanges)

        sensorList.append((metric, value, sensorNumber))
    return sensorList


def createDeviceListFromJSONObject(site):
    ''' Given a JSON Object taken from Doppel 2.0 API at

    ../devices/?site_id=2

    this function creates a devices list with sensors embedded.
    The data is obtained by using the Doppel Crawler script. It
    outputs devices and sensors at random.
    The format of the returned list is:
    devices = [
        (deviceID, [
            (sensor1, value1, sensorID1),
            (sensor2, value2, sensorID2),
            (sensor3, value3, sensorID3),
            (sensor4, value4, sensorID4)
            ]),
        (deviceID2, [...])
    ]
    '''

    deviceList = []
    for device in site['data']:
        deviceTagNumber = device['name'].split('Test Device ')[-1]
        sensorList = createSensorListForDevice(device['sensors']['data'])
        deviceList.append((deviceTagNumber, sensorList))

    return deviceList

if __name__=='__main__':
    deviceList = createDeviceListFromJSONObject(site5)
    generate_graph('Media Lab', deviceList, 'doppelGraph.gv')
