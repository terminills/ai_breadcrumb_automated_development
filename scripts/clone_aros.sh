#!/bin/bash
# Clone AROS repository for AI training and development

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/config.json"

# Parse config using Python
AROS_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_repo_url'])")
AROS_UPSTREAM_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_upstream_url'])")
AROS_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_local_path'])")
GITHUB_TOKEN_ENV=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['github_token_env'])")
FULL_PATH="$PROJECT_ROOT/$AROS_PATH"

# Get GitHub token from environment variable
GITHUB_TOKEN="${!GITHUB_TOKEN_ENV}"

echo "================================================"
echo "AROS Repository Clone Script"
echo "================================================"
echo "Repository: $AROS_URL"
echo "Upstream: $AROS_UPSTREAM_URL"
echo "Target: $FULL_PATH"
echo ""

# Prepare authenticated URL if GitHub token is available
if [ -n "$GITHUB_TOKEN" ]; then
    # Extract the URL without protocol
    REPO_PATH=$(echo "$AROS_URL" | sed 's|https://||')
    AUTH_URL="https://${GITHUB_TOKEN}@${REPO_PATH}"
    echo "Using GitHub token authentication..."
else
    AUTH_URL="$AROS_URL"
    echo "No GitHub token found (set $GITHUB_TOKEN_ENV environment variable for private repos)"
fi

# Check if already cloned
if [ -d "$FULL_PATH" ]; then
    echo "AROS repository already exists at $FULL_PATH"
    echo "Updating repository..."
    cd "$FULL_PATH"
    
    # Update origin remote with authenticated URL if token is available
    if [ -n "$GITHUB_TOKEN" ]; then
        git remote set-url origin "$AUTH_URL"
    fi
    
    git pull
    echo "Repository updated successfully!"
else
    echo "Cloning AROS repository..."
    git clone "$AUTH_URL" "$FULL_PATH"
    echo "Repository cloned successfully!"
    
    # Add upstream remote for syncing
    cd "$FULL_PATH"
    git remote add upstream "$AROS_UPSTREAM_URL" 2>/dev/null || echo "Upstream remote already exists"
fi

# Ensure upstream remote exists
cd "$FULL_PATH"
if ! git remote | grep -q "^upstream$"; then
    echo "Adding upstream remote..."
    git remote add upstream "$AROS_UPSTREAM_URL"
fi

echo ""
echo "Repository statistics:"
echo "Total commits: $(git rev-list --count HEAD)"
echo "Total C files: $(find . -name '*.c' 2>/dev/null | wc -l)"
echo "Total H files: $(find . -name '*.h' 2>/dev/null | wc -l)"
echo ""
echo "Remotes configured:"
git remote -v
echo ""
echo "✓ AROS repository ready for AI training!"
