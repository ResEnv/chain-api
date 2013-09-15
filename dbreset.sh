#!/bin/bash

# this script is for early development where the DB schema isn't yet settled
# and there's no data worth keeping in the DB. It clears the DB (including all
# tables), removes the initial migration for core, then regenerates the initial
# migration and the DB tables

./manage.py sqlclear core tastypie south | ./manage.py dbshell
rm -f doppel2/core/migrations/0001_initial.py*
./manage.py syncdb
./manage.py schemamigration --init core
./manage.py migrate
