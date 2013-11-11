*NOTE: DOPPEL2 IS IN HEAVY DEVELOPMENT AND NOT YET READY FOR USE*

API Overview
============

Resource Representation
-----------------------

All resources are specified with a URI. When presented to the client, the
resource is represented as a JSON object with at minimum an `_href` property
that contains its URI. and a `_type` property that should be a link that both
uniquely identifies that resource type and also provides its documentation.
When a parent resource (such as a Collection Resource or some other related
resource) contains embedded child resources, those resources may be fully
embedded or may only contain the `_href` property, in which case the client
should follow the given link to access the child resource. Clients should be
written to handle both cases transparently, to support future server-side
changes and optimizations.

### Example of an embedded resource

    GET http://example.com/api/books/483

    {
        '_href': 'http://example.com/api/books/483',
        '_type': 'http://example.com/api-types/book',
        'title': 'Jane Eyre',
        'author': {
            '_href': 'http://example.com/api/authors/910',
            '_type': 'http://example.com/api-types/author',
            'firstName': 'Charlotte',
            'lastName': 'Bronte',
            'books': { '_href': '/api/authors/910/books/' }
        }
    }

### Example of a linked resource

    GET http://example.com/api/book/483

    {
        '_href': 'http://example.com/api/books/483',
        '_type': 'http://example.com/api-types/book',
        'title': 'Jane Eyre',
        'author': { '_href': 'http://example.com/api/authors/910' }
    }

A Parent resource might also contain a list of related resources, such as the
list of books by an author. In this case the 'books' field would be itself
a Collection Resource, so the Author resource would look like:

    GET http://example.com/api/authors/910

    {
        '_href': 'http://example.com/api/authors/910',
        '_type': 'http://example.com/api-types/author',
        'firstName': 'Charlotte',
        'lastName': 'Bronte'
        'books': { '_href': 'http://example.com/api/authors/910/books/ }
    }

Or if the 'books' resource is expanded:

    GET http://example.com/api/authors/910

    {
        '_href': 'http://example.com/api/authors/910',
        '_type': 'http://example.com/api-types/author',
        'firstName': 'Charlotte',
        'lastName': 'Bronte'
        'books': {
            '_href': 'http://example.com/api/authors/910/books/',
            'meta': { 'total_count': 3 },
            '_type': 'resource-list',
            'data': [
                {
                    '_href': 'http://example.com/api/books/483',
                    '_type': 'http://example.com/api-types/book',
                    'title': 'Jane Eyre',
                    'author': { '_href': 'http://example.com/api/authors/910' }
                },
                {
                    '_href': 'http://example.com/api/books/918',
                    '_type': 'http://example.com/api-types/book',
                    'title': 'Shirley',
                    'author': { '_href': 'http://example.com/api/authors/910' }
                },
                {
                    '_href': 'http://example.com/api/books/710',
                    '_type': 'http://example.com/api-types/book',
                    'title': 'The Professor',
                    'author': { '_href': 'http://example.com/api/authors/910' }
                },
            ]
        }
    }

Getting Resources
-----------------

The URIs given at the API entry point point to Collection Resources. Sending an
HTTP GET request to a Resource List will return a response with the requested
resources as well as metadata about the response. Currently the only supported
metadata is the total count of that resource. In the future this metadata will
include information mostly useful for pagination such as the limit, offset, and
a link to the next page of data. See below for an example response.

    GET http://example.com/api/some_resources/

    {
        '_href': 'http://example.com/api/some_resources/',
        'meta': { "total_count": 2 },
        'data': [
            {
                '_href': 'http://example.com/api/some_resources/192',
                '_type': 'http://example.com/api-types/some_resource',
                'name': 'A great resource',
                'state': 'Idaho'
            },
            {
                '_href': 'http://example.com/api/some_resources/193',
                '_type': 'http://example.com/api-types/some_resource',
                'name': 'Another Resource',
                'state': 'New York'
            }
        ]
    }

Sending a GET to the URI for a specific resource will return only that
resource, e.g.

    GET http://example.com/api/some_resources/193

    {
        '_href': 'http://example.com/api/some_resources/193',
        '_type': 'http://example.com/api-types/some_resource',
        'name': 'Another Resource',
        'state': 'New York'
    }

Filtering Resources
-------------------

NOTE: this section is under revision, and may not be how we handle things in
the end

In general the Collection Resources can be filtered with any filter available
through the django ORM, described at
https://docs.djangoproject.com/en/1.5/ref/models/querysets/#field-lookups. The
filters are given in the query string, for example if a resource has a field
called `timestamp` and the client wished to retreive all the resources since
April 12, 2013 at midnight, it could send a `GET` request to:

    http://example.com/api/scalar_data/?timestamp__gt=2013-04-12T00:00:00Z

Note that when filtering, dates should be given ISO 8601 format with the time
zone specified.

Grouping and Aggregating
------------------------

NOTE: THIS ISN'T HOW WE'RE DOING THINGS

rather than trying to implement a general query language, we're going to
provide the client with useful groupings via the URL linkages. For now I'm
keeping the below content for reference as the API develops.

END NOTE

Often the client will want to collect a large number of resources, each of
which might have a lot of data in common. For instance, when requesting a block
of sensor data, each data resource will contain the unit and metric. To reduce
data duplication in the response and potentially ease client-side parsing, the
client can request that the data be grouped by the common values by using the
`group_by=FIELD` query parameter. Additionally, the client might be interested
in an aggregate value across a set of resources, such as calculating the
average, or getting the maximum. Currently only averaging is supported, and can
be accessed using the `average_by=FIELD` query parameter.

For example, a `GET` request to `api/room_temps/` might return:

    {
        'meta': {
            "total_count": 4
        },
        'data': [
            {
                '_href': 'http://example.com/api/room_temps/192',
                '_type': 'http://example.com/api-types/room_temp',
                'room': 'Bedroom',
                'temperature': 26,
                'timestamp': '2013-04-12T03:30:00Z'
            },
            {
                '_href': 'http://example.com/api/room_temps/193',
                '_type': 'http://example.com/api-types/room_temp',
                'room': 'Bedroom',
                'temperature': 27,
                'timestamp': '2013-04-12T03:35:00Z'
            },
            {
                '_href': 'http://example.com/api/room_temps/194',
                '_type': 'http://example.com/api-types/room_temp',
                'room': 'Living Room',
                'temperature': 22,
                'timestamp': '2013-04-12T03:30:00Z'
            },
            {
                '_href': 'http://example.com/api/room_temps/195',
                '_type': 'http://example.com/api-types/room_temp',
                'room': 'Living Room',
                'temperature': 28,
                'timestamp': '2013-04-12T03:35:00Z'
            }
        ]
    }

whereas a `GET` request to `http://example.com/api/room_temps/?group_by=room` would return:

    {
        "meta": {
            "total_count": 4
        },
        "room_groups": {
            "Bedroom": [
                {
                    "_href": "http://example.com/api/room_temps/192",
                    '_type': 'http://example.com/api-types/room_temp',
                    "temperature": 26,
                    "timestamp": "2013-04-12T03:30:00Z"
                },
                {
                    "_href": "http://example.com/api/room_temps/193",
                    '_type': 'http://example.com/api-types/room_temp',
                    "temperature": 27,
                    "timestamp": "2013-04-12T03:35:00Z"
                }
            ],
            "Living Room": [
                {
                    "_href": "http://example.com/api/room_temps/194",
                    '_type': 'http://example.com/api-types/room_temp',
                    "temperature": 22,
                    "timestamp": "2013-04-12T03:30:00Z"
                },
                {
                    "_href": "http://example.com/api/room_temps/195",
                    '_type': 'http://example.com/api-types/room_temp',
                    "temperature": 28,
                    "timestamp": "2013-04-12T03:35:00Z"
                }
            ]
        }
    }

and a `GET` request to `http://example.com/api/room_temps/?average_by=temperature` would return:

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
http://example.com/api/room_temps/?average_by=temperature&group_by=room would return:

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

Entry Point
-----------

The API entry point is at `http://example.com/api/`, so a `GET` request will give you links to
the available base resources in the following format:

    {
        '_href': 'http://example.com/api/',
        '_type': 'http://example.com/api-types/api-root',
        'sites': {
            '_href': 'http://example.com/api/sites/',
            '_type': 'resource-list',
            'meta': { 'total_count': 2 },
            'data': [
                {
                    '_href': 'http://example.com/api/sites/92',
                    '_type': 'http://example.com/api-types/site',
                    'name': 'DoppelLab',
                },
                {
                    '_href': 'http://example.com/api/sites/12',
                    '_type': 'http://example.com/api-types/site',
                    'name': 'TidMarsh',
                }
            }
        }
    }

Currently the only top-level resource available is the collection of Sites.
The client first selects which site they are interested in and can navigate
from there to explore that site.  Clients should not assume hard-coded URIs,
but should instead get the proper URI from the API entry point.

Base Resource Types
===================

NOTE: At some point this information should be moved into the docstrings of
the resources themselves, so we can generate the documentation as well as the
information at the `_type` URLs from the same info.

Site
----

An installation of Doppel2, usually on the scale of several or many buildings.

### Example

    {
        '_href': 'http://example.com/api/sites/758',
        '_type': 'http://example.com/api-types/site',
        'name': 'TidMarsh',
        'devices': { '_href': 'http://example.com/api/sites/758/devices' }
    }

Device
------

A device that may contain several sensor channels.

### Example

    {
        '_href': 'http://example.com/api/devices/129',
        '_type': 'http://example.com/api-types/device',
        'name': 'Bathroom Thermostat',
        'site': { '_href': 'http://example.com/api/sites/928' },
        'building': 'Pool House',
        'floor': '2',
        'room': 'Bathroom',
        'sensors': { '_href': 'http://example.com/api/devices/129/sensors' }
    }

Sensor
------

A sensor captures a single channel of data. There may be multiple sensors on a
single device. Issuing a GET request for a Sensor resource also includes the
current value for that sensor. The value could be a scalar value or some other
TBD data types.

### Resource Fields

* `_href` (string) - URI of this resource
* `_type` (string) - Type of this resource
* `device` (string) - URI of the device this sensor is part of
* `metric` (string) - What the sensor is measuring (e.g. 'temperature')
* `unit` (string) - The unit the data is in (e.g. 'kWh')
* `value` (variable type) - The last reported value of the sensor
* `updated_timestamp` (ISO 8601 timestamp) - Timestamp marking when the data
  was captured

### Example

    {
        '_href': 'http://example.com/api/sensors/758',
        '_type': 'http://example.com/api-types/sensor',
        'device': { '_href': 'http://example.com/api/devices/358' },
        'metric': 'temperature',
        'unit': 'C'
        'value': 25.2,
        'updated_timestamp': '2013-04-12T03:30:00Z'
    }

Scalar Data
-----------

Scalar Data is the raw data captured by the sensors.

### Resource Fields

* `_href` (string) - URI of this resource
* `sensor_uri` (string) - URI of the sensor that captured this data
* `value` (float) - The value of the sensor data
* `timestamp` (ISO 8601 timestamp) - Timestamp marking when the data was
  captured

### Example

    {
        '_href': 'http://example.com/api/scalar_data/193',
        '_type': 'http://example.com/api-types/scalar_data',
        'sensor': { '_href': 'http://example.com/api/sensors/91' },
        'value': 25.2,
        'timestamp': '2013-04-12T03:30:00Z',
    }

Dev Server Initial Setup
========================

To develop for doppel2 the best way is with a virtual machine. The following
instructions should guide you through setting up a development environment that
should match the production machine.

First you'll want to make sure that both Virtualbox and Vagrant are installed,
as well as mercurial.

Then clone the code from the repository with:

    hg clone http://simonetti.media.mit.edu/hg/doppel2

Mercurial (hg) will create a folder called doppel2 and check out the code into
it.

from within that folder run 'vagrant up' and it should instantiate the virtual
machine.

after the machine is up you can run 'vagrant ssh' to ssh into the new VM. From
there you can follow the below instructions on setting up a Doppel2 server.

Doppel2 Server Setup Instructions
=================================

Install puppet and the proper puppet modules with

    sudo apt-get install puppet
    sudo puppet module install puppetlabs/postgresql -v3.2.0

Then set up the server with

    sudo puppet apply manifest.pp


Now you can initialize your django environment

    ./manage.py syncdb
    ./manage.py migrate

Now you should be able to run the server with:

    ./manage.py runserver 0.0.0.0:8000

and access it from your host machine's browser at

    http://localhost:8000/admin
