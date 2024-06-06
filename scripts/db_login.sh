#!/bin/bash

CONTAINER_ID=$(docker ps -aqf "name=^mtgdb$")

docker exec -it $CONTAINER_ID bash -c 'psql -d mtgdb -U mtguser'
