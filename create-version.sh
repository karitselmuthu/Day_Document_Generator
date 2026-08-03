#!/bin/bash
# create-version.sh
# 
# Usage: ./create-version.sh "2.1.0"
# 
# This script:
# 1. Creates a version branch from current main
# 2. Pushes the version branch to GitHub (archive)
# 3. Keeps main ready for next changes
#

if [ -z "$1" ]; then
    echo "Usage: ./create-version.sh <VERSION>"
    echo "Example: ./create-version.sh 2.1.0"
    exit 1
fi

VERSION=$1
DATE=$(date +%Y-%m-%d)
BRANCH_NAME="v${VERSION}-${DATE}"
CURRENT_COMMIT=$(git rev-parse HEAD)

echo "════════════════════════════════════════════════════════"
echo "Creating version branch: $BRANCH_NAME"
echo "════════════════════════════════════════════════════════"
echo ""

# Ensure we're on main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: You must be on main branch to create a version"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Ensure main is up to date
echo "📥 Pulling latest changes..."
git pull origin main || {
    echo "❌ Failed to pull from origin"
    exit 1
}

# Create version branch
echo "🔄 Creating version branch: $BRANCH_NAME from commit ${CURRENT_COMMIT:0:7}"
git branch "$BRANCH_NAME" HEAD || {
    echo "❌ Failed to create version branch"
    exit 1
}

# Push version branch to GitHub
echo "📤 Pushing version branch to GitHub..."
git push origin "$BRANCH_NAME" || {
    echo "❌ Failed to push version branch"
    exit 1
}

# Verify push
REMOTE_BRANCHES=$(git branch -r | grep "$BRANCH_NAME")
if [ -n "$REMOTE_BRANCHES" ]; then
    echo "✅ Version branch pushed successfully"
else
    echo "❌ Failed to verify version branch on GitHub"
    exit 1
fi

# Remind about next steps
echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Version $BRANCH_NAME created and pushed to GitHub"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo "   1. Main branch is ready for new changes"
echo "   2. Version branch ($BRANCH_NAME) is archived on GitHub"
echo "   3. Continue developing on main branch:"
echo "      git checkout main"
echo "      # Make your changes..."
echo "      git add ."
echo "      git commit -m 'Your changes'"
echo ""
echo "📊 Current Versions:"
git branch -v | grep "^.*v[0-9]" || echo "   (No version branches yet)"
echo "   main: $(git log -1 --oneline)"
echo ""
