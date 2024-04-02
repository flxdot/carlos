#!/bin/sh

echo "Processing env file"
sed -i '/VITE_APP_API_URL:/c\    VITE_APP_API_URL: "'"$VITE_APP_API_URL"'",' config.js

echo "Starting"
exec "$@"
