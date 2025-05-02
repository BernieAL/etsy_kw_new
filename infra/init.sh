#!/bin/bash

# Update & install Docker + Compose
apt update
apt install -y docker.io docker-compose git

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Optional: auto-start Docker (should already be enabled)
systemctl enable docker

# Optional: clone your app if it's on GitHub (change as needed)
# cd /home/ubuntu
# git clone https://github.com/yourname/your-app.git
# cd your-app
# docker-compose up -d

