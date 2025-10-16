#!/bin/bash
# Test script to demonstrate diagnostic improvements

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  AROS-Cognito Diagnostics Test                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Command-line diagnostics
echo "Test 1: Running command-line diagnostics..."
echo "─────────────────────────────────────────────────────────────────────"
python3 scripts/check_system_diagnostics.py
EXIT_CODE=$?
echo ""
echo "Exit code: $EXIT_CODE (0 = success, 1 = critical issues)"
echo ""

# Test 2: JSON export
echo "Test 2: Testing JSON export..."
echo "─────────────────────────────────────────────────────────────────────"
python3 scripts/check_system_diagnostics.py --json /tmp/diagnostics_test.json --quiet
if [ -f /tmp/diagnostics_test.json ]; then
    echo "✓ JSON export successful"
    echo "Preview:"
    head -20 /tmp/diagnostics_test.json
    echo ""
    FILE_SIZE=$(wc -c < /tmp/diagnostics_test.json)
    echo "File size: $FILE_SIZE bytes"
else
    echo "✗ JSON export failed"
fi
echo ""

# Test 3: Enhanced download_models.py
echo "Test 3: Testing enhanced download_models.py..."
echo "─────────────────────────────────────────────────────────────────────"
python3 scripts/download_models.py --check
echo ""

# Test 4: Model loader diagnostics (simulate)
echo "Test 4: Simulating model loader error with diagnostics..."
echo "─────────────────────────────────────────────────────────────────────"
python3 -c "
import sys
sys.path.insert(0, 'src')
from local_models.model_loader import LocalModelLoader

try:
    loader = LocalModelLoader()
    # This will fail because torch is not installed
    loader.load_model('codegen', use_mock=False)
except Exception as e:
    print('Caught expected error:')
    print(str(e)[:500])  # Print first 500 chars
"
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
