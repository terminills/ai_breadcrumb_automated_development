#!/bin/bash
# Sync AROS repository with upstream changes from aros-development-team

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/config.json"

# Parse config using Python
AROS_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_local_path'])")
AROS_UPSTREAM_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_upstream_url'])")
FULL_PATH="$PROJECT_ROOT/$AROS_PATH"

echo "================================================"
echo "AROS Upstream Sync Script"
echo "================================================"
echo "Syncing from: $AROS_UPSTREAM_URL"
echo "Local path: $FULL_PATH"
echo ""

# Check if repository exists
if [ ! -d "$FULL_PATH" ]; then
    echo "Error: AROS repository not found at $FULL_PATH"
    echo "Please run clone_aros.sh first"
    exit 1
fi

cd "$FULL_PATH"

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "Error: Not a git repository: $FULL_PATH"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Ensure upstream remote exists
if ! git remote | grep -q "^upstream$"; then
    echo "Adding upstream remote..."
    git remote add upstream "$AROS_UPSTREAM_URL"
else
    echo "Upstream remote already exists"
    git remote set-url upstream "$AROS_UPSTREAM_URL"
fi

# Fetch upstream changes
echo ""
echo "Fetching upstream changes..."
git fetch upstream

# Get upstream branch (typically master or main)
UPSTREAM_BRANCH="master"
if git ls-remote --heads upstream main | grep -q main; then
    UPSTREAM_BRANCH="main"
fi

echo "Upstream branch: $UPSTREAM_BRANCH"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo ""
    echo "Warning: You have uncommitted changes in your working directory."
    echo "Please commit or stash them before syncing."
    echo ""
    echo "Uncommitted files:"
    git status --short
    exit 1
fi

# Show what will be merged
echo ""
echo "Changes to be merged:"
git log --oneline HEAD..upstream/$UPSTREAM_BRANCH | head -20
TOTAL_COMMITS=$(git rev-list --count HEAD..upstream/$UPSTREAM_BRANCH)
echo ""
echo "Total commits to merge: $TOTAL_COMMITS"

# Ask for confirmation unless --yes flag is provided
if [ "$1" != "--yes" ] && [ "$1" != "-y" ]; then
    echo ""
    read -p "Do you want to merge these changes? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Sync cancelled"
        exit 0
    fi
fi

# Merge upstream changes
echo ""
echo "Merging upstream changes..."
if git merge upstream/$UPSTREAM_BRANCH --no-edit; then
    echo "✓ Successfully merged upstream changes"
    MERGE_SUCCESS=true
else
    echo "✗ Merge conflicts detected!"
    echo ""
    echo "Conflicting files:"
    git diff --name-only --diff-filter=U
    echo ""
    echo "To resolve conflicts:"
    echo "  1. Edit the conflicting files"
    echo "  2. Run: git add <file>"
    echo "  3. Run: git commit"
    echo ""
    exit 1
fi

# Show summary
echo ""
echo "================================================"
echo "Sync Summary"
echo "================================================"
echo "Branch: $CURRENT_BRANCH"
echo "Commits merged: $TOTAL_COMMITS"
echo "Repository is now up to date with upstream"
echo ""

# Show recent commits
echo "Recent commits after merge:"
git log --oneline -10
echo ""
echo "✓ Sync completed successfully!"
