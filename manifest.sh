#!/bin/bash

#NGINX WebSockets Proxying
if grep "nginx" /etc/apt/sources.list > /dev/null
then
	sudo apt-get update
else
	echo 'deb http://nginx.org/packages/ubuntu/ precise nginx' | sudo tee -a /etc/apt/sources.list
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ABF5BD827BD9BF62
	sudo apt-get update
fi

#Reconfigure Locales or an error will popup when installing new packages
sudo locale-gen en_US en_US.UTF-8 de_AT.UTF-8
sudo dpkg-reconfigure locales

#Packages
sudo apt-get --yes --force-yes install python-dev libpq-dev python-pip
sudo apt-get --yes --force-yes install nginx
sudo apt-get --yes --force-yes install supervisor
sudo apt-get --yes --force-yes install apache2-utils
sudo apt-get --yes --force-yes install postgresql postgresql-contrib
sudo apt-get --yes --force-yes install libzmq-dev

#Postgres setup
#su – postgres
#createuser --pwprompt
#createdb chain;
#./setup.py develop
#./manage.py syncdb
#./manage.py migrate
#./manage.py runserver 0.0.0.0:8000
