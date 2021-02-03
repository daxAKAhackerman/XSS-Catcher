#!/bin/bash

OLD_PASSWORD=FvzZ0a1mxfWWRp9gAeml

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "[!] POSTGRES password is not set. Did you run 'make deploy'?"
    exit
fi

if [ "$POSTGRES_PASSWORD" != "$OLD_PASSWORD" ]; then
    psql -d "postgresql://$POSTGRES_USER:$OLD_PASSWORD@$POSTGRES_HOSTNAME/$POSTGRES_DB" -c "\q" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        psql -d "postgresql://$POSTGRES_USER:$OLD_PASSWORD@$POSTGRES_HOSTNAME/$POSTGRES_DB" -c "ALTER USER \"$POSTGRES_USER\" WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';"
    fi

fi

python3 -m flask db upgrade
python3 -c "import app; tmpapp = app.create_app(); app.models.init_app(tmpapp)"
waitress-serve --call 'xss:create_app'

