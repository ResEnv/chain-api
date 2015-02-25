# Runs chain webserver on port 8080 within docker image
FROM ubuntu:14.04

MAINTAINER Ken Leidal version: 0.0.1

EXPOSE 8080

ENV CHAIN_HOME /opt/chain-api

RUN apt-get update && apt-get -y install git build-essential
RUN git clone https://github.com/ssfrr/chain-api.git /opt/chain-api 
RUN chmod +x /opt/chain-api/manifest.sh && sleep 2 && /opt/chain-api/manifest.sh
RUN cp /opt/chain-api/chain/localsettings_vagrant.py /opt/chain-api/chain/localsettings.py
RUN cd /opt/chain-api/ && ./setup.py develop && cd -
ADD install-chain /opt/
RUN chmod +x /opt/install-chain && sleep 2 && /opt/install-chain
ADD startup start-chain test-chain /opt/
RUN chmod +x /opt/startup /opt/start-chain /opt/test-chain && sleep 2
