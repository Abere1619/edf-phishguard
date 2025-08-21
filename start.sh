#!/bin/bash

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery Worker..."
    celery -A tasks worker --loglevel=info
else
    echo "Starting FastAPI Server..."
    uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
fi
