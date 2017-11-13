#!/bin/bash

sudo apt-get --yes --force-yes install curl apt-transport-https
# set up environment variables useful for adding sources.list.d entries
source /etc/lsb-release

#NGINX WebSockets Proxying
if [ ! -e /etc/apt/sources.list.d/nginx.list ]
then
	echo "deb http://nginx.org/packages/ubuntu/ ${DISTRIB_CODENAME} nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ABF5BD827BD9BF62
fi

# influxdb
if [ ! -e /etc/apt/sources.list.d/influxdb.list ]
then
	curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
	echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
fi

sudo apt-get update

#Reconfigure Locales or an error will popup when installing new packages
sudo locale-gen en_US en_US.UTF-8 de_AT.UTF-8
sudo dpkg-reconfigure locales

#Packages
sudo apt-get --yes --force-yes install python-dev libpq-dev python-pip
sudo apt-get --yes --force-yes install nginx
sudo apt-get --yes --force-yes install influxdb
sudo apt-get --yes --force-yes install supervisor
sudo apt-get --yes --force-yes install apache2-utils
sudo apt-get --yes --force-yes install postgresql postgresql-contrib
# sudo apt-get --yes --force-yes install libzmq-dev

#Postgres setup
#su – postgres
#createuser --pwprompt
#createdb chain;
#./setup.py develop
#./manage.py syncdb
#./manage.py migrate
#./manage.py runserver 0.0.0.0:8000
