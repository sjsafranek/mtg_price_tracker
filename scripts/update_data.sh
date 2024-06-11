#!/bin/bash


# Settings
FILE="data/prices.csv"
MAX_AGE="14400"


# Build dataset if file does not exist.
# If file exists, check file age.
if [ ! -f "$FILE" ] || [ "$(( $(date +"%s") - $(stat -c "%Y" "$FILE") ))" -gt "$MAX_AGE" ]; then

	echo "Building new dataset"
   	NEW_FILE=$(python build.py)

   	echo "$NEW_FILE"

   	# Check if new file was created
   	if [ -f "$NEW_FILE" ]; then
   		cp "$NEW_FILE" "$FILE"

   		echo "Uploading data to database"
		CONTAINER_ID=$(docker ps -aqf "name=^mtgdb$")
		docker exec -it $CONTAINER_ID bash -c 'psql -d mtgdb -U mtguser -f /scripts/load_data.sql'
	fi

fi


# for FILE in data/prices_*.csv; do
# 	echo "Uploading $FILE to database"
# 	cp $FILE "data/prices.csv"
# 	CONTAINER_ID=$(docker ps -aqf "name=^mtgdb$")
# 	docker exec -it $CONTAINER_ID bash -c 'psql -d mtgdb -U mtguser -f /scripts/load_data.sql'	
# done

