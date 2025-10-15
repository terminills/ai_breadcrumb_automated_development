#!/usr/bin/env python3
"""
Test script for breadcrumb parser
Validates that the parser correctly extracts breadcrumbs from sample files
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.breadcrumb_parser import BreadcrumbParser, BreadcrumbValidator

def test_parser():
    """Test basic parser functionality"""
    print("Testing Breadcrumb Parser...")
    print("=" * 60)
    
    parser = BreadcrumbParser()
    validator = BreadcrumbValidator()
    
    # Test with sample files
    sample_dir = Path(__file__).parent.parent / 'aros-src'
    
    if not sample_dir.exists():
        print("❌ Sample directory not found. Creating test file...")
        sample_dir.mkdir(exist_ok=True)
        
        # Create a test file
        test_file = sample_dir / 'test.c'
        test_file.write_text("""
// AI_PHASE: TEST_PHASE
// AI_STATUS: IMPLEMENTED
// AI_STRATEGY: Test strategy
static void test_function(void) {
    // Test implementation
}
""")
        print(f"✓ Created test file: {test_file}")
    
    # Parse files
    c_files = list(sample_dir.glob('*.c'))
    print(f"\nFound {len(c_files)} C files in {sample_dir}")
    
    total_breadcrumbs = 0
    for c_file in c_files:
        breadcrumbs = parser.parse_file(str(c_file))
        total_breadcrumbs += len(breadcrumbs)
        if breadcrumbs:
            print(f"  ✓ {c_file.name}: {len(breadcrumbs)} breadcrumbs")
    
    print(f"\nTotal breadcrumbs found: {total_breadcrumbs}")
    
    # Validate
    if parser.breadcrumbs:
        print("\nValidating breadcrumbs...")
        validator.validate_breadcrumbs(parser.breadcrumbs)
        report = validator.get_report()
        
        if report['valid']:
            print(f"✅ All {len(parser.breadcrumbs)} breadcrumbs are valid!")
        else:
            print(f"⚠️  Validation errors: {report['error_count']}")
            for error in report['errors'][:5]:
                print(f"   - {error}")
    
    # Get statistics
    stats = parser.get_statistics()
    print("\nStatistics:")
    print(f"  Total: {stats['total_breadcrumbs']}")
    print(f"  Files: {stats['files_with_breadcrumbs']}")
    
    if stats['phases']:
        print(f"  Phases: {len(stats['phases'])}")
        for phase, count in list(stats['phases'].items())[:5]:
            print(f"    - {phase}: {count}")
    
    if stats['statuses']:
        print(f"  Statuses: {len(stats['statuses'])}")
        for status, count in stats['statuses'].items():
            print(f"    - {status}: {count}")
    
    print("\n" + "=" * 60)
    print("✅ Parser test complete!")
    
    return len(parser.breadcrumbs) > 0

def test_api_imports():
    """Test that API modules can be imported"""
    print("\nTesting API imports...")
    print("=" * 60)
    
    try:
        from src.compiler_loop import ErrorTracker, ReasoningTracker
        print("✓ ErrorTracker imported")
        print("✓ ReasoningTracker imported")
        
        # Test instantiation
        error_tracker = ErrorTracker('./logs/errors')
        print("✓ ErrorTracker instantiated")
        
        reasoning_tracker = ReasoningTracker('./logs/reasoning')
        print("✓ ReasoningTracker instantiated")
        
        print("\n✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BREADCRUMB PARSER TEST SUITE")
    print("=" * 60 + "\n")
    
    tests_passed = 0
    tests_total = 2
    
    # Test 1: Parser functionality
    if test_parser():
        tests_passed += 1
    
    # Test 2: API imports
    if test_api_imports():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {tests_passed}/{tests_total} tests passed")
    print("=" * 60)
    
    return 0 if tests_passed == tests_total else 1

if __name__ == '__main__':
    sys.exit(main())
