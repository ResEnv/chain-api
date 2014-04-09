General API Concept Overview
============================

The Chain API is built on top of the [Hypertext Application Language][hal],
or HAL. Currently it only implements the application/hal+json MIME type.
hal+json is relatively simple, and clients are free to ignore HAL and treat the
responses as regular JSON data. There are also various libraries that can
take advantage of the hal+json conventions to abstract some of the details
away. For a more thorough spec of hal+json see [this IETF draft][hal-spec].


Link Relations
--------------

Given a link from one resource to another, clients generally need to know what
sort of relationship that link is modeling. Is it a link from a child to a
parent? From a device to a list of contained sensors? These relations (often
shortened to "rels") are central to the architecture of the Chain API, and
hypermedia in general.

Note that the `href` field in links will be a URL, which should be parsed
as per [RFC1808][rfc1808]. Basically this means that URLs might be absolute
(`http://example.com/things/392`) or relative to the domain (`/things/392`).
RFC1808 also allows URLs to be expressed relative to the current resource
(`../things/392`), but the Chain API does not use these.

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
issue hal+json supports Compact URIs or "CURIEs". The
[wikipedia page][curie-wiki] shows an example of a CURIE used as an XML
namespace, and the [w3c spec][curie-w3c] has a much more detailed description.
In the context of hal+json CURIEs are simply a URI template that can be used
for each rel that references it.

Embedded Relations
------------------

While links are the primary way to describe relationships between resources, it
is sometimes cumbersome and inefficient to always request them separately. As
an optimization, Chain API will sometimes embed the full related resource in
addition to the link. In this case you will find the embedded resource in the
`_embedded` section of the response, which is a hal+json standard. Note that in
this case the resource will still be linked in the `_links` section with the
same rel name, so clients can ignore the `_embedded` objects if they choose.

Collection Resources
--------------------

Sending an HTTP GET request to a Collection Resource will return a response
with the requested resources as well as metadata about the response, such as
the total number of resources represented by this collection.  If there are
more resources than will fit into a single response, there may also be links to
the first, last, previous, and next pages.

Related Collections
-------------------

When a resource has a related collection (e.g. a parent resource has a
"children" relation), there are several possible ways to represent it.

_Note - this section is pretty speculative, and we probably won't allow the
full flexibility of all these different related collection formats_

### A single link to the collection as a separate resource

```json
{
  "_links": {
    "self": {"href": "/parents/392"},
    "children": {"href": "/parents/392/children/"}
  }
}
```

which when followed gives you a full collection resource:

```json
{
  "_links": {
    "self": {"href": "/parents/392/children/"},
    "next": { "href": "/parents/392/children?page=2", "title": "Page 2" },
    "last": { "href": "/parents/392/children?page=5", "title": "Page 5" },
    "createForm": { "href": "/parents/392/children/", "title": "Create Order"},
    "items": [
      {"href": "/children/382", "title": "Child 1"},
      {"href": "/children/8371", "title": "Child 2"},
      {"href": "/children/716", "title": "Child 3"}
    ]
  }
}
```

or a collection resource with embedded children

```json
{
  "_links": {
    "self": {"href": "/parents/392/children/"},
    "next": { "href": "/parents/392/children?page=2", "title": "Page 2" },
    "last": { "href": "/parents/392/children?page=5", "title": "Page 5" },
    "createForm": { "href": "/parents/392/children/", "title": "Create Order"},
    "items": [
      {"href": "/children/382", "title": "Child 1"},
      {"href": "/children/8371", "title": "Child 2"},
      {"href": "/children/716", "title": "Child 3"}
    ]
  },
  "_embedded": {
    "items": [
      {
        "_links" {
          "self": {"href": "/children/382"}
        },
        "name": "Child 1",
        "age": 13
      },
      {
        "_links" {
          "self": {"href": "/children/8371"}
        },
        "name": "Child 2",
        "age": 16
      },
      {
        "_links" {
          "self": {"href": "/children/716"}
        },
        "name": "Child 3",
        "age": 31
      }
    ]
  }
}
```

### Direct links to each child

This seems fine for small related lists, but doesn't allow pagination links or
metadata about the collection

```json
{
  "_links": {
    "self": {"href": "/parents/392"},
    "children": [
      {"href": "/children/382", "title": "Child 1"},
      {"href": "/children/8371", "title": "Child 2"},
      {"href": "/children/716", "title": "Child 3"}
    ]
  }
}
```

### An embedded collection resource with links

```json
    {
      "_links": {
        "self": {"href": "/parents/392"},
        "children": {"href": "/parents/392/children/"}
      },
      "_embedded": {
        "children": {
          "_links": {
            "self": {"href": "/parents/392/children/"},
            "next": { "href": "/parents/392/children?page=2", "title": "Page 2" },
            "last": { "href": "/parents/392/children?page=5", "title": "Page 5" },
            "createForm": { "href": "/parents/392/children/", "title": "Create Order"},
            "items": [
              {"href": "/children/382", "title": "Child 1"},
              {"href": "/children/8371", "title": "Child 2"},
              {"href": "/children/716", "title": "Child 3"}
            ]
          }
        }
      }
    }
```

### An embedded collection with embedded items

```json
{
  "_links": {
    "self": {"href": "/parents/392"},
    "children": {"href": "/parents/392/children/"}
  },
  "_embedded": {
    "children": {
      "_links": {
        "self": {"href": "/parents/392/children/"},
        "next": { "href": "/parents/392/children?page=2", "title": "Page 2" },
        "last": { "href": "/parents/392/children?page=5", "title": "Page 5" },
        "createForm": { "href": "/parents/392/children/", "title": "Create Order"},
        "items": [
          {"href": "/children/382", "title": "Child 1"},
          {"href": "/children/8371", "title": "Child 2"},
          {"href": "/children/716", "title": "Child 3"}
        ],
        "_embedded": {
          "items": [
            {
            "_links" {
              "self": {"href": "/children/382"}
            },
            "name": "Child 1",
            "age": 13
            },
            {
            "_links" {
              "self": {"href": "/children/8371"}
            },
            "name": "Child 2",
            "age": 16
            },
            {
            "_links" {
              "self": {"href": "/children/716"}
            },
            "name": "Child 3",
            "age": 31
            }
          ]
        }
      }
    }
  }
}
```


hal+json Example
----------------

    GET /orders HTTP/1.1
    Host: example.org
    Accept: application/hal+json

    HTTP/1.1 200 OK
    Content-Type: application/hal+json

    {
      "_links": {
        "self": { "href": "/orders/" },
        "next": { "href": "/orders?page=2", "title": "Page 2" },
        "last": { "href": "/orders?page=5", "title": "Page 5" },
        "createForm": { "href": "/orders/", "title": "Create Order"},
        "curies": [{
            "name": "rel",
            "href": "http://docs.example.com/rels/{rel}",
            "templated": true
        }],
        "items": [
            {"href": "/orders/123", title="Christmas Order"},
            {"href": "/orders/124", title="Birthday Order"},
        ]
      },
      "_embedded": {
        "items": [
        {
          "_links": {
            "self": { "href": "/orders/123" },
            "rel:basket": { "href": "/baskets/98712" },
            "rel:customer": { "href": "/customers/7809" }
          },
          "name": "Christmas Order",
          "total": 30.00,
          "currency": "USD",
          "status": "shipped",
        },
        {
          "_links": {
            "self": { "href": "/orders/124" },
            "rel:basket": { "href": "/baskets/97213" },
            "rel:customer": { "href": "/customers/12369" }
          },
          "name": "Birthday Order",
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

Posting Data
------------

You'll see in the above collection payload a `createForm` rel, which is a link
that you can use to add new elements to the collection. Issuing a GET request
to the `createForm` link will return a document in [JSON-schema][json-schema]
format that tells the client what format the resource should take. POSTing to
the link in the proper format will create a new resource and will return it
with an HTTP 201 Created status.

Editing Data
------------

When the client is able to edit a resource, there will be an `editForm` rel.
As with `createForm`, sending a GET request to this URL will return a
[JSON-schema][json-schema] document. The default values given in the schema are
the current vaues for the resource being edited. POSTing to the URL with the
updated JSON data will update the resource.

Details on the `createForm` and `editForm` rels can be found in
[RFC6861][rfc6861]. Note that, following JSON conventions and to make things
easier on clients, we have modified the standard hyphonated rel names to
camelCase.

The Chain API
=============

Entry Point
-----------

The API entry point is at `http://tidmarsh.media.mit.edu/api/`. A `GET` request
will give you a link to the available sites.

```json
{
  "_links": {
    "self": { "href": "/api" },
    "curies": [{
      "name": "ch",
      "href": "/rels/{rel}",
      "templated": true
    }],
    "ch:sites": {
      "title": "Sites",
      "href": "/sites/"
    }
  }
}
```

Currently the only top-level resource available is the collection of Sites.
The client first selects which site they are interested in and can navigate
from there to explore that site. Clients should not assume hard-coded URIs, but
should instead get the proper URI from the API entry point.

Base Resource Types
===================

NOTE: At some point this information should be moved into the docstrings of
the resources themselves, so we can generate the documentation as well as the
information at the rel URLs from the same info.

Site
----

An installation of Chain API, usually on the scale of several or many
buildings.

### Resource Fields

* `name` (string) - Name of this site
* `geoLocation` (elevation, latitude, longitude) - The geographic location of
  the site. All measurements are in meters.
* `ch:devices` (related resource) - A collection of all the devices in this
  site.  New devices can be POSTed to this collection to add them to this site.

### Example

```json
{
  "_links": {
      "curies": [{
          "name": "ch",
          "href": "/rels/{rel}",
          "templated": true
      }],
      "self": { "href": "/api/sites/92" },
      "ch:devices": {
          "title": "Devices",
          "href": "/api/sites/758/devices"
      }
  },
  "name": "MIT Media Lab",
  "geoLocation": {
    "elevation": 5.8,
    "latitude": 42.360461,
    "longitude": -71.087347
  }
}
```

Device
------

A device that may contain several sensor channels.

### Resource Fields

* `name` (string) - Name of this device
* `ch:site` (related resource) - The site this device is a part of
* `description` (string) - A longer description of this device
* `building` (string) - The building the device is in
* `floor` (string) - The floor of the building
* `room` (string) - The room containing the device
* `ch:sensors` (related resource) - A collection of all the sensors in this
  device. New sensors can be POSTed to this collection to add them to this
  device.

### Example

```json
{
  "_links": {
      "curies": [{
          "name": "ch",
          "href": "/rels/{rel}",
          "templated": true
      }],
      "self": { "href": "/api/devices/929" },
      "ch:sensors": {
          "title": "Sensors",
          "href": "/api/devices/929/sensors"
      },
      "ch:site": {
          "title": "Summer Cabin"
          "href": "/api/sites/928",
      },
  },
  "name": "Bathroom Thermostat",
  "description": "Thermostat in the pool house bathroom",
  "building": "Pool House",
  "floor": "2",
  "room": "Bathroom",
}
```

Sensor
------

A sensor captures a single channel of data. There may be multiple sensors on a
single device. Issuing a GET request for a Sensor resource also includes the
current value for that sensor. The value could be a scalar value or some other
TBD data types.

### Resource Fields

* `ch:device` (related resource) - The device this sensor is part of
* `ch:dataHistory` (related resource) - Collection of data from this sensor
* `metric` (string) - What the sensor is measuring (e.g. "temperature")
* `unit` (string) - The unit the data is in, e.g. "kW-hr". This should be an
  abbreviation from the [QUDT unit list][qudt].
* `dataType` (string) - Data type of this sensor. Currently there's only `float`
* `updated` (ISO8601 timestamp) - Timestamp of the most recent update
* `value` (various) - The most recent reading from this sensor. Currently only
  floating point sensors are supported, but in the future this could be an xyz
  position, GPS coordinate, image, etc.

### Example

```json
{
  "_links": {
      "curies": [{
        "name": "ch",
        "href": "/rels/{rel}",
        "templated": true
      }],
      "self": { "href": "/api/sensors/929" },
      "ch:dataHistory": {
        "title": "History",
        "href": "/api/sensors/929/history"
      },
      "ch:device": {
        "title": "Bathroom Thermostat",
        "href": "/api/devices/928",
      },
  },
  "dataType": "float",
  "value": 23.5,
  "updated": "2014-03-12T13:37:27+00:00",
  "metric": "temperature",
  "unit": "C"
}
```

Sensor Data
-----------

Sensor Data is the raw data captured by the sensors. The `data` field is a list
containing the actual data points. If necessary there are pagination links just
like collection resources. There is also a `createForm` link which gives the
URL to post data to this data set.

### Resource Fields

* `dataType` (string) - The type of the data, currently always "float"
* `data` (list) - List of data, each of which is a JSON object with at least
  a `value` key and a `timestamp` key. The type of the `value` key is determined
  by the `datatype` attribute
* `totalCount` (int) - The total number of data points in the collection. If the
  total count is too large a single response may only have one page of data

### Example

```json
{
  "_links": {
      "self": {"href": "/api/scalar_data/?device=9382"},
      "curies": [{
          "name": "ch",
          "href": "/rels/{rel}",
          "templated": true
      }],
      "createForm": {
          "href": "/api/scalar_data/?device=9382",
          "title": "Add Data"
      }
  },
  "dataType": "float",
  "data": [
    {"value": 23.5, "timestamp": "2014-03-12T13:37:27+00:00"},
    {"value": 23.3, "timestamp": "2014-03-12T13:38:81+00:00"},
    {"value": 22.9, "timestamp": "2014-03-12T13:39:75+00:00"},
    {"value": 22.4, "timestamp": "2014-03-12T13:40:98+00:00"}
  ],
  "totalCount": 4
}
```

Dev Server Initial Setup
========================

To develop for Chain API the best way is with a virtual machine. The following
instructions should guide you through setting up a development environment that
should match the production machine.

First you'll want to make sure that both Virtualbox and Vagrant are installed,
as well as git.

Then clone the code from the repository with:

    git clone https://github.com/ssfrr/chain-api.git

Git will create a folder called chain-api and check out the code into
it.

from within that folder run "vagrant up" and it should instantiate the virtual
machine.

after the machine is up you can run "vagrant ssh" to ssh into the new VM. From
there you can follow the below instructions on setting up a Chain API server.

Chain API Server Setup Instructions
===================================

Currently Chain API is supported on Ubuntu Precise (12.04 LTS)
Install puppet and the proper puppet modules with

    sudo apt-get install rubygems
    sudo gem install puppet -v3.4.3 --no-rdoc --no-ri
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

Copy `localsettings_template.py` into a new file called `localsettings.py`, setting
the username and password, as well as the `SECRET_KEY`. You can generate an
appropriate secret key in python with:

    import random
    ''.join([random.SystemRandom().
        choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
        for i in range(50)])

Then set up the server with

    sudo puppet apply manifest.pp

Now you can initialize your django environment

    ./manage.py syncdb
    ./manage.py migrate

Now you should be able to run the server with:

    ./manage.py runserver 0.0.0.0:8000

and access it from your host machine's browser at

    http://localhost:8000/admin

Setting up for Production
-------------------------

While the above steps should be fine for development, there are a few more
things you need to do for a production machine.

First make sure whatever user will be deploying is in the "staff" group. This will
allow us to autodeploy without needing root permissions.

    sudo usermod -aG staff USERNAME

First install the django app to your system python install by running

    sudo chmod -R g+w /usr/local/bin
    ./setup.py develop

This will install the app as a system package, so you don't need to hard-code
paths.

NOTE - the package is installed WITHOUT root permissions. This is
important because if we install with root permissions the first time then we'll
need root permission on every subsequent time.

Then copy the system config files

    sudo cp -R system/* /

And enable the HTTP interface to supervisor by adding the following code to
the configuration at /etc/supervisor/supervisord.conf (setting the username
and password to whatever you want them to be)

    [inet_http_server]
    port=*:9001
    user=username
    password=password

We also need to change the permissions so that anyone in the "staff" group can
manage supervisor tasks.

    [unix_http_server]
    file=/var/run/supervisor.sock
    chmod=0770
    chown=nobody:staff

Now you can restart supervisord and nginx to pick up the config changes. Note
that supervisor restart doesn't work, so it must be stopped and started.

sudo /etc/init.d/supervisor stop
sudo /etc/init.d/supervisor start
sudo /etc/init.d/nginx restart





[hal]: http://stateless.co/hal_specification.html
[hal-spec]: http://tools.ietf.org/html/draft-kelly-json-hal-06
[rfc6861]: http://tools.ietf.org/html/rfc6861
[rfc5988]: http://tools.ietf.org/html/rfc5988
[rfc1808]: http://tools.ietf.org/html/rfc1808
[curie-w3c]: http://www.w3.org/TR/curie/
[curie-wiki]: http://en.wikipedia.org/wiki/CURIE
[rels-iana]: http://www.iana.org/assignments/link-relations/link-relations.xhtml
[qudt]: http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html
[json-schema]: http://json-schema.org/examples.html
