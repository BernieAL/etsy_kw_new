#!/bin/bash

# Exit on error
set -e

# Create temporary directories
mkdir -p build/lambda/scraper_worker
mkdir -p build/lambda/email_worker

# Install dependencies for scraper worker
echo "Installing scraper worker dependencies..."
pip install -r src/lambda/requirements.txt -t build/lambda/scraper_worker/python/

# Remove unnecessary files to reduce package size
echo "Cleaning up scraper worker dependencies..."
find build/lambda/scraper_worker/python -type d -name "tests" -exec rm -rf {} +
find build/lambda/scraper_worker/python -type d -name "__pycache__" -exec rm -rf {} +
find build/lambda/scraper_worker/python -type d -name "test" -exec rm -rf {} +
find build/lambda/scraper_worker/python -type d -name "docs" -exec rm -rf {} +
find build/lambda/scraper_worker/python -type f -name "*.pyc" -delete
find build/lambda/scraper_worker/python -type f -name "*.pyo" -delete

# Copy scraper worker code
echo "Copying scraper worker code..."
cp src/lambda/scraper_worker/lambda_function.py build/lambda/scraper_worker/
cp -r src/common build/lambda/scraper_worker/

# Create scraper worker layer
echo "Creating scraper worker layer..."
cd build/lambda/scraper_worker
zip -r ../../../lambda/scraper_worker/layer.zip python/
zip -r ../../../lambda/scraper_worker/function.zip lambda_function.py common/

# Install dependencies for email worker
echo "Installing email worker dependencies..."
cd ../../..
pip install boto3 python-dotenv -t build/lambda/email_worker/python/

# Copy email worker code
echo "Copying email worker code..."
cp src/lambda/email_worker/lambda_function.py build/lambda/email_worker/
cp -r src/common build/lambda/email_worker/
cp -r src/workers/email_worker/email_builder.py build/lambda/email_worker/

# Create email worker layer
echo "Creating email worker layer..."
cd build/lambda/email_worker
zip -r ../../../lambda/email_worker/layer.zip python/
zip -r ../../../lambda/email_worker/function.zip lambda_function.py common/ email_builder.py

# Clean up
cd ../../..
rm -rf build

echo "Lambda functions packaged successfully!" 