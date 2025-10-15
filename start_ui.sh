#!/bin/bash
# Start the AI Breadcrumb UI Server
# This script starts the Flask UI for monitoring AI development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=========================================="
echo "Starting AI Breadcrumb Development UI"
echo "=========================================="
echo ""

# Check Python dependencies
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed. Installing dependencies..."
    pip install -r "$PROJECT_ROOT/requirements.txt" --user
fi

# Create necessary directories if they don't exist
mkdir -p "$PROJECT_ROOT/logs/errors"
mkdir -p "$PROJECT_ROOT/logs/reasoning"
mkdir -p "$PROJECT_ROOT/logs/training"
mkdir -p "$PROJECT_ROOT/logs/compilation"
mkdir -p "$PROJECT_ROOT/models"

# Check if aros-src exists
if [ ! -d "$PROJECT_ROOT/aros-src" ]; then
    echo "⚠️  Warning: aros-src directory not found"
    echo "   Sample files will be used for demonstration"
    echo "   Run './scripts/clone_aros.sh' to clone the full AROS repository"
    echo ""
fi

# Start the UI server
cd "$PROJECT_ROOT/ui"
echo "🚀 Starting UI server..."
echo ""
python3 app.py
