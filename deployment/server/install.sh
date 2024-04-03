#!/bin/bash
# takes two paramters, the domain name and the email to be associated with the certificate
DOMAIN=$1
EMAIL=$2

echo DOMAIN=${DOMAIN}
echo EMAIL=${EMAIL}

# Phase 1
docker-compose -f ./deployment/server/docker-compose-initiate.yaml --env /carlos/.env up -d nginx
docker-compose -f ./deployment/server/docker-compose-initiate.yaml --env /carlos/.env up certbot
docker-compose -f ./deployment/server/docker-compose-initiate.yaml --env /carlos/.env down

# some configurations for let's encrypt
curl -L --create-dirs -o ./.carlos_data/letsencrypt/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf
openssl dhparam -out ./.carlos_data/letsencrypt/ssl-dhparams.pem 2048

# Phase 2
crontab ./deployment/server/crontab
docker-compose -f ./deployment/server/docker-compose.yaml --env /carlos/.env -d up