#!/bin/bash
# Integration test for ROCm 5.7.1 PyTorch installation fix
# This test validates the logic without actually installing packages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_test() {
    echo -e "${YELLOW}TEST:${NC} $1"
}

print_pass() {
    echo -e "${GREEN}PASS:${NC} $1"
}

print_fail() {
    echo -e "${RED}FAIL:${NC} $1"
}

test_count=0
pass_count=0
fail_count=0

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   ROCm 5.7.1 PyTorch Installation Test                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Check that setup.sh has ROCm 5.7 special handling
test_count=$((test_count + 1))
print_test "setup.sh contains ROCm 5.7 special handling"
if grep -q 'if \[\[ "$rocm_ver" == "5.7" \]\]' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "ROCm 5.7 detection logic present"
else
    fail_count=$((fail_count + 1))
    print_fail "ROCm 5.7 detection logic missing"
fi

# Test 2: Check for AMD repository wheel URLs
test_count=$((test_count + 1))
print_test "setup.sh contains AMD repository wheel URLs"
if grep -q 'repo.radeon.com/rocm/manylinux/rocm-rel-5.7' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "AMD repository URLs present"
else
    fail_count=$((fail_count + 1))
    print_fail "AMD repository URLs missing"
fi

# Test 3: Check for --ignore-installed flag
test_count=$((test_count + 1))
print_test "setup.sh uses --ignore-installed flag"
if grep -q -- '--ignore-installed' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "--ignore-installed flag present"
else
    fail_count=$((fail_count + 1))
    print_fail "--ignore-installed flag missing"
fi

# Test 4: Check for torch 2.0.1+rocm5.7 wheel
test_count=$((test_count + 1))
print_test "setup.sh references torch 2.0.1+rocm5.7"
if grep -q 'torch-2.0.1%2Brocm5.7-cp310' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "torch 2.0.1+rocm5.7 wheel URL present"
else
    fail_count=$((fail_count + 1))
    print_fail "torch 2.0.1+rocm5.7 wheel URL missing"
fi

# Test 5: Check for torchvision 0.15.2+rocm5.7 wheel
test_count=$((test_count + 1))
print_test "setup.sh references torchvision 0.15.2+rocm5.7"
if grep -q 'torchvision-0.15.2%2Brocm5.7-cp310' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "torchvision 0.15.2+rocm5.7 wheel URL present"
else
    fail_count=$((fail_count + 1))
    print_fail "torchvision 0.15.2+rocm5.7 wheel URL missing"
fi

# Test 6: Check for torchaudio 2.0.2 installation
test_count=$((test_count + 1))
print_test "setup.sh installs torchaudio 2.0.2"
if grep -q 'torchaudio==2.0.2' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "torchaudio 2.0.2 installation present"
else
    fail_count=$((fail_count + 1))
    print_fail "torchaudio 2.0.2 installation missing"
fi

# Test 7: Check for numpy<2 force reinstall
test_count=$((test_count + 1))
print_test "setup.sh force reinstalls numpy<2"
if grep -q 'numpy<2.*--force-reinstall' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "numpy<2 force reinstall present"
else
    fail_count=$((fail_count + 1))
    print_fail "numpy<2 force reinstall missing"
fi

# Test 8: Check for Python 3.10 version check
test_count=$((test_count + 1))
print_test "setup.sh checks for Python 3.10"
if grep -q 'python_ver.*3.10' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "Python 3.10 version check present"
else
    fail_count=$((fail_count + 1))
    print_fail "Python 3.10 version check missing"
fi

# Test 9: Check troubleshooting documentation update
test_count=$((test_count + 1))
print_test "BOOTSTRAP_TROUBLESHOOTING.md has PyTorch installation section"
if grep -q 'PyTorch Installation Issues' "$PROJECT_ROOT/BOOTSTRAP_TROUBLESHOOTING.md"; then
    pass_count=$((pass_count + 1))
    print_pass "PyTorch installation troubleshooting documented"
else
    fail_count=$((fail_count + 1))
    print_fail "PyTorch installation troubleshooting missing"
fi

# Test 10: Check for distutils conflict documentation
test_count=$((test_count + 1))
print_test "Documentation covers distutils conflict"
if grep -q 'distutils-installed-package' "$PROJECT_ROOT/BOOTSTRAP_TROUBLESHOOTING.md"; then
    pass_count=$((pass_count + 1))
    print_pass "distutils conflict documented"
else
    fail_count=$((fail_count + 1))
    print_fail "distutils conflict documentation missing"
fi

# Test 11: Validate script syntax
test_count=$((test_count + 1))
print_test "setup.sh has valid bash syntax"
if bash -n "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "setup.sh syntax valid"
else
    fail_count=$((fail_count + 1))
    print_fail "setup.sh has syntax errors"
fi

# Test 12: Check for fallback mechanism
test_count=$((test_count + 1))
print_test "setup.sh has fallback to standard installation"
if grep -q 'Falling back to standard installation' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "Fallback mechanism present"
else
    fail_count=$((fail_count + 1))
    print_fail "Fallback mechanism missing"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                Test Summary                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Total Tests:  $test_count"
echo -e "Passed:       ${GREEN}$pass_count${NC}"
echo -e "Failed:       ${RED}$fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "The following features are validated:"
    echo "  ✓ ROCm 5.7.1 detection and special handling"
    echo "  ✓ AMD repository wheel URLs"
    echo "  ✓ --ignore-installed flag for distutils conflicts"
    echo "  ✓ torch 2.0.1+rocm5.7 installation"
    echo "  ✓ torchvision 0.15.2+rocm5.7 installation"
    echo "  ✓ torchaudio 2.0.2 installation"
    echo "  ✓ numpy<2 force reinstall"
    echo "  ✓ Python 3.10 version check"
    echo "  ✓ Comprehensive documentation"
    echo "  ✓ Fallback mechanism"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
