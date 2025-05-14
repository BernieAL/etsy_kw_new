#!/bin/bash

# Exit on error
set -e

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Function to package Lambda
package_lambda() {
    local worker_dir=$1
    local output_zip=$2
    
    echo "Packaging $worker_dir..."
    
    # Create a new virtual environment
    python -m venv "$TEMP_DIR/venv"
    source "$TEMP_DIR/venv/bin/activate"
    
    # Install dependencies
    pip install -r "$worker_dir/requirements.txt"
    
    # Copy Lambda function
    cp "$worker_dir/lambda_function.py" "$TEMP_DIR/"
    
    # Install Chrome if it's the scraper worker
    if [[ $worker_dir == *"scraper_worker"* ]]; then
        # Install Chrome
        curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        dpkg -i google-chrome-stable_current_amd64.deb || true
        apt-get install -f -y
        
        # Install Chrome dependencies
        apt-get install -y \
            libxss1 \
            libappindicator1 \
            libindicator7 \
            fonts-liberation \
            libasound2 \
            libatk-bridge2.0-0 \
            libatk1.0-0 \
            libatspi2.0-0 \
            libcups2 \
            libdbus-1-3 \
            libdrm2 \
            libgbm1 \
            libgtk-3-0 \
            libnspr4 \
            libnss3 \
            libx11-xcb1 \
            libxcb1 \
            libxcomposite1 \
            libxdamage1 \
            libxext6 \
            libxfixes3 \
            libxrandr2 \
            xdg-utils
    fi
    
    # Create deployment package
    cd "$TEMP_DIR"
    zip -r "$output_zip" .
    
    # Clean up
    deactivate
    rm -rf "$TEMP_DIR/venv"
}

# Package scraper worker
package_lambda "src/workers/scraper_worker" "scraper_worker.zip"

# Package email worker
package_lambda "src/workers/email_worker" "email_worker.zip"

# Clean up
rm -rf "$TEMP_DIR"

echo "Lambda functions packaged successfully!" 