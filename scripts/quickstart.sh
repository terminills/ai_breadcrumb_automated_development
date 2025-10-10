#!/bin/bash
# Quick start script for AROS-Cognito system
# Sets up the environment and starts the monitoring UI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     AROS-Cognito: AI Breadcrumb Development System         ║"
echo "║              Quick Start Initialization                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

if ! command_exists python3; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

if ! command_exists git; then
    echo "❌ Error: Git is not installed"
    echo "   Please install Git"
    exit 1
fi

echo "✓ Python 3: $(python3 --version)"
echo "✓ Git: $(git --version)"
echo ""

# Check if requirements are installed
echo "Checking Python dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Create necessary directories
echo "Creating directory structure..."
mkdir -p "$PROJECT_ROOT/logs/"{training,compile,errors,agent}
mkdir -p "$PROJECT_ROOT/models"
echo "✓ Directories created"
echo ""

# Check if AROS is cloned
if [ ! -d "$PROJECT_ROOT/aros-src" ]; then
    echo "AROS repository not found."
    read -p "Would you like to clone it now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        bash "$SCRIPT_DIR/clone_aros.sh"
    else
        echo "Skipping AROS clone. You can run ./scripts/clone_aros.sh later."
    fi
else
    echo "✓ AROS repository found"
fi
echo ""

# Display next steps
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo ""
echo "1. Start the Monitoring UI:"
echo "   cd ui && python app.py"
echo "   Then open: http://localhost:5000"
echo ""
echo "2. Train the AI Model (optional):"
echo "   ./scripts/train_model.sh"
echo ""
echo "3. Run the AI Agent:"
echo "   ./scripts/run_ai_agent.sh ITERATE radeonsi 10"
echo ""
echo "4. View Documentation:"
echo "   cat SETUP.md"
echo ""

# Offer to start UI
read -p "Would you like to start the monitoring UI now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting UI..."
    echo "Press Ctrl+C to stop"
    echo ""
    cd "$PROJECT_ROOT/ui"
    python3 app.py
fi
