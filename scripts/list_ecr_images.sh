#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ECR repository base and name
ecr_base="058135280735.dkr.ecr.us-east-1.amazonaws.com"
repo_name="etsy-analyzer"

echo -e "${BLUE}🔍 Checking ECR repository: $repo_name in us-east-1...${NC}"

# Check if repository exists
if ! aws ecr describe-repositories --repository-name "$repo_name" --region us-east-1 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Repository $repo_name not found.${NC}"
    exit 0
fi

# Get image details
images=$(aws ecr describe-images \
    --repository-name "$repo_name" \
    --region us-east-1 \
    --query 'imageDetails[*].[imageTags[0],imageSizeInBytes,imagePushedAt]' \
    --output text)

if [[ -z "$images" ]]; then
    echo -e "${YELLOW}⚠️  No images found in repository.${NC}"
    exit 0
fi

# Print header
echo -e "\n${GREEN}📦 Repository: $repo_name${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
printf "%-30s %-15s %-25s\n" "TAG" "SIZE" "PUSHED AT"
echo -e "${BLUE}----------------------------------------${NC}"

total_size=0

# Process each image
while IFS=$'\t' read -r tag size pushed_at; do
    # Format size in MB using awk
    size_mb=$(awk "BEGIN {printf \"%.2f\", $size/1024/1024}")
    # Format date
    date=$(date -d "$pushed_at" "+%Y-%m-%d %H:%M:%S")
    
    printf "%-30s %-15s %-25s\n" "$tag" "${size_mb}MB" "$date"
    
    total_size=$((total_size + size))
done <<< "$images"

# Print summary
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "\n${GREEN}📊 Summary:${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "Total Images: ${YELLOW}$(echo "$images" | wc -l)${NC}"
echo -e "Total Size: ${YELLOW}$(awk "BEGIN {printf \"%.2f\", $total_size/1024/1024}")MB${NC}"
echo -e "${BLUE}----------------------------------------${NC}" 