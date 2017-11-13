#!/bin/bash

docker run -i -t -v "$(pwd)/../../:/opt/chain-api-dev" chain/dev /opt/test-chain
