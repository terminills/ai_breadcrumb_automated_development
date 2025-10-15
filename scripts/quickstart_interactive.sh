#!/bin/bash
# Quick Start Script for Interactive Development
# Gets you up and running in seconds

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        Welcome to AI Breadcrumb Development!              ║"
echo "║           Quick Start - Interactive Mode                  ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found."
    echo "   Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check basic dependencies
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    pip install -q -r "$PROJECT_ROOT/requirements.txt" --user || true
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies installed"
fi

# Create necessary directories
mkdir -p "$PROJECT_ROOT/logs/sessions"
mkdir -p "$PROJECT_ROOT/logs/errors"
mkdir -p "$PROJECT_ROOT/logs/reasoning"
echo "✓ Directories created"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Setup Complete! Choose your first experience:"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  1. 🎬 Interactive Demo (2 minutes)"
echo "     See the full AI development workflow in action"
echo ""
echo "  2. 💬 Chat Mode (Interactive)"
echo "     Talk with the AI development assistant"
echo ""
echo "  3. 🌐 Web UI (Browser-based)"
echo "     Monitor development in your browser"
echo ""
echo "  4. 📖 Read Documentation"
echo "     Learn more before starting"
echo ""
echo "  5. ⚙️  Advanced: Configure Models"
echo "     Set up real AI models for code generation"
echo ""

read -p "Enter choice [1-5]: " choice

echo ""

case $choice in
    1)
        echo "🎬 Starting Interactive Demo..."
        echo ""
        python3 "$SCRIPT_DIR/interactive_demo.py"
        ;;
    2)
        echo "💬 Starting Chat Mode..."
        echo ""
        echo "Tip: Type 'help' to see available commands"
        echo ""
        python3 "$SCRIPT_DIR/interactive_chat.py"
        ;;
    3)
        echo "🌐 Starting Web UI..."
        echo ""
        echo "The UI will open in your browser at:"
        echo "  http://localhost:5000"
        echo ""
        echo "Press Ctrl+C to stop when done"
        echo ""
        sleep 2
        cd "$PROJECT_ROOT"
        ./start_ui.sh
        ;;
    4)
        echo "📖 Opening Documentation..."
        echo ""
        echo "Available guides:"
        echo "  • Interactive Guide: docs/INTERACTIVE_GUIDE.md"
        echo "  • Copilot Style: docs/COPILOT_STYLE_ITERATION.md"
        echo "  • Quick Start: docs/QUICKSTART_COPILOT.md"
        echo "  • System Overview: SYSTEM_OVERVIEW.md"
        echo ""
        echo "Opening Interactive Guide..."
        echo ""
        if command -v less &> /dev/null; then
            less "$PROJECT_ROOT/docs/INTERACTIVE_GUIDE.md"
        elif command -v more &> /dev/null; then
            more "$PROJECT_ROOT/docs/INTERACTIVE_GUIDE.md"
        else
            cat "$PROJECT_ROOT/docs/INTERACTIVE_GUIDE.md"
        fi
        ;;
    5)
        echo "⚙️  Model Configuration..."
        echo ""
        echo "To use real AI models for code generation:"
        echo ""
        echo "1. Install PyTorch and Transformers:"
        echo "   pip install torch transformers"
        echo ""
        echo "2. Edit config/models.json to set your preferred models"
        echo ""
        echo "3. Run copilot iteration:"
        echo "   ./scripts/run_copilot_iteration.sh radeonsi 10"
        echo ""
        echo "For detailed instructions, see:"
        echo "  docs/QUICKSTART_COPILOT.md"
        echo ""
        
        read -p "Would you like to see the model config? [y/N]: " show_config
        if [[ "$show_config" =~ ^[Yy] ]]; then
            echo ""
            cat "$PROJECT_ROOT/config/models.json"
            echo ""
        fi
        ;;
    *)
        echo "Invalid choice."
        echo ""
        echo "Run this script again to try an option, or use:"
        echo "  ./scripts/interactive_mode.sh"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Thanks for trying AI Breadcrumb Development!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  • Run this script again to try other modes"
echo "  • Launch the full menu: ./scripts/interactive_mode.sh"
echo "  • Read the docs: docs/INTERACTIVE_GUIDE.md"
echo "  • Try the API: examples/copilot_api_example.py"
echo ""
