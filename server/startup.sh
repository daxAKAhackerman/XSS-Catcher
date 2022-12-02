#!/bin/bash

if [[ -f "app.db" ]]; then
    pg_password=$(head -n 1 $POSTGRES_PASSWORD_FILE)
    pgloader sqlite:///app.db pgsql://$POSTGRES_USER:$pg_password@$POSTGRES_HOSTNAME/$POSTGRES_DB
fi

python3 -m flask db upgrade
python3 -c "import app; tmpapp = app.create_app(); app.models.init_app(tmpapp)"
waitress-serve --call 'xss:create_app'
