#!/bin/bash
# Clone AROS repository for AI training and development

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/config.json"

# Parse config using Python
AROS_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_repo_url'])")
AROS_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_local_path'])")
FULL_PATH="$PROJECT_ROOT/$AROS_PATH"

echo "================================================"
echo "AROS Repository Clone Script"
echo "================================================"
echo "Repository: $AROS_URL"
echo "Target: $FULL_PATH"
echo ""

# Check if already cloned
if [ -d "$FULL_PATH" ]; then
    echo "AROS repository already exists at $FULL_PATH"
    echo "Updating repository..."
    cd "$FULL_PATH"
    git pull
    echo "Repository updated successfully!"
else
    echo "Cloning AROS repository..."
    git clone "$AROS_URL" "$FULL_PATH"
    echo "Repository cloned successfully!"
fi

echo ""
echo "Repository statistics:"
cd "$FULL_PATH"
echo "Total commits: $(git rev-list --count HEAD)"
echo "Total C files: $(find . -name '*.c' | wc -l)"
echo "Total H files: $(find . -name '*.h' | wc -l)"
echo ""
echo "✓ AROS repository ready for AI training!"
