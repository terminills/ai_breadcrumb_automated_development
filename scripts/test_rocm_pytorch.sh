#!/bin/bash
# Integration test for ROCm 7.0 PyTorch 2.9.0 installation
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
echo "║   ROCm 7.0 PyTorch 2.9.0 Installation Test                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Check that setup.sh has ROCm 7.0 special handling
test_count=$((test_count + 1))
print_test "setup.sh contains ROCm 7.0 special handling"
if grep -q 'if \[\[ "$rocm_ver" == "7.0" \]\]' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "ROCm 7.0 detection logic present"
else
    fail_count=$((fail_count + 1))
    print_fail "ROCm 7.0 detection logic missing"
fi

# Test 2: Check for PyTorch 2.9.0 version variable
test_count=$((test_count + 1))
print_test "setup.sh uses PYTORCH_VERSION=2.9.0"
if grep -q 'PYTORCH_VERSION="2.9.0"' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "PyTorch 2.9.0 version variable present"
else
    fail_count=$((fail_count + 1))
    print_fail "PyTorch 2.9.0 version variable missing"
fi

# Test 3: Check for official PyTorch repository usage
test_count=$((test_count + 1))
print_test "setup.sh uses official PyTorch repository"
if grep -q 'download.pytorch.org/whl' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "Official PyTorch repository URL present"
else
    fail_count=$((fail_count + 1))
    print_fail "Official PyTorch repository URL missing"
fi

# Test 4: Check that old AMD repository URLs are removed
test_count=$((test_count + 1))
print_test "setup.sh does not use old AMD repository wheels"
if ! grep -q 'torch-2.0.1%2Brocm5.7-cp310' "$PROJECT_ROOT/scripts/setup.sh" && ! grep -q 'torch-2.3.1%2Brocm5.7-cp310' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "Old torch wheel URLs removed"
else
    fail_count=$((fail_count + 1))
    print_fail "Old torch wheel URLs still present"
fi

# Test 5: Check for proper ROCm version formatting
test_count=$((test_count + 1))
print_test "setup.sh formats ROCm version correctly for PyTorch URL"
if grep -q 'rocm_url_ver="rocm' "$PROJECT_ROOT/scripts/setup.sh" && grep -q 'rocm_ver' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "ROCm version formatting present"
else
    fail_count=$((fail_count + 1))
    print_fail "ROCm version formatting missing"
fi

# Test 6: Check for torch/torchvision/torchaudio installation
test_count=$((test_count + 1))
print_test "setup.sh installs torch, torchvision, and torchaudio"
if grep -q 'pip install torch==' "$PROJECT_ROOT/scripts/setup.sh" && grep -q 'torchvision torchaudio' "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "PyTorch stack installation present"
else
    fail_count=$((fail_count + 1))
    print_fail "PyTorch stack installation missing"
fi

# Test 7: Check requirements.txt specifies torch>=2.9.0
test_count=$((test_count + 1))
print_test "requirements.txt specifies torch>=2.9.0"
if grep -q 'torch>=2.9.0' "$PROJECT_ROOT/requirements.txt"; then
    pass_count=$((pass_count + 1))
    print_pass "requirements.txt has correct PyTorch version"
else
    fail_count=$((fail_count + 1))
    print_fail "requirements.txt PyTorch version incorrect"
fi

# Test 8: Validate script syntax
test_count=$((test_count + 1))
print_test "setup.sh has valid bash syntax"
if bash -n "$PROJECT_ROOT/scripts/setup.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "setup.sh syntax valid"
else
    fail_count=$((fail_count + 1))
    print_fail "setup.sh has syntax errors"
fi

# Test 9: Check for fallback mechanism
test_count=$((test_count + 1))
print_test "setup.sh has fallback to unversioned installation"
if grep -q 'Trying without specifying exact version' "$PROJECT_ROOT/scripts/setup.sh"; then
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
    echo "  ✓ ROCm 7.0 detection and handling"
    echo "  ✓ PyTorch 2.9.0 version variable"
    echo "  ✓ Official PyTorch repository usage"
    echo "  ✓ Old AMD repository URLs removed"
    echo "  ✓ ROCm version formatting for URLs"
    echo "  ✓ PyTorch stack installation (torch, torchvision, torchaudio)"
    echo "  ✓ requirements.txt specifies torch>=2.9.0"
    echo "  ✓ Valid bash syntax"
    echo "  ✓ Fallback mechanism"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
