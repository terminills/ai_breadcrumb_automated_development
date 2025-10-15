#!/bin/bash
# Test script for bootstrap functionality
# Tests key components without requiring full installation

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

run_test() {
    test_count=$((test_count + 1))
    print_test "$1"
    if eval "$2"; then
        pass_count=$((pass_count + 1))
        print_pass "$1"
    else
        fail_count=$((fail_count + 1))
        print_fail "$1"
        return 1
    fi
}

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Bootstrap Test Suite                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Script files exist and are executable
print_test "Bootstrap script exists and is executable"
if [ -x "$PROJECT_ROOT/scripts/bootstrap_ubuntu.sh" ]; then
    pass_count=$((pass_count + 1))
    print_pass "Bootstrap script exists and is executable"
else
    fail_count=$((fail_count + 1))
    print_fail "Bootstrap script not found or not executable"
fi
test_count=$((test_count + 1))

# Test 2: Migration script exists and is executable
print_test "Migration script exists and is executable"
if [ -x "$PROJECT_ROOT/scripts/migrate_database.sh" ]; then
    pass_count=$((pass_count + 1))
    print_pass "Migration script exists and is executable"
else
    fail_count=$((fail_count + 1))
    print_fail "Migration script not found or not executable"
fi
test_count=$((test_count + 1))

# Test 3: Script syntax validation
print_test "Bootstrap script syntax"
if bash -n "$PROJECT_ROOT/scripts/bootstrap_ubuntu.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "Bootstrap script syntax valid"
else
    fail_count=$((fail_count + 1))
    print_fail "Bootstrap script has syntax errors"
fi
test_count=$((test_count + 1))

print_test "Migration script syntax"
if bash -n "$PROJECT_ROOT/scripts/migrate_database.sh"; then
    pass_count=$((pass_count + 1))
    print_pass "Migration script syntax valid"
else
    fail_count=$((fail_count + 1))
    print_fail "Migration script has syntax errors"
fi
test_count=$((test_count + 1))

# Test 4: Configuration file exists and is valid JSON
print_test "Configuration file exists and is valid JSON"
if [ -f "$PROJECT_ROOT/config/config.json" ] && python3 -m json.tool "$PROJECT_ROOT/config/config.json" > /dev/null 2>&1; then
    pass_count=$((pass_count + 1))
    print_pass "Configuration file valid"
else
    fail_count=$((fail_count + 1))
    print_fail "Configuration file missing or invalid"
fi
test_count=$((test_count + 1))

# Test 5: UI host is set to 0.0.0.0 for network access
print_test "UI configured for network access"
if grep -q '"host": "0.0.0.0"' "$PROJECT_ROOT/config/config.json"; then
    pass_count=$((pass_count + 1))
    print_pass "UI host set to 0.0.0.0"
else
    fail_count=$((fail_count + 1))
    print_fail "UI host not set to 0.0.0.0"
fi
test_count=$((test_count + 1))

# Test 6: Run database migration
print_test "Database migration execution"
if bash "$PROJECT_ROOT/scripts/migrate_database.sh" > /dev/null 2>&1; then
    pass_count=$((pass_count + 1))
    print_pass "Database migration successful"
else
    fail_count=$((fail_count + 1))
    print_fail "Database migration failed"
fi
test_count=$((test_count + 1))

# Test 7: Check database files created
print_test "Database files created"
all_exist=true
for db in "logs/errors/error_database.json" "logs/reasoning/reasoning_database.json" "logs/training/training_state.json" "logs/compile/compile_state.json"; do
    if [ ! -f "$PROJECT_ROOT/$db" ]; then
        all_exist=false
        break
    fi
done

if [ "$all_exist" = true ]; then
    pass_count=$((pass_count + 1))
    print_pass "All database files created"
else
    fail_count=$((fail_count + 1))
    print_fail "Some database files missing"
fi
test_count=$((test_count + 1))

# Test 8: Validate database JSON
print_test "Database files are valid JSON"
all_valid=true
for db in "logs/errors/error_database.json" "logs/reasoning/reasoning_database.json" "logs/training/training_state.json" "logs/compile/compile_state.json"; do
    if ! python3 -m json.tool "$PROJECT_ROOT/$db" > /dev/null 2>&1; then
        all_valid=false
        break
    fi
done

if [ "$all_valid" = true ]; then
    pass_count=$((pass_count + 1))
    print_pass "All database files are valid JSON"
else
    fail_count=$((fail_count + 1))
    print_fail "Some database files have invalid JSON"
fi
test_count=$((test_count + 1))

# Test 9: Check schema version tracking
print_test "Schema version tracking"
if [ -f "$PROJECT_ROOT/logs/.schema_version" ]; then
    version=$(cat "$PROJECT_ROOT/logs/.schema_version")
    if [ "$version" = "1" ]; then
        pass_count=$((pass_count + 1))
        print_pass "Schema version correctly set to 1"
    else
        fail_count=$((fail_count + 1))
        print_fail "Schema version incorrect: $version"
    fi
else
    fail_count=$((fail_count + 1))
    print_fail "Schema version file not found"
fi
test_count=$((test_count + 1))

# Test 10: Check UI app syntax
print_test "UI app Python syntax"
if python3 -m py_compile "$PROJECT_ROOT/ui/app.py" 2>/dev/null; then
    pass_count=$((pass_count + 1))
    print_pass "UI app syntax valid"
else
    fail_count=$((fail_count + 1))
    print_fail "UI app has syntax errors"
fi
test_count=$((test_count + 1))

# Test 11: Check directory structure
print_test "Required directory structure"
all_dirs=true
for dir in "scripts" "ui" "config" "src" "logs" "models"; do
    if [ ! -d "$PROJECT_ROOT/$dir" ]; then
        all_dirs=false
        break
    fi
done

if [ "$all_dirs" = true ]; then
    pass_count=$((pass_count + 1))
    print_pass "All required directories exist"
else
    fail_count=$((fail_count + 1))
    print_fail "Some required directories missing"
fi
test_count=$((test_count + 1))

# Test 12: Check README updates
print_test "README contains bootstrap documentation"
if grep -q "bootstrap_ubuntu.sh" "$PROJECT_ROOT/README.md"; then
    pass_count=$((pass_count + 1))
    print_pass "README updated with bootstrap info"
else
    fail_count=$((fail_count + 1))
    print_fail "README missing bootstrap documentation"
fi
test_count=$((test_count + 1))

# Test 13: Check SETUP.md updates
print_test "SETUP.md contains bootstrap documentation"
if grep -q "bootstrap_ubuntu.sh" "$PROJECT_ROOT/SETUP.md"; then
    pass_count=$((pass_count + 1))
    print_pass "SETUP.md updated with bootstrap info"
else
    fail_count=$((fail_count + 1))
    print_fail "SETUP.md missing bootstrap documentation"
fi
test_count=$((test_count + 1))

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
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
