#!/bin/bash

# This script is used to update the deployed server
docker-compose -f /carlos/deployment/server/docker-compose.yml --env-file /carlos/.env down
docker-compose -f /carlos/deployment/server/docker-compose.yml --env-file /carlos/.env up --build --detach
