#!/bin/bash

# Run migrations
python3 -m flask db upgrade

# Start the server
python3 run_prod.py
