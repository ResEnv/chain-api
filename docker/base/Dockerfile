# NOTE: this dockerfile assumes the context directory is the root of the
# repository, so it should be run using the `-f` flag.

FROM ubuntu:18.04
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV DEBIAN_FRONTEND=noninteractive
# install sudo, which isn't included in the 18.04 image. We need this to be
# able to run the included manifest.sh
# see https://github.com/tianon/docker-brew-ubuntu-core/issues/48#issuecomment-215522746
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

MAINTAINER Ken Leidal version: 0.0.1

# Runs chain webserver on port 8080 within docker image
EXPOSE 8080

ENV CHAIN_HOME /opt/chain-api

RUN apt-get update && apt-get -y install git build-essential
COPY . /opt/chain-api
RUN /opt/chain-api/manifest.sh
RUN cp /opt/chain-api/chain/localsettings_vagrant.py /opt/chain-api/chain/localsettings.py
RUN cd /opt/chain-api/ && ./setup.py develop && cd -
# setuptools doesn't support installing scripts that have non-ascii characters,
# so we need to install this one manually
COPY collectors/tidpost /usr/local/bin
RUN /opt/chain-api/docker/base/install-chain
COPY docker/base/start-chain docker/base/test-chain /opt/
