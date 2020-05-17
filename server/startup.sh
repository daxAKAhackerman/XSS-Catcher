#!/bin/bash

python3 -m flask db upgrade
python3 -c "import app; tmpapp = app.create_app(); app.models.create_first_user(tmpapp)"
waitress-serve --call 'xss:create_app'

