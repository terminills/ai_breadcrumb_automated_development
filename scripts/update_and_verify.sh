#!/bin/bash
# Complete workflow: sync from upstream and verify build

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================"
echo "AROS Update and Build Verification Workflow"
echo "================================================"
echo ""

# Step 1: Sync with upstream
echo "Step 1: Syncing with upstream AROS repository..."
echo "================================================"
if bash "$SCRIPT_DIR/sync_aros_upstream.sh" "$@"; then
    echo "✓ Sync completed successfully"
else
    EXIT_CODE=$?
    echo "✗ Sync failed with exit code: $EXIT_CODE"
    
    if [ $EXIT_CODE -eq 1 ]; then
        echo ""
        echo "This could be due to merge conflicts."
        echo "Please resolve conflicts manually and then run:"
        echo "  $SCRIPT_DIR/verify_aros_build.sh"
    fi
    
    exit $EXIT_CODE
fi

# Step 2: Verify build
echo ""
echo "Step 2: Verifying AROS build..."
echo "================================================"
if bash "$SCRIPT_DIR/verify_aros_build.sh"; then
    echo ""
    echo "================================================"
    echo "✓ Update and Verification Complete"
    echo "================================================"
    echo "Your AROS repository is up to date and builds successfully!"
    exit 0
else
    echo ""
    echo "================================================"
    echo "✗ Build Verification Failed"
    echo "================================================"
    echo "The sync completed but build verification found issues."
    echo "Check the build log for details and fix any errors."
    exit 1
fi
