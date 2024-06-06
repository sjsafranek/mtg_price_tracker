FROM timescale/timescaledb:latest-pg16

MAINTAINER Stefan Safranek, sjsafranek@gmail.com

RUN apk update

COPY base_schema /base_schema

COPY db_init.sh /docker-entrypoint-initdb.d/db_init.sh
RUN chown root:root /docker-entrypoint-initdb.d/db_init.sh && \
    chmod 4755 /docker-entrypoint-initdb.d/db_init.sh