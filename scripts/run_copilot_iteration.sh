#!/bin/bash
# Run Copilot-Style Iteration with Local Models
# Enhanced iteration loop with exploration, reasoning, and interactive capabilities

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "  Copilot-Style AI Iteration with Local Models"
echo "============================================================"
echo ""

# Parse arguments
PROJECT="${1:-radeonsi}"
MAX_ITERATIONS="${2:-10}"
AROS_PATH="${3:-$PROJECT_ROOT/aros-src}"
LOG_PATH="${4:-$PROJECT_ROOT/logs/copilot_iteration}"

echo "Configuration:"
echo "  Project: $PROJECT"
echo "  Max Iterations: $MAX_ITERATIONS"
echo "  AROS Path: $AROS_PATH"
echo "  Log Path: $LOG_PATH"
echo ""

# Check if AROS is cloned
if [ ! -d "$AROS_PATH" ]; then
    echo "Error: AROS repository not found at $AROS_PATH"
    echo "Please run: ./scripts/clone_aros.sh"
    echo "Or specify the correct path as the 3rd argument"
    exit 1
fi

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import torch; import transformers" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: PyTorch or Transformers not installed!"
    echo "The models will fail to load without these dependencies."
    echo ""
    echo "To install (CPU version):"
    echo "  pip install torch transformers"
    echo ""
    echo "To install (AMD ROCm version for GPU acceleration):"
    echo "  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7"
    echo "  pip install transformers"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create log directory
mkdir -p "$LOG_PATH"

# Setup Python path
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo ""
echo "Starting Copilot-Style Iteration..."
echo "Press Ctrl+C to stop at any time"
echo ""
echo "Logs will be saved to: $LOG_PATH"
echo ""

# Run the copilot iteration script
python3 "$PROJECT_ROOT/src/copilot_iteration.py" \
    --aros-path "$AROS_PATH" \
    --project "$PROJECT" \
    --max-iterations "$MAX_ITERATIONS" \
    --log-path "$LOG_PATH"

EXIT_CODE=$?

echo ""
echo "============================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Copilot-Style Iteration completed successfully!"
else
    echo "⚠ Copilot-Style Iteration completed with errors (exit code: $EXIT_CODE)"
fi

echo ""
echo "Session logs: $LOG_PATH/sessions/"
echo "Compilation logs: $LOG_PATH/compile/"
echo "Error logs: $LOG_PATH/errors/"
echo ""
echo "============================================================"

exit $EXIT_CODE
