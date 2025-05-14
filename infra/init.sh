#!/bin/bash
set -e

# Install Docker and dependencies
apt-get update -y && apt-get install -y docker.io awscli git
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# Usage: Set AWS_ACCOUNT_ID before running this script
# export AWS_ACCOUNT_ID=058135280735

# Login to ECR
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS \
  --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

# Clone repo or pull docker-compose.yml if not already included in AMI
cd /home/ubuntu/app  # or wherever your compose file is located

# Pull and run containers
docker compose -f docker-compose.ec2.yml pull
docker compose -f docker-compose.ec2.yml up -d
