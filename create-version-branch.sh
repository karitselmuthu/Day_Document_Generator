#!/bin/bash

# Script: create-version-branch.sh
# Purpose: Automatically create a version branch for today's commits
# Usage: ./create-version-branch.sh
# Or with custom version: ./create-version-branch.sh v2.0.1

set -e

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get today's date
TODAY=$(date +%Y-%m-%d)
TODAY_FORMATTED=$(date +%d_%m_%y)

# Determine version
if [ -z "$1" ]; then
    # Auto-detect version from last version branch
    LAST_VERSION=$(git branch -r | grep "origin/v" | tail -1 | sed 's|.*origin/||' | sed 's|-.*||')
    
    if [ -z "$LAST_VERSION" ]; then
        VERSION="v1.0.0"
    else
        # Parse semantic versioning
        MAJOR=$(echo $LAST_VERSION | cut -d. -f1 | sed 's/v//')
        MINOR=$(echo $LAST_VERSION | cut -d. -f2)
        PATCH=$(echo $LAST_VERSION | cut -d. -f3)
        
        # Increment patch version for same day, minor for new day
        LAST_DATE=$(git branch -r | grep "origin/v" | tail -1 | sed 's|.*-||')
        
        if [ "$LAST_DATE" == "$TODAY_FORMATTED" ]; then
            # Same day - increment patch
            PATCH=$((PATCH + 1))
        else
            # New day - increment minor, reset patch
            MINOR=$((MINOR + 1))
            PATCH=0
        fi
        
        VERSION="v${MAJOR}.${MINOR}.${PATCH}"
    fi
else
    VERSION="$1"
fi

VERSION_BRANCH="${VERSION}-${TODAY_FORMATTED}"

echo -e "${YELLOW}Creating version branch for today (${TODAY})${NC}"
echo -e "Branch name: ${GREEN}${VERSION_BRANCH}${NC}\n"

# Check if branch already exists
if git show-ref --quiet refs/heads/$VERSION_BRANCH || \
   git show-ref --quiet refs/remotes/origin/$VERSION_BRANCH; then
    echo -e "${RED}✗ Branch ${VERSION_BRANCH} already exists!${NC}"
    exit 1
fi

# Get current main commit
MAIN_COMMIT=$(git rev-parse main)
echo "Current main commit: ${MAIN_COMMIT:0:7}"

# Create and push version branch
echo -e "\n${YELLOW}Creating branch...${NC}"
git checkout -b $VERSION_BRANCH

echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push origin $VERSION_BRANCH

echo -e "\n${YELLOW}Switching back to main...${NC}"
git checkout main

echo -e "\n${GREEN}✓ Version branch created and pushed successfully!${NC}"
echo -e "   Branch: ${VERSION_BRANCH}"
echo -e "   Status: Ready for production\n"

# Show all current version branches
echo -e "${YELLOW}Current version branches:${NC}"
git branch -r | grep "origin/v" | sed 's|.*origin/||' | sort -V | tail -5
