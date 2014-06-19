#!/usr/bin/env python

from setuptools import setup

setup(
    name='chain-api',
    version='0.0.3',
    description='RESTful Sensor API based on HAL+JSON',
    py_packages=['chain', 'flask-sockets'],
    scripts=['collectors/tidpost',
             'collectors/thermpost',
             'scripts/chainsocketpolicyd'],
    author='Spencer Russell',
    author_email='sfr@mit.edu',
    url='http://github.com/ssfrr/chain-api',
    license='MIT',
    install_requires=[
        'psycopg2',
        'django',
        'django-extensions',
        'south',
        'jinja2',
        'mimeparse',
        'django-debug-toolbar',
        'gunicorn',
        'chainclient>=0.1',
        'pyzmq',
        'docopt',
        'coloredlogs',
        'gevent',
        'gevent-websocket',
        'flask',
        'websocket-client',
        'python-dateutil',
    ]
)
