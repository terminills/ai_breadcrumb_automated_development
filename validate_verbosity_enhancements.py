#!/usr/bin/env python3
"""
Validation script for verbosity enhancements
Checks that the enhanced logging is properly integrated
"""

import sys
import re
from pathlib import Path

def check_file_for_patterns(file_path, patterns, description):
    """Check if file contains expected logging patterns"""
    print(f"\n📋 Checking {description}: {file_path.name}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    found = []
    missing = []
    
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, content, re.MULTILINE):
            found.append(pattern_name)
            print(f"  ✓ Found: {pattern_name}")
        else:
            missing.append(pattern_name)
            print(f"  ✗ Missing: {pattern_name}")
    
    return len(missing) == 0, found, missing

def main():
    """Main validation"""
    print("="*70)
    print("Validating Enhanced Verbosity Implementation")
    print("="*70)
    
    base_path = Path(__file__).parent
    
    # Check interactive_session.py
    session_patterns = {
        "Exploration file logging": r"logger\.info.*Analyzing:.*relative_to",
        "File size logging": r"logger\.info.*bytes.*lines",
        "Breadcrumb count logging": r"logger\.info.*breadcrumbs",
        "Reasoning context logging": r"logger\.info.*Context available",
        "Generation statistics": r"logger\.info.*Generated:.*characters",
        "Code preview": r"logger\.info.*preview:",
        "Review findings": r"logger\.info.*Review.*preview:",
    }
    
    session_file = base_path / "src" / "interactive_session.py"
    session_ok, found, missing = check_file_for_patterns(
        session_file, 
        session_patterns,
        "Session Manager enhancements"
    )
    
    # Check copilot_iteration.py
    iteration_patterns = {
        "Phase headers": r"PHASE \d+:.*-",
        "Exploration results": r"📊 Exploration Results",
        "Files examined list": r"📁 Files Examined",
        "Key insights": r"💡 Key Insights",
        "Strategy formulated": r"📝 Strategy Formulated",
        "Code statistics": r"📊 Generation Statistics",
        "Review complete": r"📋 Review Complete",
        "Compilation status": r"Compilation.*SUCCESSFUL|FAILED",
    }
    
    iteration_file = base_path / "src" / "copilot_iteration.py"
    iteration_ok, found2, missing2 = check_file_for_patterns(
        iteration_file,
        iteration_patterns,
        "Copilot Iteration enhancements"
    )
    
    # Check UI template
    ui_patterns = {
        "Detailed exploration logging": r"exploration\.files_examined",
        "Generation details": r"generation\.length",
        "Review details": r"review\.has_errors",
        "Compilation details": r"compilation\.success",
        "Toggle details function": r"(async )?function toggleDetails",
    }
    
    ui_file = base_path / "ui" / "templates" / "sessions.html"
    ui_ok, found3, missing3 = check_file_for_patterns(
        ui_file,
        ui_patterns,
        "UI template enhancements"
    )
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    total_checks = len(session_patterns) + len(iteration_patterns) + len(ui_patterns)
    total_found = len(found) + len(found2) + len(found3)
    
    print(f"\nTotal checks: {total_checks}")
    print(f"Passed: {total_found}")
    print(f"Failed: {total_checks - total_found}")
    
    if session_ok and iteration_ok and ui_ok:
        print("\n✅ All validation checks passed!")
        print("\nThe enhanced verbosity features are properly implemented:")
        print("  • Detailed exploration logging with file lists")
        print("  • Reasoning phase shows context and strategy")
        print("  • Generation displays code statistics and preview")
        print("  • Review shows detailed findings")
        print("  • Compilation logs detailed results")
        print("  • UI displays all enhanced information")
        return 0
    else:
        print("\n⚠ Some validation checks failed")
        if not session_ok:
            print(f"  Session Manager: {len(missing)} issues")
        if not iteration_ok:
            print(f"  Copilot Iteration: {len(missing2)} issues")
        if not ui_ok:
            print(f"  UI Template: {len(missing3)} issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
