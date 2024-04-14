#!/bin/sh

echo "Processing env file"
sed -i '/VITE_APP_API_URL:/c\    VITE_APP_API_URL: "'"$VITE_APP_API_URL"'",' config.js
sed -i '/VITE_AUTH0_DOMAIN:/c\    VITE_AUTH0_DOMAIN: "'"$VITE_AUTH0_DOMAIN"'",' config.js
sed -i '/VITE_AUTH0_CLIENT_ID:/c\    VITE_AUTH0_CLIENT_ID: "'"$VITE_AUTH0_CLIENT_ID"'",' config.js
sed -i '/VITE_AUTH0_AUDIENCE:/c\    VITE_AUTH0_AUDIENCE: "'"VITE_AUTH0_AUDIENCE"'",' config.js
sed -i '/VITE_SENTRY_DSN:/c\    VITE_SENTRY_DSN: "'"$VITE_SENTRY_DSN"'",' config.js
sed -i '/VITE_SENTRY_ENVIRONMENT:/c\    VITE_SENTRY_ENVIRONMENT: "'"$VITE_SENTRY_ENVIRONMENT"'",' config.js

echo "Starting"
exec "$@"
