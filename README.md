General API Concept Overview
============================

The Chain API is built on top of the [Hypertext Application Language][1],
or HAL. Currently it only implements the application/hal+json MIME type.
hal+json is relatively simple, and clients are free to ignore HAL and treat the
responses as regular JSON data. There are also various libraries that can
take advantage of the hal+json conventions to abstract some of the details
away. For a more thorough spec of hal+json see [this IETF draft][2].


Link Relations
--------------

Given a link from one resource to another, clients generally need to know what
sort of relationship that link is modeling. Is it a link from a child to a
parent? From a device to a list of contained sensors? These relations (often
shortened to "rels") are central to the architecture of the Chain API, and
hypermedia in general.

Following along with standard hal+json, most rels are self-documenting, and the
rel itself actually serve as a link(URI) to the human-readable documentation
that describes what that relationship actually means. This rel URI should also
be used by clients as a unique, persistant identifier. This gives flexibility
to server implementers as they can add new relation types, or even new versions
of existing relation types, to existing resources without breaking older
clients. As long as the new rels have unique URIs, old clients will simply
ignore them.

Some relations are specific to the Chain API, in which case they are documented
on the Chain API site (currently chain-api.media.mit.edu). Where possible, the
API uses [standard link rel names][rels-iana] in which case the rel names are
not qualified with a URI. See [RFC5988][rfc5988] for more info on link
relations.

In the Chain API attributes can also be considered relations, except the
related object is simple data, instead of a linked or embedded resource. As
such, attributes use the same self-documenting mechanism as resource relations.

CURIES
------

Using URIs as relation names has the benefit of providing a stable and unique
identifier for relation names, but using a full URI as a json dictionary key is
cumbersome and duplicates lots of data in a typicaly payload. To alleviate this
issue hal+json supports Compact URIs or "CURIEs". CURIEs. The
[wikipedia page][curie-wiki] shows an example of a CURIE used as an XML
namespace, and the [w3c spec][curie-w3c] has a much more detailed description.
In the context of hal+json CURIEs are simply a URI template that can be used
for each rel that references it.

Getting Resources
-----------------

The URIs given at the API entry point point to Collection Resources. Sending an
HTTP GET request to a Collection Resource will return a response with the
requested resources as well as metadata about the response. This metadata
includes the total number of resources represented by this collection. If there
are more resources than will fit into a single response, the meta field may
also contain links to the first, last, previous, and next pages.

### hal+json Example

    GET /orders HTTP/1.1
    Host: example.org
    Accept: application/hal+json

    HTTP/1.1 200 OK
    Content-Type: application/hal+json

    {
      "_links": {
        "self": { "href": "/orders" },
        "next": { "href": "/orders?page=2", "title": "Page 2" },
        "last": { "href": "/orders?page=5", "title": "Page 5" },
        "curies": [{
            "name": "rel",
            "href": "http://docs.example.org/rels/{rel}",
            "templated": true
        }]
      },
      "_embedded": {
        "rel:orders": [{
          "_links": {
            "self": { "href": "/orders/123" },
            "rel:basket": { "href": "/baskets/98712" },
            "rel:customer": { "href": "/customers/7809" }
          },
          "total": 30.00,
          "currency": "USD",
          "status": "shipped",
        },{
          "_links": {
            "self": { "href": "/orders/124" },
            "rel:basket": { "href": "/baskets/97213" },
            "rel:customer": { "href": "/customers/12369" }
          },
          "total": 20.00,
          "currency": "USD",
          "status": "processing"
        }]
      },
      "currentlyProcessing": 14,
      "shippedToday": 20
    }

Sending a GET to the URI for a specific resource will return only that
resource, e.g.

    GET /orders/123 HTTP/1.1
    Host: example.org
    Accept: application/hal+json

    HTTP/1.1 200 OK
    Content-Type: application/hal+json
    {
      "_links": {
        "self": { "href": "/orders/123" },
        "rel:basket": { "href": "/baskets/98712" },
        "rel:customer": { "href": "/customers/7809" }
        "curies": [{
            "name": "rel",
            "href": "http://docs.example.org/rels/{rel}",
            "templated": true
        }]
      },
      "rel:total": 30.00,
      "rel:currency": "USD",
      "rel:status": "shipped",
    }


The Tidmarsh API
================

Entry Point
-----------

The API entry point is at `http://tidmarsh.media.mit.edu/api/`. A `GET` request
will give you links to the available sites in the following format:

    {
      "_links": {
        "self": { "href": "http://tidmarsh.media.mit.edu/api/" },
        "curies": [{
            "name": "ch",
            "href": "http://chain-api.media.mit.edu/rels/{rel}",
            "templated": true
        }]
      },
      "_embedded": {
        "ch:sites": [
          {
            "_links": {
              "self": { "href": "http://tidmarsh.media.mit.edu/api/sites/92" }
            },
            "name": "DoppelLab",
            "latitude": 42.360461,
            "longitude": -71.087347
          },
          {
            "_links": {
              "self": { "href": "http://tidmarsh.media.mit.edu/api/sites/12" }
            },
            "name": "TidMarsh",
            "latitude": 39.948171,
            "longitude": -70.827105
          }
        ]
      }
    }

Currently the only top-level resource available is the collection of Sites.
The client first selects which site they are interested in and can navigate
from there to explore that site. Clients should not assume hard-coded URIs, but
should instead get the proper URI from the API entry point.

Base Resource Types
===================

NOTE: At some point this information should be moved into the docstrings of
the resources themselves, so we can generate the documentation as well as the
information at the `_type` URLs from the same info.

Site
----

An installation of Doppel2, usually on the scale of several or many buildings.

### Resource Fields

* `name` (string) - Name of this site
* `latitude` (float) - The latitude of the site
* `longitude` (float) - The longitude of the site
* `devices` (related resource) - A collection of all the devices in this site.
  New devices can be POSTed to this collection to add them to this site.

### Example

    {
      "_links": {
          "curies": [{
              "name": "ch",
              "href": "http://chain-api.media.mit.edu/rels/{rel}",
              "templated": true
          }],
          "self": { "href": "http://tidmarsh.media.mit.edu/api/sites/92" },
          "ch:devices": {
              "title": "Devices",
              "href": "http://tidmarsh.media.mit.edu/api/sites/758/devices"
          }
      },
      "name": "DoppelLab",
      "latitude": 42.360461,
      "longitude": -71.087347
    }

Device
------

A device that may contain several sensor channels.

### Resource Fields

* `name` (string) - Name of this device
* `site` (related resource) - The site this device is a part of
* `description` (string) - A longer description of this device
* `building` (string) - The building the device is in
* `floor` (string) - The floor of the building
* `room` (string) - The room containing the device
* `sensors` (related resource) - A collection of all the sensors in this
  device. New sensors can be POSTed to this collection to add them to this
  device.
* `site` (related resource) - The site that this sensor is located at


### Example

    {
      "_links": {
          "curies": [{
              "name": "ch",
              "href": "http://chain-api.media.mit.edu/rels/{rel}",
              "templated": true
          }],
          "self": { "href": "http://tidmarsh.media.mit.edu/api/devices/929" },
          "ch:sensors": {
              "title": "Sensors",
              "href": "http://tidmarsh.media.mit.edu/api/devices/929/sensors"
          },
          "ch:site": {
              "title": "Summer Cabin"
              "href": "http://tidmarsh.media.mit.edu/api/sites/928",
          },
      },
      "name": "Bathroom Thermostat",
      "description": "Thermostat in the pool house bathroom",
      "building": "Pool House",
      "floor": "2",
      "room": "Bathroom",
    }

Sensor
------

A sensor captures a single channel of data. There may be multiple sensors on a
single device. Issuing a GET request for a Sensor resource also includes the
current value for that sensor. The value could be a scalar value or some other
TBD data types.

### Resource Fields

* `device` (related resource) - The device this sensor is part of
* `history` (related resource) - Collection of data from this sensor
* `metric` (string) - What the sensor is measuring (e.g. "temperature")
* `unit` (string) - The unit the data is in (e.g. "kWh")
* `updated` (ISO8601 timestamp) - Timestamp of the most recent update
* `value` (various) - The most recent reading from this sensor. Currently only
  floating point sensors are supported, but in the future this could be an xyz
  position, GPS coordinate, image, etc.

_TODO: We need to figure out a way to communicate the datatype_

### Example

    {
      "_links": {
          "curies": [{
            "name": "ch",
            "href": "http://chain-api.media.mit.edu/rels/{rel}",
            "templated": true
          }],
          "self": { "href": "http://tidmarsh.media.mit.edu/api/sensors/929" },
          "ch:history": {
            "title": "History",
            "href": "http://tidmarsh.media.mit.edu/api/sensors/929/history"
          },
          "ch:device": {
            "title": "Bathroom Thermostat",
            "href": "http://tidmarsh.media.mit.edu/api/devices/928",
          },
      },
      "value": 23.5,
      "updated": "2014-03-12T13:37:27+00:00"
      "metric": "temperature",
      "unit": "C"
    }

Sensor Data
-----------

Sensor Data is the raw data captured by the sensors. Each Sensor Data resource
represents a single data point, so the client is often looking at large
aggregations of this data.

### Resource Fields

* `value` (float) - The value of the sensor data
* `timestamp` (ISO 8601 timestamp) - Timestamp marking when the data was
  captured

### Example

    {
      "_links": {
          "self": { "href": "http://tidmarsh.media.mit.edu/api/scalar_data/91830" }
      },
      "value": 23.5,
      "timestamp": "2014-03-12T13:37:27+00:00"
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

from within that folder run "vagrant up" and it should instantiate the virtual
machine.

after the machine is up you can run "vagrant ssh" to ssh into the new VM. From
there you can follow the below instructions on setting up a Doppel2 server.

Doppel2 Server Setup Instructions
=================================

Install puppet and the proper puppet modules with

    sudo apt-get install puppet
    (or on Arch use yaourt -S puppet)
    sudo puppet module install puppetlabs/postgresql -v3.2.0

NOTE FOR ARCH:

The puppet manifest doesn't work well on Arch, so just install the python
packages with pip system packages with pacman that are listed in the manifest,
and comment those stanzas out.  I also had to set the ownership of
/var/lib/postgres with:

    sudo chown -R postgres:users /var/lib/postgres

END OF ARCH-SPECIFIC NOTE

edit manifest.pp and change the database username and password.

Edit settings.py and set the username and password, as well as the
`SECRET_KEY` setting.

Then set up the server with

    sudo puppet apply manifest.pp


Now you can initialize your django environment

    ./manage.py syncdb
    ./manage.py migrate

Now you should be able to run the server with:

    ./manage.py runserver 0.0.0.0:8000

and access it from your host machine's browser at

    http://localhost:8000/admin

[1]: [http://stateless.co/hal_specification.html]
[2]: [http://tools.ietf.org/html/draft-kelly-json-hal-06]
[rfc5988]: [http://tools.ietf.org/html/rfc5988]
[curie-w3c]: [http://www.w3.org/TR/curie/]
[curie-wiki]: [http://en.wikipedia.org/wiki/CURIE]
[rels-iana]: [http://www.iana.org/assignments/link-relations/link-relations.xhtml]
