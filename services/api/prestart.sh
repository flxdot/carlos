#!/bin/bash

# This script is used to run any migrations or other setup tasks before the app starts.

# let the database start
sleep 10
# Run the migration script
python -m carlos.database.migration