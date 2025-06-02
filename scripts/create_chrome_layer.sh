#!/bin/bash

# Exit on error
set -e

# Create temporary directory
mkdir -p build/chrome_layer

# Download Chrome binary
echo "Downloading Chrome binary..."
curl -L https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm -o build/chrome_layer/chrome.rpm

# Create Lambda layer structure
mkdir -p lambda/chrome_layer/opt/chrome

# Extract Chrome binary
echo "Extracting Chrome binary..."
cd build/chrome_layer
rpm2cpio chrome.rpm | cpio -idmv
cd ../..

# Copy Chrome binary and dependencies
echo "Copying Chrome files..."
cp build/chrome_layer/opt/google/chrome/chrome lambda/chrome_layer/opt/chrome/
cp build/chrome_layer/opt/google/chrome/*.so* lambda/chrome_layer/opt/chrome/

# Create layer zip
echo "Creating layer zip..."
cd lambda/chrome_layer
zip -r ../chrome_layer.zip .
cd ../..

# Clean up
rm -rf build

echo "Chrome Lambda layer created successfully!" 