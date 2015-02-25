#!/bin/bash

sudo docker run -d -p 8000:8000 -p 9001:9001 -p 8080:80 --volumes-from chain_data chain/base /opt/start-chain
