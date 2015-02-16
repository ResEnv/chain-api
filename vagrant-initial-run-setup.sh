#!/bin/bash

# This script should be run when the vagrant box is first initialized.
# It performs the final initialization necessary to run ChainAPI

ORIGIN=$(pwd)
cd /vagrant

if [ ! -e ./chain/localsettings.py ]
  then
	echo "localsettings configuration file does not exist.  Creating one with vagrant defaults."
	cp ./chain/localsettings_vagrant.py ./chain/localsettings.py
fi

sudo su - postgres -c 'psql -c "ALTER USER yoda WITH SUPERUSER;"'
sudo ./setup.py develop
sudo ./manage.py migrate
yes yes | sudo ./manage.py collectstatic
sudo chmod -R g+wx-s /usr/local /srv
sudo chmod -R a+r /usr/local

sleep 2
sudo /etc/init.d/supervisor stop
sudo /etc/init.d/supervisor start
sudo /etc/init.d/nginx restart
cd $ORIGIN
