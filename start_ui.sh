#!/bin/bash
# Start the AI Breadcrumb UI Server
# This script starts the Flask UI for monitoring AI development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/venv"

echo "=========================================="
echo "Starting AI Breadcrumb Development UI"
echo "=========================================="
echo ""

# Activate virtual environment if it exists and is not already active
if [ -d "$VENV_DIR" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "🔧 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "✓ Virtual environment activated"
    echo ""
elif [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not found at $VENV_DIR"
    echo "   Run './scripts/bootstrap_ubuntu.sh' to set up the environment"
    echo "   Attempting to use system Python..."
    echo ""
fi

# Check Python dependencies
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed. Installing dependencies..."
    if [ -n "$VIRTUAL_ENV" ]; then
        pip install -r "$PROJECT_ROOT/requirements.txt"
    else
        pip install -r "$PROJECT_ROOT/requirements.txt" --user
    fi
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

# Use python if in venv, otherwise python3
if [ -n "$VIRTUAL_ENV" ]; then
    python app.py
else
    python3 app.py
fi
