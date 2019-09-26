#!/bin/bash

docker pull zardus/research:cyborg && \
docker build -t "zardus/research:cyborg-generator" --build-arg CACHEBUST=`date +%s` . && \
docker push zardus/research:cyborg-generator
