#!/bin/bash

pg_password=$(head -n 1 $POSTGRES_PASSWORD_FILE)
pgloader sqlite://./database-backup.db pgsql://$POSTGRES_USER:$pg_password@$POSTGRES_HOSTNAME/$POSTGRES_DB
