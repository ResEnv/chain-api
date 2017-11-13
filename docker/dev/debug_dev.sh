#!/bin/bash

docker run -i -t -p 8000:8000 -p 9001:9001 -p 8080:80 -v "$(pwd)/../../:/opt/chain-api-dev" chain/dev bash
