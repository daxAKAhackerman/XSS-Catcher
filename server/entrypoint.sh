#!/bin/bash

# Run migrations
python3.13 -m flask db upgrade

# Start the server
python3.13 run_prod.py
