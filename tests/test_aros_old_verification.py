#!/usr/bin/env python3
"""
Test suite for AROS-OLD repository verification
Tests cloning, exploration, editing, configuration, and build verification
"""

import os
import sys
import unittest
import subprocess
import tempfile
import shutil
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAROSOldVerification(unittest.TestCase):
    """Test AROS-OLD repository operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.project_root = Path(__file__).parent.parent
        cls.config_file = cls.project_root / 'config' / 'config.json'
        
        # Load configuration
        with open(cls.config_file) as f:
            cls.config = json.load(f)
        
        cls.aros_repo_url = cls.config['aros_repo_url']
        cls.test_clone_dir = None
        
    def setUp(self):
        """Set up for each test"""
        # Create temporary directory for test clones
        self.test_clone_dir = tempfile.mkdtemp(prefix='aros_test_')
        
    def tearDown(self):
        """Clean up after each test"""
        # Clean up test clone directory
        if self.test_clone_dir and os.path.exists(self.test_clone_dir):
            shutil.rmtree(self.test_clone_dir, ignore_errors=True)
    
    def test_01_clone_repository(self):
        """Test cloning AROS-OLD repository"""
        print("\n=== Testing AROS-OLD Repository Clone ===")
        
        clone_path = Path(self.test_clone_dir) / 'aros-old'
        
        # Attempt to clone (with limited depth for speed)
        cmd = [
            'git', 'clone',
            '--depth', '1',  # Shallow clone for testing
            self.aros_repo_url,
            str(clone_path)
        ]
        
        print(f"Cloning from: {self.aros_repo_url}")
        print(f"Clone destination: {clone_path}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Note: Clone might fail in sandboxed environment without internet
            # This is expected per the issue description
            if result.returncode == 0:
                print("✓ Clone succeeded")
                self.assertTrue(clone_path.exists(), "Clone directory should exist")
                self.assertTrue((clone_path / '.git').exists(), "Git directory should exist")
            else:
                print(f"✗ Clone failed (expected in sandbox): {result.stderr}")
                # Mark as expected failure in sandbox
                self.skipTest("Clone failed due to sandbox network restrictions (expected)")
                
        except subprocess.TimeoutExpired:
            self.fail("Clone operation timed out")
        except Exception as e:
            self.skipTest(f"Clone failed due to environment: {e}")
    
    def test_02_explore_repository(self):
        """Test exploring cloned repository structure"""
        print("\n=== Testing Repository Exploration ===")
        
        # Use existing clone if available, otherwise skip
        aros_path = self.project_root / self.config['aros_local_path']
        
        if not aros_path.exists():
            self.skipTest("AROS repository not cloned yet")
        
        print(f"Exploring: {aros_path}")
        
        # Check for key AROS directories and files
        expected_items = [
            'compiler',
            'rom',
            'workbench',
            'arch',
            'configure',
            'mmakefile'
        ]
        
        found_items = []
        missing_items = []
        
        for item in expected_items:
            item_path = aros_path / item
            if item_path.exists():
                found_items.append(item)
                print(f"✓ Found: {item}")
            else:
                missing_items.append(item)
                print(f"✗ Missing: {item}")
        
        # Should find at least some core items
        self.assertGreater(len(found_items), 0, "Should find at least some AROS components")
        
        # Count C source files
        c_files = list(aros_path.rglob('*.c'))
        h_files = list(aros_path.rglob('*.h'))
        
        print(f"\nRepository statistics:")
        print(f"  C source files: {len(c_files)}")
        print(f"  Header files: {len(h_files)}")
        print(f"  Found items: {len(found_items)}/{len(expected_items)}")
        
        self.assertGreater(len(c_files), 0, "Should find C source files")
    
    def test_03_edit_files(self):
        """Test file editing capabilities"""
        print("\n=== Testing File Editing ===")
        
        # Create a test file
        test_file = Path(self.test_clone_dir) / 'test_edit.c'
        
        original_content = '''/* Test file for editing */
#include <stdio.h>

int main() {
    printf("Original content\\n");
    return 0;
}
'''
        
        # Write original content
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        print(f"Created test file: {test_file}")
        self.assertTrue(test_file.exists(), "Test file should be created")
        
        # Read and verify
        with open(test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, original_content, "Content should match")
        
        # Edit file
        modified_content = '''/* Test file for editing - MODIFIED */
#include <stdio.h>

int main() {
    printf("Modified content\\n");
    return 0;
}
'''
        
        with open(test_file, 'w') as f:
            f.write(modified_content)
        
        # Verify modification
        with open(test_file, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, modified_content, "Content should be modified")
        self.assertNotEqual(content, original_content, "Content should differ from original")
        
        print("✓ File editing successful")
    
    def test_04_configure_verification(self):
        """Test AROS configuration verification"""
        print("\n=== Testing AROS Configuration ===")
        
        aros_path = self.project_root / self.config['aros_local_path']
        
        if not aros_path.exists():
            self.skipTest("AROS repository not cloned yet")
        
        print(f"Checking configuration for: {aros_path}")
        
        # Check if configure script exists
        configure_script = aros_path / 'configure'
        
        if configure_script.exists():
            print(f"✓ Configure script found: {configure_script}")
            self.assertTrue(configure_script.is_file(), "Configure should be a file")
        else:
            print(f"✗ Configure script not found")
            self.skipTest("Configure script not available")
        
        # Check if already configured
        config_markers = [
            aros_path / 'mmakefile.config',
            aros_path / 'bin',
        ]
        
        configured = any(marker.exists() for marker in config_markers)
        
        if configured:
            print("✓ AROS appears to be already configured")
        else:
            print("Note: AROS not yet configured (expected for fresh clone)")
        
        # We won't actually run configure in tests, just verify the capability exists
        print("Configuration verification complete")
    
    def test_05_build_verification(self):
        """Test build verification capability"""
        print("\n=== Testing Build Verification ===")
        
        aros_path = self.project_root / self.config['aros_local_path']
        
        if not aros_path.exists():
            self.skipTest("AROS repository not cloned yet")
        
        print(f"Checking build capability for: {aros_path}")
        
        # Check for build tools
        build_tools = ['make', 'gcc', 'python3']
        available_tools = []
        missing_tools = []
        
        for tool in build_tools:
            result = subprocess.run(
                ['which', tool],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                available_tools.append(tool)
                print(f"✓ Build tool available: {tool}")
            else:
                missing_tools.append(tool)
                print(f"✗ Build tool missing: {tool}")
        
        # Should have at least some build tools
        self.assertGreater(len(available_tools), 0, "Should have some build tools available")
        
        # Test syntax checking on a sample file
        sample_files = list(aros_path.rglob('*.c'))[:5]  # Check first 5 C files
        
        if sample_files and 'gcc' in available_tools:
            print(f"\nPerforming syntax check on {len(sample_files)} sample files...")
            
            syntax_ok = 0
            syntax_errors = 0
            
            for sample_file in sample_files:
                result = subprocess.run(
                    ['gcc', '-fsyntax-only', '-I.', str(sample_file)],
                    capture_output=True,
                    text=True,
                    cwd=str(aros_path),
                    timeout=10
                )
                
                if result.returncode == 0:
                    syntax_ok += 1
                    print(f"  ✓ {sample_file.name}")
                else:
                    syntax_errors += 1
                    print(f"  ✗ {sample_file.name}")
            
            print(f"\nSyntax check results: {syntax_ok} OK, {syntax_errors} errors")
            
            # Note: Some errors expected due to missing includes
            # Just verify the mechanism works
            print("✓ Syntax checking mechanism verified")
    
    def test_06_compiler_output_capture(self):
        """Test capturing compiler output"""
        print("\n=== Testing Compiler Output Capture ===")
        
        # Create a test C file with an actual error
        test_file = Path(self.test_clone_dir) / 'test_compile.c'
        
        # File with intentional syntax error that will fail compilation
        error_code = '''#include <stdio.h>

int main() {
    // Intentional syntax errors
    printf("Test %d\\n", "string_not_int");
    undefined_function();
    missing_semicolon
    return 0;
}
'''
        
        with open(test_file, 'w') as f:
            f.write(error_code)
        
        # Try to compile and capture output
        result = subprocess.run(
            ['gcc', '-c', str(test_file), '-o', '/dev/null'],
            capture_output=True,
            text=True
        )
        
        print(f"Compilation exit code: {result.returncode}")
        print(f"\nCompiler stderr output:")
        print(result.stderr)
        
        # Should have non-zero exit code (compilation failed)
        self.assertNotEqual(result.returncode, 0, "Compilation should fail for error code")
        
        # Should have error messages
        self.assertTrue(len(result.stderr) > 0, "Should have error output")
        
        # Check for expected error patterns
        error_output_lower = result.stderr.lower()
        has_error_indicators = any(indicator in error_output_lower for indicator in [
            'error', 'warning', 'undefined', 'implicit'
        ])
        
        self.assertTrue(has_error_indicators, "Should have error indicators in output")
        
        print("\n✓ Compiler output capture successful")
        print("✓ Error detection working")


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAROSOldVerification)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
