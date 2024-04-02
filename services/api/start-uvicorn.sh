#! /usr/bin/env sh
set -e

# If there's a prestart.sh script in the /app directory or other path specified, run it before starting
PRE_START_PATH=${PRE_START_PATH:-/app/prestart.sh}
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

# Start uvicorn
# https://fastapi.tiangolo.com/deployment/docker/#behind-a-tls-termination-proxy
CMD="uvicorn carlos.api.app:app --proxy-headers --host 0.0.0.0 --port 8000"
echo "Running uvicorn: $CMD"
exec $CMD
