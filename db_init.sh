#!/bin/bash

# psql -c "CREATE USER mtguser WITH PASSWORD 'dev'"
# psql -c "CREATE DATABASE mtgdb"
# psql -c "GRANT ALL PRIVILEGES ON DATABASE mtgdb TO mtguser"
# psql -c "ALTER USER mtguser WITH SUPERUSER"

echo "Initializing database"
cd base_schema
PGPASSWORD=dev psql -d mtgdb -U mtguser -f db_setup.sql
cd ..
