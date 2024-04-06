#!/bin/bash

# This script will update the code to the latest available version and restart it

cd /carlos && git pull

docker-compose -f /carlos/deployment/server/docker-compose.yml --env-file /carlos/.env down
docker-compose -f /carlos/deployment/server/docker-compose.yml --env-file /carlos/.env up --build --detach
