Notes on docker configuration:

(these notes don't apply to the images here built by Ken, they're my(spencer's)
notes about how we might organize our docker config as I learn more about it.)

## General notes and ideas

* alpine linux seems like a good base image, it's super small
* see the `alpine-python` image (https://github.com/jfloff/alpine-python) for
  some good examples
* use `dumb-init` or `tini` as an init process to handle zombie processes and signals
* volume-only containers shouldn't be necessary now that there are named volumes
  some good info here: https://boxboat.com/2016/06/18/docker-data-containers-and-named-volumes/
* we'll want to mount the current directory inside the container so we can develop
  on our host machine and not need to re-build the image every time. Probably mount it read-only
* one big question is - how many containers?
* it looks like we could run supervisord inside a container. still want to use an `init`
  process though.
* if we run multiple processes we need to figure out how to deal with logs

## Processes we need to run
* postgres
* chain webserver
* flask webserver
* collector scripts

## Image Build-time Steps

1. Start with basic alpine image
2. Install APK packages (python, etc.)
3. install any pip packages needed to bootstrap `setup.py`
3. run `setup.py develop` to install dependencies and chain package

## Container Init Steps

## Configuration

* Inter-process config (e.g. port numbers, postgres password)
* Other config/secrets (e.g. admin password)

## User steps (WIP)
1. install docker
2. create a named volume that will hold the data: `docker volume create --name chain_dbdata`
3. to run a container that accesses that data use the `-v chain_dbdata:/var/lib/postgresql`.
   you can have multiple versions of the database with different names if you want

## Deployment
