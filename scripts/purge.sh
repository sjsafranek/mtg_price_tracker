#!/bin/bash

echo "Removing docker container"
CONTAINER_ID=$(docker ps -aqf "name=^mtgdb$")
docker container rm $CONTAINER_ID

echo "Removing docker image"
IMAGE_ID=$(docker images -q "mtg_price_tracker-mtgdb")
docker image rm $IMAGE_ID

echo "Removing docker volume"
rm -rf docker_volumes/*