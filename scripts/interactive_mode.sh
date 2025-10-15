#!/bin/bash
# Interactive Development Mode Launcher
# Provides easy access to interactive AI development tools

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║       Interactive AI Development Assistant                ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Choose your interactive mode:"
echo ""
echo "  1. Interactive Demo    - See the full workflow in action"
echo "  2. Chat Mode          - Conversational development assistant"
echo "  3. Copilot Iteration  - Run full iteration with real models"
echo "  4. Web UI             - Monitor development in browser"
echo "  5. Exit"
echo ""

read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Starting Interactive Demo..."
        echo ""
        python3 "$SCRIPT_DIR/interactive_demo.py"
        ;;
    2)
        echo ""
        echo "Starting Chat Mode..."
        echo ""
        python3 "$SCRIPT_DIR/interactive_chat.py"
        ;;
    3)
        echo ""
        read -p "Enter project name (e.g., radeonsi): " project
        read -p "Enter max iterations (default: 10): " iterations
        iterations=${iterations:-10}
        echo ""
        echo "Starting Copilot Iteration..."
        echo ""
        "$SCRIPT_DIR/run_copilot_iteration.sh" "$project" "$iterations"
        ;;
    4)
        echo ""
        echo "Starting Web UI..."
        echo ""
        cd "$PROJECT_ROOT"
        ./start_ui.sh
        ;;
    5)
        echo ""
        echo "Goodbye! 👋"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid choice. Please run again and select 1-5."
        echo ""
        exit 1
        ;;
esac
