#!/bin/bash

# Create temporary directories
mkdir -p temp/scraper_worker_pkg
mkdir -p temp/email_worker_pkg
mkdir -p temp/scraper_layer/python
mkdir -p temp/pandas_layer/python

# Install core dependencies for scraper worker (lightweight)
pip install --target temp/scraper_worker_pkg boto3

# Install selenium dependencies in the main layer
pip install --target temp/scraper_layer/python selenium-wire undetected-chromedriver

# Install pandas in a separate layer
pip install --target temp/pandas_layer/python pandas

# Install dependencies for email worker
pip install --target temp/email_worker_pkg boto3

# Copy Lambda function code
cp src/workers/scraper_worker/lambda_function.py temp/scraper_worker_pkg/
cp src/workers/email_worker/lambda_function.py temp/email_worker_pkg/

# Get absolute paths for PowerShell
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

# Create source and destination paths for PowerShell
SCRAPER_PKG_PATH=$(cygpath -w "${PROJECT_DIR}/temp/scraper_worker_pkg")
EMAIL_PKG_PATH=$(cygpath -w "${PROJECT_DIR}/temp/email_worker_pkg")
SCRAPER_LAYER_PATH=$(cygpath -w "${PROJECT_DIR}/temp/scraper_layer/python")
PANDAS_LAYER_PATH=$(cygpath -w "${PROJECT_DIR}/temp/pandas_layer/python")

SCRAPER_ZIP_PATH=$(cygpath -w "${PROJECT_DIR}/src/workers/scraper_worker/lambda_function.zip")
EMAIL_ZIP_PATH=$(cygpath -w "${PROJECT_DIR}/src/workers/email_worker/lambda_function.zip")
SCRAPER_LAYER_ZIP_PATH=$(cygpath -w "${PROJECT_DIR}/src/workers/scraper_worker/layer.zip")
PANDAS_LAYER_ZIP_PATH=$(cygpath -w "${PROJECT_DIR}/src/workers/scraper_worker/pandas_layer.zip")

# Create zip files using PowerShell with proper Windows paths
powershell -Command "Compress-Archive -Path \"${SCRAPER_PKG_PATH}\\*\" -DestinationPath \"${SCRAPER_ZIP_PATH}\" -Force"
powershell -Command "Compress-Archive -Path \"${EMAIL_PKG_PATH}\\*\" -DestinationPath \"${EMAIL_ZIP_PATH}\" -Force"
powershell -Command "Compress-Archive -Path \"${SCRAPER_LAYER_PATH}\\*\" -DestinationPath \"${SCRAPER_LAYER_ZIP_PATH}\" -Force"
powershell -Command "Compress-Archive -Path \"${PANDAS_LAYER_PATH}\\*\" -DestinationPath \"${PANDAS_LAYER_ZIP_PATH}\" -Force"

# Cleanup
rm -rf temp

echo "Lambda deployment packages and layers created successfully!" 