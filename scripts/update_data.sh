#!/bin/bash


# Settings
FILE="data/prices.csv"
MAX_AGE="14400"


# Build dataset if file does not exist.
# If file exists, check file age.
if [ ! -f "$FILE" ] || [ "$(( $(date +"%s") - $(stat -c "%Y" "$FILE") ))" -gt "$MAX_AGE" ]; then

	echo "Building new dataset"
   	python build.py

   	echo "Uploading data to database"
	CONTAINER_ID=$(docker ps -aqf "name=^mtgdb$")
	docker exec -it $CONTAINER_ID bash -c 'psql -d mtgdb -U mtguser -f /scripts/load_data.sql'
	
fi