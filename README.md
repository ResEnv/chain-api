Chain API
=========

Update: Slides from my recent workshop at the MIT Media Lab are available here:
http://ssfrr.github.io/ChainDinnerSpring2014/workshop_slides.html

Chain API is a hypermedia HTTP API for working with sensor data. It includes an
HTTP interface supporting request/response interactions, as well as a
Websockets streaming API for realtime "push" updates.

This project is led by [Spencer Russell][ssfrr], in the
[Responsive Environments][resenv] group at the [MIT Media Lab][medialab]. It is
still relatively early stage and in development, and certainly not yet intended
for real production use. It is currently in use for the
[Tidmarsh Living Observatory][tidmarsh] project.

The Chain API is built on top of the [Hypertext Application Language][hal],
or HAL. Currently it only implements the application/hal+json MIME type.
hal+json is relatively simple, and clients are free to ignore HAL and treat the
responses as regular JSON data. There are also various libraries that can
take advantage of the hal+json conventions to abstract some of the details
away. For a more thorough spec of hal+json see [this IETF draft][hal-spec].

We'll start by describing the basic JSON payloads you should expect, but also
be sure to check out the API Concept Overview for more information on the
common themes and design principles driving the API.

Entry Point
-----------

The API entry point is at http://chain-api.media.mit.edu. A `GET` request
will give you a link to the available sites.

```json
{
  "_links": {
    "curies": [
      {
        "href": "http://chain-api.media.mit.edu/rels/{rel}",
        "name": "ch",
        "templated": true
      }
    ],
    "self": {
      "href": "http://chain-api.media.mit.edu/"
    },
    "ch:sites": {
      "href": "http://chain-api.media.mit.edu/sites/",
      "title": "Sites"
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
  "geoLocation": {
    "latitude": 42.360624,
    "elevation": null,
    "longitude": -71.087577
  },
  "_links": {
    "ch:siteSummary": {
      "href": "http://chain-api.media.mit.edu/sites/5/summary",
      "title": "Summary"
    },
    "rawZMQStream": {
      "href": "tcp://tidmarsh.media.mit.edu:1305",
      "title": "Raw ZMQ Stream"
    },
    "ch:devices": {
      "href": "http://chain-api.media.mit.edu/devices/?site_id=5",
      "title": "Devices"
    },
    "curies": [
      {
        "href": "http://chain-api.media.mit.edu/rels/{rel}",
        "name": "ch",
        "templated": true
      }
    ],
    "self": {
      "href": "http://chain-api.media.mit.edu/sites/5"
    },
    "ch:websocketStream": {
      "href": "ws://chain-api.media.mit.edu/ws/site-5",
      "title": "Websocket Stream"
    },
    "editForm": {
      "href": "http://chain-api.media.mit.edu/sites/5/edit",
      "title": "Edit Site"
    }
  },
  "name": "MIT Media Lab"
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
  "building": "E14",
  "room": "Cafe",
  "floor": "5",
  "description": "CityFarm Greenhouse (North)",
  "_links": {
    "ch:site": {
      "href": "http://chain-api.media.mit.edu/sites/5",
      "title": "MIT Media Lab"
    },
    "curies": [
      {
        "href": "http://chain-api.media.mit.edu/rels/{rel}",
        "name": "ch",
        "templated": true
      }
    ],
    "self": {
      "href": "http://chain-api.media.mit.edu/devices/32"
    },
    "ch:websocketStream": {
      "href": "ws://chain-api.media.mit.edu/ws/device-32",
      "title": "Websocket Stream"
    },
    "ch:sensors": {
      "href": "http://chain-api.media.mit.edu/sensors/?device_id=32",
      "title": "Sensors"
    },
    "editForm": {
      "href": "http://chain-api.media.mit.edu/devices/32/edit",
      "title": "Edit Device"
    }
  },
  "name": "0x8123"
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
  "updated": "2014-04-12T20:47:15.291305+00:00",
  "dataType": "float",
  "metric": "temperature",
  "value": 22.32,
  "_links": {
    "ch:dataHistory": {
      "href": "http://chain-api.media.mit.edu/sensordata/?sensor_id=263",
      "title": "Data"
    },
    "curies": [
      {
        "href": "http://chain-api.media.mit.edu/rels/{rel}",
        "name": "ch",
        "templated": true
      }
    ],
    "self": {
      "href": "http://chain-api.media.mit.edu/sensors/263"
    },
    "ch:device": {
      "href": "http://chain-api.media.mit.edu/devices/32",
      "title": "0x8123"
    },
    "ch:websocketStream": {
      "href": "ws://chain-api.media.mit.edu/ws/sensor-263",
      "title": "Websocket Stream"
    },
    "editForm": {
      "href": "http://chain-api.media.mit.edu/sensors/263/edit",
      "title": "Edit Sensor"
    }
  },
  "unit": "celsius"
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
  "dataType": "float",
  "totalCount": 69148,
  "_links": {
    "curies": [
      {
        "href": "http://chain-api.media.mit.edu/rels/{rel}",
        "name": "ch",
        "templated": true
      }
    ],
    "self": {
      "href": "http://chain-api.media.mit.edu/sensordata/?sensor_id=263"
    },
    "first": {
      "href": "http://chain-api.media.mit.edu/sensordata/?sensor_id=263&limit=500&offset=0",
      "title": "0 through 499"
    },
    "createForm": {
      "href": "http://chain-api.media.mit.edu/sensordata/create?sensor_id=263",
      "title": "Add Data"
    },
    "previous": {
      "href": "http://chain-api.media.mit.edu/sensordata/?sensor_id=263&limit=500&offset=68148",
      "title": "68148 through 68647"
    }
  },
  "data": [
    {
      "timestamp": "2014-04-12T15:00:04.202361+00:00",
      "value": 29.81
    },
    {
      "timestamp": "2014-04-12T15:00:25.232755+00:00",
      "value": 29.82
    }
  ]
}
```

General API Concept Overview
============================

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
"children" relation), it will be represented with a collection resource.  The
resource might have "next", "previous", or "last" links to handle pagination.
If the application can add items to the collection, it can have a `createForm`
link. See the section on forms for details.

For instance, the following parent resource has a `children` collection:

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

Rather than the collection only containing links to the items, it may include
the items themselves embedded within the response. If you are using a HAL
client (or chainclient), then it should handle both cases (linked or embedded)
transparently and your application code shouldn't need to care. An example
with embedded items would look like:

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

hal+json Example
----------------

Issuing a GET to /orders might illicit the response:

```json
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
        {"href": "/orders/123", "title": "Christmas Order"},
        {"href": "/orders/124", "title": "Birthday Order"},
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
```

Sending a GET to the URI for a specific resource will return only that
resource, e.g. GET /orders/123 might return:

```json
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
```

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

Websockets Streaming API
------------------------

Many applications are interested in the latest data as it comes in. For these
applications constantly polling is a drain on both the client and server, so
this API implements a streaming interface via [Websockets][websockets]. For
many resources you will find a `ch:websocketStream` link that you can follow
with any websocket-capable browser or client application. Once the websocket
connection is established the server will send HAL+JSON-formatted updates that
typically are the same as what you would receive in a GET response. Streams for
some resources will also include "contained" resources. For instance,
subscribing to the stream for a Site resource might also include all the
devices in that site, and even all the sensors in those devices.

Typically clients will start by synching their current state using the HTTP
API, and maintain a hash that maps resource URLs to the client's internal
representation. After subscribing to a stream, clients can match incoming
resource descriptions by using the `self` link as the key into the hash.


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
Install dependencies with manifest.sh

    cd chain-api/
    sudo chmod +x ./manifest.sh
    sudo ./manifest.sh

NOTE FOR ARCH:

The puppet manifest doesn't work well on Arch, so just install the python
packages with pip system packages with pacman that are listed in the manifest,
and comment those stanzas out.  I also had to set the ownership of
/var/lib/postgres with:

    sudo chown -R postgres:users /var/lib/postgres

END OF ARCH-SPECIFIC NOTE

### Setup Postgres

    sudo su - postgres
    createuser --pwprompt <POSTGRES USERNAME>

after creating a new user, you can create the postgres db like so:

    createdb chain



Copy `localsettings_template.py` into a new file called `localsettings.py`, setting
the username and password, as well as the `SECRET_KEY`. You can generate an
appropriate secret key in python with:

    import random
    ''.join([random.SystemRandom().
        choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
        for i in range(50)])

Then install python dependencies like so:

    ./setup.py develop

Now you can initialise your django environment

    ./manage.py syncdb
    ./manage.py migrate

Now you should be able to run the server with:

    ./manage.py runserver 0.0.0.0:8000

and access it from your host machine's browser at

    http://localhost:8000/admin

Dev Server Vagrant Box Setup
---------------------------
An alternative method to quickly start developing with chain-api on Ubuntu 12.04 Wheezy64 Vagrant Box

    curl -o package.box http://phive-yogurt.mit.edu/chain-ubuntu1404.box
    vagrant box add chain-box package.box
    vagrant init chain-box
    vagrant up
    vagrant ssh

default postgres username/password:

    username: yoda
    password: 123

default http username/password:

    username: yoda
    password: 123

Make sure to change the username/password and edit localsettings.py

Supervisor and Nginx are setup to run automatically, but you will have to run the following first.

    cd /vagrant
    sudo ./setup.py develop
    sudo chmod -R g+wx-s /usr/local /srv
    sudo chmod -R a+r /usr/local

Then restart supervisor and nginx:

    sudo /etc/init.d/supervisor stop
    sudo /etc/init.d/supervisor start
    sudo /etc/init.d/nginx restart


Setting up for Production
-------------------------

While the above steps should be fine for development, there are a few more
things you need to do for a production machine.

First make sure whatever user will be deploying is in the "staff" group. This will
allow us to autodeploy without needing root permissions.

    sudo usermod -aG staff USERNAME
    sudo chown -R root:staff /usr/local /srv
    sudo chmod -R g+wx-s /usr/local /srv
    sudo chmod -R a+r /usr/local

First install the django app to your system python install by running

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

Now create the htpasswd file that will determine the usernames and passwords
that will be allowed to POST to your ChainAPI Instance:

    sudo htpasswd -c /var/www/mywebsite.com/.htpasswd exampleuser

and edit /etc/nginx/sites-available/chain.conf to add the path to your
.htpasswd file where it says `PATH/TO/HTPASSWD`.

Now you can restart supervisord and nginx to pick up the config changes. Note
that supervisor restart doesn't work, so it must be stopped and started.

    sudo /etc/init.d/supervisor stop
    sudo /etc/init.d/supervisor start
    sudo /etc/init.d/nginx restart

Deploy Hooks
------------

In the "hooks" directory you'll find a post-receive hook that should be copied
(or symlinked) into the .git/hooks directory of your deployed server. You'll also
need to run

    git config receive.denyCurrentBranch ignore

To allow pushes to the checked-out branch.

On your development machine you should now be able to set up the deployment server as a
git remote

    git remote add production ssh://deployuser@yourserver.com/deployed/repo/dir

then whenever you have a version to push to production just:

    git push production



[ssfrr]: http://ssfrr.com
[resenv]: http://resenv.media.mit.edu
[medialab]: http://media.mit.edu
[tidmarsh]: http://tidmarsh.media.mit.edu
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
[websockets]: http://en.wikipedia.org/wiki/WebSocket
