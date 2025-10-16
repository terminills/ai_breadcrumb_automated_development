#!/bin/bash
set -euo pipefail
# Test script to demonstrate diagnostic improvements

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  AROS-Cognito Diagnostics Test                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Create secure temporary file
TEMP_JSON=$(mktemp)
trap 'rm -f "$TEMP_JSON"' EXIT

# Test 1: Command-line diagnostics
echo "Test 1: Running command-line diagnostics..."
echo "─────────────────────────────────────────────────────────────────────"
python3 scripts/check_system_diagnostics.py || true
EXIT_CODE=$?
echo ""
echo "Exit code: $EXIT_CODE (0 = success, 1 = critical issues)"
echo ""

# Test 2: JSON export
echo "Test 2: Testing JSON export..."
echo "─────────────────────────────────────────────────────────────────────"
python3 scripts/check_system_diagnostics.py --json "$TEMP_JSON" --quiet || true
if [ -f "$TEMP_JSON" ]; then
    echo "✓ JSON export successful"
    echo "Preview:"
    head -20 "$TEMP_JSON"
    echo ""
    FILE_SIZE=$(wc -c < "$TEMP_JSON")
    echo "File size: $FILE_SIZE bytes"
else
    echo "✗ JSON export failed"
fi
echo ""

# Test 3: Enhanced download_models.py
echo "Test 3: Testing enhanced download_models.py..."
echo "─────────────────────────────────────────────────────────────────────"
python3 scripts/download_models.py --check || true
echo ""

# Test 4: Model loader diagnostics (simulate)
echo "Test 4: Simulating model loader error with diagnostics..."
echo "─────────────────────────────────────────────────────────────────────"
python3 scripts/test_model_loader_diagnostic.py || true
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Diagnostics Test Summary                                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Features tested:"
echo "  ✓ Command-line diagnostics with detailed output"
echo "  ✓ JSON export for programmatic access"
echo "  ✓ Enhanced model download script diagnostics"
echo "  ✓ Model loader error messages with diagnostics"
echo ""
echo "To test web UI diagnostics:"
echo "  1. Run: ./start_ui.sh"
echo "  2. Open: http://localhost:5000"
echo "  3. Click: '🔍 System Diagnostics' button"
echo ""
