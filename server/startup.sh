#!/bin/bash

OLD_PASSWORD=FvzZ0a1mxfWWRp9gAeml

if [ "$POSTGRES_PASSWORD" != "$OLD_PASSWORD" ]; then
    psql -d "postgresql://$POSTGRES_USER:$OLD_PASSWORD@db/$POSTGRES_DB" -c "\q"

    if [ $? -eq 0 ]; then
        psql -d "postgresql://$POSTGRES_USER:$OLD_PASSWORD@db/$POSTGRES_DB" -c "ALTER USER $POSTGRES_USER WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';"
    fi

fi

python3 -m flask db upgrade
python3 -c "import app; tmpapp = app.create_app(); app.models.init_app(tmpapp)"
waitress-serve --call 'xss:create_app'

