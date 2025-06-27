#!/bin/bash

# Development server script for hot reloading
echo "Starting development server with hot reload..."
echo "API will be available at http://localhost:8000"
echo "Press Ctrl+C to stop"

# Start uvicorn with reload enabled
uvicorn api.monitoring_api:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app 