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
        'psycopg2==2.5.2',
        'django==1.6.2',
        'django-extensions==1.3.3',
        'django-cors-headers==0.13',
        'south==0.8.4',
        'jinja2==2.7.2',
        'mimeparse==0.1.3',
        'django-debug-toolbar==1.0.1',
        'gunicorn==18.0',
        'chainclient>=0.1',
        'pyzmq==14.1.1',
        'docopt==0.6.1',
        'coloredlogs==0.4.7',
        'gevent==1.0',
        'gevent-websocket==0.9.3',
        'flask==0.10.1',
        'websocket-client==0.12.0',
        'python-dateutil',
    ]
)
