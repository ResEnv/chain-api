# NOTE: this dockerfile assumes the context directory is the root of the
# repository, so it should be run using the `-f` flag.

# Runs chain webserver on port 8080 within docker image
FROM ubuntu:14.04

MAINTAINER Ken Leidal version: 0.0.1

EXPOSE 8080

ENV CHAIN_HOME /opt/chain-api

RUN apt-get update && apt-get -y install git build-essential
COPY . /opt/chain-api
RUN /opt/chain-api/manifest.sh
RUN cp /opt/chain-api/chain/localsettings_vagrant.py /opt/chain-api/chain/localsettings.py
RUN cd /opt/chain-api/ && ./setup.py develop && cd -
RUN /opt/chain-api/docker/base/install-chain
COPY docker/base/start-chain docker/base/test-chain /opt/
