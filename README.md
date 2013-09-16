*NOTE: DOPPEL2 IS IN HEAVY DEVELOPMENT AND NOT YET READY FOR USE*

API Overview
============

Entry Point
-----------

The API entry point is at /api/, so a GET request will give you links to the
available base resources in the following format:

    {
        'scalar_data': '/api/scalar_data/',
        'sensor': '/api/sensor/',
        'device': '/api/device/'
    }

New resource types may be added in the future. Clients should not assume
hard-coded URIs, but should instead get the proper URI from the API entry
point.

Getting Resources
-----------------

The URIs given at the API entry point point to Resource Lists. Sending an HTTP
GET request to a Resource List will return a response with the requested
resources as well as metadata about the response. Currently the only supported
metadata is the total count of that resource. In the future this metadata will
include information mostly useful for pagination such as the limit, offset, and
a link to the next page of data. See below for an example response.

    {
        'meta': {
            "total_count": 2
        },
        'objects': [{
            'resource_uri': '/api/some_resource/192',
            'name': 'A great resource',
            'state': 'Idaho'
        },
        {
            'resource_uri': '/api/some_resource/193',
            'name': 'Another Resource',
            'state': 'New York'
        }]
    }

In addition to the resource-specific data, each resource in the 'objects' list
will contain a 'resource_uri' field where the client can access that specific
resource, for instance if the client wanted to modify it. Sending a GET to the
URI for a specific resource will return only that resource, e.g.

        {
            'resource_uri': '/api/some_resource/193',
            'name': 'Another Resource',
            'state': 'New York'
        }

Filtering Resources
-------------------

In general the resource lists can be filtered with any filter available through
the django ORM, described at
https://docs.djangoproject.com/en/1.5/ref/models/querysets/#field-lookups. The
filters are given in the query string, for example if a resource has a field
called 'timestamp' and the client wished to retreive all the resources since
April 12, 2013 at midnight, it could send a GET request to:

    /api/scalar_data/?timestamp__gt=2013-04-12T00:00:00Z

Note that when filtering, dates should be given ISO 8601 format with the time
zone specified.

Grouping and Aggregating
------------------------

Often the client will want to collect a large number of resources, each of
which might have a lot of data in common. For instance, when requesting a block
of sensor data, each data resource will contain the unit and metric. To reduce
data duplication in the response and potentially ease client-side parsing, the
client can request that the data be grouped by the common values by using the
'group_by=FIELD' query parameter. Additionally, the client might be interested
in an aggregate value across a set of resources, such as calculating the
average, or getting the maximum. Currently only averaging is supported, and can
be accessed using the 'average_by=FIELD' query parameter.

For example, a GET request to /api/room_temp/ might return:

    {
        'meta': {
            "total_count": 4
        },
        'objects': [
            {
                'resource_uri': '/api/room_temp/192',
                'room': 'Bedroom',
                'temperature': 26,
                'timestamp': '2013-04-12T03:30:00Z'
            },
            {
                'resource_uri': '/api/room_temp/193',
                'room': 'Bedroom',
                'temperature': 27,
                'timestamp': '2013-04-12T03:35:00Z'
            },
            {
                'resource_uri': '/api/room_temp/194',
                'room': 'Living Room',
                'temperature': 22,
                'timestamp': '2013-04-12T03:30:00Z'
            },
            {
                'resource_uri': '/api/room_temp/195',
                'room': 'Living Room',
                'temperature': 28,
                'timestamp': '2013-04-12T03:35:00Z'
            }
        ]
    }

whereas a GET request to /api/room_temp/?group_by=room would return:

    {
        "meta": {
            "total_count": 4
        },
        "room_groups": {
            "Bedroom": [
                {
                    "resource_uri": "/api/room_temp/192",
                    "temperature": 26,
                    "timestamp": "2013-04-12T03:30:00Z"
                },
                {
                    "resource_uri": "/api/room_temp/193",
                    "temperature": 27,
                    "timestamp": "2013-04-12T03:35:00Z"
                }
            ],
            "Living Room": [
                {
                    "resource_uri": "/api/room_temp/194",
                    "temperature": 22,
                    "timestamp": "2013-04-12T03:30:00Z"
                },
                {
                    "resource_uri": "/api/room_temp/195",
                    "temperature": 28,
                    "timestamp": "2013-04-12T03:35:00Z"
                }
            ]
        }
    }

and a GET request to /api/room_temp/?average_by=temperature would return:

    {
        "meta": {
            "total_count": 4
        },
        "temperature_average": 25.75
    }

Note that when aggregating data, the other fields from the original resources
are discarded. The dictionary key for the aggregate value is given by
FIELD_average. Grouping and Aggregating can be combined, in which case the
aggregation happens within each group. so a GET request to
/api/room_temp/?average_by=temperature&group_by=room would return:

    {
        "meta": {
            "total_count": 4
        },
        "room_groups": {
            "BedRoom": {
                "temperature_average": 26.5
            },
            "Living Room": {
                "temperature_average": 25.0
            }
        }
    }

To summarize, the order of operations is always filtering, then grouping, then
aggregation. The 'total_count' field represents the number of resources
reprensented by the response, so it is the count after filtering but before
aggregation (grouping doesn't effect the number of returned resources).

Base Resource Types
===================

Sensor
------

A sensor captures a single channel of data. There may be multiple sensors on a
single device. Issuing a GET request for a Sensor resource also includes the
current value for that sensor. The value could be a scalar value or some other
TBD data types.

### Resource Fields

* resource_uri (string) - URI of this resource
* device_uri (string) - URI of the device this sensor is part of
* metric (string) - What the sensor is measuring (e.g. 'temperature')
* unit (string) - The unit the data is in (e.g. 'kWh')
* value (variable type) - The last reported value of the sensor
* updated_timestamp (ISO 8601 timestamp) - Timestamp marking when the data was captured

### Groupable Fields

* device_uri
* metric

### Aggregatable Fields

* value

### Filterable Fields

* device_uri
* metric
* unit
* value
* updated_timestamp

### Example

    {
        'resource_uri': '/api/sensor/758',
        'device_uri': '/api/device/358',
        'metric': 'temperature',
        'unit': 'C'
        'value': 25.2,
        'updated_timestamp': '2013-04-12T03:30:00Z'
    }

Scalar Data
-----------

Scalar Data is the raw data captured by the sensors.

### Resource Fields

* resource_uri (string) - URI of this resource
* sensor_uri (string) - URI of the sensor that captured this data
* value (float) - The value of the sensor data
* timestamp (ISO 8601 timestamp) - Timestamp marking when the data was captured

### Groupable Fields

* sensor_uri

### Aggregatable Fields

* value

### Filterable Fields

* timestamp
* sensor_uri
* value

### Example

    {
        'resource_uri': '/api/scalar_data/193',
        'sensor_uri': '/api/sensor/91',
        'value': 25.2,
        'timestamp': '2013-04-12T03:30:00Z',
    }

Doppel2 Server Setup Instructions
=================================

Install puppet and the proper puppet modules with

    sudo apt-get install puppet
    sudo puppet module install puppetlabs/postgresql

Then set up the server with

    sudo puppet apply manifest.pp

