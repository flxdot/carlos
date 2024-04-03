#!/bin/bash
# takes two paramters, the domain name and the email to be associated with the certificate
DOMAIN=$1
EMAIL=$2

echo DOMAIN=${DOMAIN}
echo EMAIL=${EMAIL}

# Phase 1
docker-compose -f /carlos/deployment/server/docker-compose-initiate.yml --env-file /carlos/.env up -d nginx
docker-compose -f /carlos/deployment/server/docker-compose-initiate.yml --env-file /carlos/.env up certbot
docker-compose -f /carlos/deployment/server/docker-compose-initiate.yml --env-file /carlos/.env down

# some configurations for let's encrypt
curl -L --create-dirs -o /carlos/.carlos_data/letsencrypt/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf
openssl dhparam -out /carlos/.carlos_data/letsencrypt/ssl-dhparams.pem 2048

# Phase 2
crontab /carlos/deployment/server/crontab
docker-compose -f /carlos/deployment/server/docker-compose.yml --env-file /carlos/.env -d up