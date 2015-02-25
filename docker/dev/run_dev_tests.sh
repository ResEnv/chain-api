#!/bin/bash

sudo docker run -i -t -v "$(pwd)/../../:/opt/chain-api-dev" chain/dev /opt/test-chain
