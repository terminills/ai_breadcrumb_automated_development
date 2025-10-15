#!/usr/bin/env python3
"""
Scan AROS source files for AI breadcrumbs
This script scans the aros-src directory and extracts breadcrumb metadata
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.breadcrumb_parser import BreadcrumbParser, BreadcrumbValidator

def scan_directory(directory_path: Path, max_files: int = None, extensions: list = None):
    """
    Scan a directory for files with breadcrumbs
    
    Args:
        directory_path: Path to directory to scan
        max_files: Maximum number of files to scan (None for all)
        extensions: List of file extensions to scan (default: ['.c', '.h'])
    
    Returns:
        Tuple of (parser, validator) with results
    """
    if extensions is None:
        extensions = ['.c', '.h', '.cpp', '.hpp']
    
    parser = BreadcrumbParser()
    validator = BreadcrumbValidator()
    
    print(f"Scanning directory: {directory_path}")
    print(f"Looking for extensions: {', '.join(extensions)}")
    print("")
    
    # Find all matching files
    all_files = []
    for ext in extensions:
        all_files.extend(directory_path.rglob(f'*{ext}'))
    
    if max_files:
        all_files = all_files[:max_files]
    
    print(f"Found {len(all_files)} files to scan")
    print("")
    
    # Parse each file
    files_with_breadcrumbs = 0
    for i, file_path in enumerate(all_files, 1):
        try:
            breadcrumbs = parser.parse_file(str(file_path))
            if breadcrumbs:
                files_with_breadcrumbs += 1
                print(f"[{i}/{len(all_files)}] ✓ {file_path.name}: {len(breadcrumbs)} breadcrumbs")
            else:
                print(f"[{i}/{len(all_files)}]   {file_path.name}: no breadcrumbs")
        except Exception as e:
            print(f"[{i}/{len(all_files)}] ✗ {file_path.name}: Error - {e}")
    
    print("")
    print(f"Scanned {len(all_files)} files")
    print(f"Files with breadcrumbs: {files_with_breadcrumbs}")
    print(f"Total breadcrumbs found: {len(parser.breadcrumbs)}")
    print("")
    
    # Validate breadcrumbs
    if parser.breadcrumbs:
        print("Validating breadcrumbs...")
        validator.validate_breadcrumbs(parser.breadcrumbs)
        report = validator.get_report()
        
        valid_count = len(parser.breadcrumbs) - report['error_count']
        print(f"✓ Valid breadcrumbs: {valid_count}")
        print(f"✗ Error count: {report['error_count']}")
        print(f"⚠ Warning count: {report['warning_count']}")
        
        if report['errors']:
            print("\nValidation Errors:")
            for error in report['errors'][:10]:  # Show first 10 errors
                print(f"  - {error['file']}:{error['line']}: {error['error']}")
        
        if report['warnings']:
            print("\nValidation Warnings:")
            for warning in report['warnings'][:10]:  # Show first 10 warnings
                print(f"  - {warning['file']}:{warning['line']}: {warning['warning']}")
    
    return parser, validator

def print_statistics(parser: BreadcrumbParser):
    """Print detailed statistics about parsed breadcrumbs"""
    stats = parser.get_statistics()
    
    print("\n" + "="*60)
    print("BREADCRUMB STATISTICS")
    print("="*60)
    
    print(f"\nTotal Breadcrumbs: {stats['total_breadcrumbs']}")
    print(f"Files with Breadcrumbs: {stats['files_with_breadcrumbs']}")
    
    if stats['phases']:
        print("\nBy Phase:")
        for phase, count in sorted(stats['phases'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {phase}: {count}")
    
    if stats['statuses']:
        print("\nBy Status:")
        for status, count in sorted(stats['statuses'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count}")

def export_to_json(parser: BreadcrumbParser, output_file: Path):
    """Export breadcrumbs to JSON file"""
    data = {
        'statistics': parser.get_statistics(),
        'breadcrumbs': [
            {
                'file_path': b.file_path,
                'line_number': b.line_number,
                'phase': b.phase,
                'status': b.status,
                'pattern': b.pattern,
                'strategy': b.strategy,
                'details': b.details,
                'ai_note': b.ai_note,
                'ai_version': b.ai_version,
                'compiler_err': b.compiler_err,
                'runtime_err': b.runtime_err,
                'fix_reason': b.fix_reason,
                'linux_ref': b.linux_ref,
                'amigaos_ref': b.amigaos_ref,
                'aros_impl': b.aros_impl,
                'ai_priority': b.ai_priority,
                'ai_complexity': b.ai_complexity,
                'ai_dependencies': b.ai_dependencies,
                'ai_blocks': b.ai_blocks
            }
            for b in parser.breadcrumbs
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Exported {len(parser.breadcrumbs)} breadcrumbs to {output_file}")

def main():
    """Main entry point"""
    import argparse
    
    parser_args = argparse.ArgumentParser(
        description='Scan AROS source files for AI breadcrumbs'
    )
    parser_args.add_argument(
        'directory',
        nargs='?',
        default='./aros-src',
        help='Directory to scan (default: ./aros-src)'
    )
    parser_args.add_argument(
        '--max-files',
        type=int,
        help='Maximum number of files to scan'
    )
    parser_args.add_argument(
        '--output',
        '-o',
        default='breadcrumbs.json',
        help='Output JSON file for breadcrumb data (default: breadcrumbs.json)'
    )
    parser_args.add_argument(
        '--extensions',
        nargs='+',
        default=['.c', '.h', '.cpp', '.hpp'],
        help='File extensions to scan (default: .c .h .cpp .hpp)'
    )
    
    args = parser_args.parse_args()
    
    # Resolve directory path
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        return 1
    
    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        return 1
    
    # Scan directory
    parser, validator = scan_directory(
        directory,
        max_files=args.max_files,
        extensions=args.extensions
    )
    
    # Print statistics
    print_statistics(parser)
    
    # Export to JSON (always export, default to breadcrumbs.json)
    output_file = Path(args.output)
    export_to_json(parser, output_file)
    
    print("\n" + "="*60)
    print("✓ Scan complete!")
    print("="*60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
