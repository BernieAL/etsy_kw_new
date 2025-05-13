#!/bin/bash

# Make sure AWS CLI is configured with correct profile and region
AWS_PROFILE=default
AWS_REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)

# Optional: define repos to clean (or auto-discover)
REPOS=$(aws ecr describe-repositories --region "$AWS_REGION" --query "repositories[*].repositoryName" --output text --profile "$AWS_PROFILE")

echo "🧼 Starting ECR cleanup..."

for repo in $REPOS; do
  echo "🗑️ Deleting images in ECR repo: $repo"

  # Get image digests
  image_digests=$(aws ecr list-images \
    --region "$AWS_REGION" \
    --repository-name "$repo" \
    --query 'imageIds[*]' \
    --output json \
    --profile "$AWS_PROFILE")

  if [[ "$image_digests" != "[]" ]]; then
    aws ecr batch-delete-image \
      --region "$AWS_REGION" \
      --repository-name "$repo" \
      --image-ids "$image_digests" \
      --profile "$AWS_PROFILE"
  else
    echo "  ⚠️  No images to delete in $repo"
  fi

  echo "❌ Deleting ECR repository: $repo"
  aws ecr delete-repository \
    --repository-name "$repo" \
    --region "$AWS_REGION" \
    --force \
    --profile "$AWS_PROFILE"
done

echo "✅ ECR cleanup complete."
