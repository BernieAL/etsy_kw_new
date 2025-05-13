#!/bin/bash

echo "🔐 Authenticating with ECR..."
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS \
  --password-stdin 058135280735.dkr.ecr.us-east-1.amazonaws.com

set -euo pipefail

# This script finds all Dockerfiles, builds, tags, and pushes them to ECR.

export GIT_PS1_SHOWCONFLICTSTATE=${GIT_PS1_SHOWCONFLICTSTATE:-}

# Get the directory of the script
script_dir="$(cd "$(dirname "$0")" && pwd)"

# Set root of the project (assumes this script is in /scripts)
project_root="$script_dir/.."

# ECR repository base and name
ecr_base="058135280735.dkr.ecr.us-east-1.amazonaws.com"
repo_name="etsy-analyzer"

echo "📦 Scanning for Dockerfiles in: $project_root"

# Create single ECR repository if it doesn't exist
if ! aws ecr describe-repositories --repository-name "$repo_name" --region us-east-1 >/dev/null 2>&1; then
    echo "📦 Creating ECR repository: $repo_name"
    aws ecr create-repository --repository-name "$repo_name" --region us-east-1
fi

# Find all Dockerfiles (excluding node_modules or other junk)
find "$project_root" -type f -name 'Dockerfile*' ! -path '*/node_modules/*' | while read dockerfile; do
  echo "📄 Found Dockerfile: $dockerfile"

  service_dir=$(dirname "$dockerfile")
  dockerfile_name=$(basename "$dockerfile")
  service_name=$(basename "$service_dir")
  echo "DEBUG: service_name=$service_name"

  if [[ "$dockerfile_name" == "Dockerfile.client" ]]; then
    echo "skipping $dockerfile"
    continue
  fi

  # For services in src directory, use src as build context
  if [[ "$service_dir" == *"/src/"* ]]; then
    build_context="$project_root/src"
    # Get the relative path from src to the service directory
    service_rel_path="${service_dir#$build_context/}"
    # The Dockerfile path should be relative to the build context
    dockerfile_path="$service_rel_path/$dockerfile_name"
  else
    build_context="$project_root"
    dockerfile_path="$dockerfile"
  fi

  # Tag with service name
  image_name="$ecr_base/$repo_name:$service_name"
  echo "🔨 Building image for $image_name from context: $build_context..."
  echo "📄 Using Dockerfile: $dockerfile_path"
  docker build -f "$dockerfile" -t "$service_name" "$build_context"

  echo "🏷️  Tagging $service_name → $image_name"
  docker tag "$service_name" "$image_name"

  echo "🚀 Pushing $image_name to ECR..."
  docker push "$image_name"
done