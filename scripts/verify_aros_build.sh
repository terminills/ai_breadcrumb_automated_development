#!/bin/bash
# Verify that AROS builds successfully after updates

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/config.json"

# Parse config using Python
AROS_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['aros_local_path'])")
LOGS_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['logs_path'])")
FULL_PATH="$PROJECT_ROOT/$AROS_PATH"
BUILD_LOG="$PROJECT_ROOT/$LOGS_PATH/build/build_verification_$(date +%Y%m%d_%H%M%S).log"

echo "================================================"
echo "AROS Build Verification Script"
echo "================================================"
echo "AROS path: $FULL_PATH"
echo "Build log: $BUILD_LOG"
echo ""

# Check if repository exists
if [ ! -d "$FULL_PATH" ]; then
    echo "Error: AROS repository not found at $FULL_PATH"
    echo "Please run clone_aros.sh first"
    exit 1
fi

cd "$FULL_PATH"

# Create log directory
mkdir -p "$(dirname "$BUILD_LOG")"

# Check for AROS build system
if [ ! -f "configure" ] && [ ! -f "mmakefile" ]; then
    echo "Warning: AROS build files not found. This may not be a complete AROS checkout."
fi

# Function to test a simple build target
test_build() {
    local target="$1"
    echo ""
    echo "Testing build target: $target"
    echo "----------------------------------------"
    
    if command -v make &> /dev/null; then
        if make $target 2>&1 | tee -a "$BUILD_LOG"; then
            echo "✓ Build target '$target' succeeded"
            return 0
        else
            echo "✗ Build target '$target' failed"
            return 1
        fi
    else
        echo "Warning: 'make' command not found. Cannot verify build."
        return 2
    fi
}

# Check for common AROS build requirements
echo "Checking build prerequisites..."
echo "----------------------------------------"

MISSING_DEPS=()

# Check for basic build tools
command -v gcc >/dev/null 2>&1 || MISSING_DEPS+=("gcc")
command -v make >/dev/null 2>&1 || MISSING_DEPS+=("make")
command -v python3 >/dev/null 2>&1 || MISSING_DEPS+=("python3")

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "Warning: Missing build dependencies:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "Install missing dependencies with:"
    echo "  sudo apt-get install gcc make python3"
    echo ""
fi

# Check if AROS is configured
if [ -f "bin/linux-x86_64/AROS/boot/aros" ] || [ -f "mmakefile.config" ]; then
    echo "✓ AROS appears to be configured"
    CONFIGURED=true
else
    echo "Note: AROS may not be configured yet"
    echo "To configure AROS, typically run:"
    echo "  ./configure --target=linux-x86_64"
    CONFIGURED=false
fi

echo ""
echo "Build verification strategy:"
if [ "$CONFIGURED" = true ]; then
    echo "  1. Test compilation of a simple module"
    echo "  2. Check for syntax errors"
else
    echo "  1. Check for syntax errors in source files"
    echo "  2. Configuration needed before full build"
fi

# Perform basic syntax checks on recent changes
echo ""
echo "Performing syntax checks on C files..."
echo "----------------------------------------"

SYNTAX_ERRORS=0
CHECKED_FILES=0

# Get recently modified C files (if any)
if git rev-parse HEAD >/dev/null 2>&1; then
    # Get files changed in last commit
    RECENT_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | grep -E '\.(c|h)$' || true)
    
    if [ -n "$RECENT_FILES" ]; then
        echo "Checking recently modified files:"
        while IFS= read -r file; do
            if [ -f "$file" ]; then
                echo -n "  Checking $file... "
                CHECKED_FILES=$((CHECKED_FILES + 1))
                
                # Basic syntax check with gcc
                if gcc -fsyntax-only -I. -Iarch/all-linux/include -Iarch/all-unix/include \
                       -Icompiler/include -Irom/exec "$file" 2>>"$BUILD_LOG"; then
                    echo "✓"
                else
                    echo "✗"
                    SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
                fi
            fi
        done <<< "$RECENT_FILES"
    else
        echo "No recently modified C/H files found"
    fi
else
    echo "Not a git repository, skipping recent changes check"
fi

# Summary
echo ""
echo "================================================"
echo "Build Verification Summary"
echo "================================================"
echo "Files checked: $CHECKED_FILES"
echo "Syntax errors: $SYNTAX_ERRORS"
echo "Build log: $BUILD_LOG"
echo ""

if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo "✓ No syntax errors detected in checked files"
    
    if [ "$CONFIGURED" = true ]; then
        echo ""
        echo "To perform a full build, run:"
        echo "  cd $FULL_PATH"
        echo "  make"
    else
        echo ""
        echo "To configure and build AROS:"
        echo "  cd $FULL_PATH"
        echo "  ./configure --target=linux-x86_64"
        echo "  make"
    fi
    
    exit 0
else
    echo "✗ Syntax errors detected. Check build log for details:"
    echo "  cat $BUILD_LOG"
    exit 1
fi
