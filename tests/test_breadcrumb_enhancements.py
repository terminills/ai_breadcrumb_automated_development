#!/usr/bin/env python3
"""
Test script for breadcrumb enhancements
Tests AI_BREADCRUMB tag and bidirectional mapping functionality
"""

import sys
import tempfile
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.breadcrumb_parser.parser import BreadcrumbParser, TAG_SET


def test_ai_breadcrumb_tag_in_tagset():
    """Test that AI_BREADCRUMB is in the TAG_SET"""
    print("\n=== Testing AI_BREADCRUMB Tag in TAG_SET ===")
    
    assert 'AI_BREADCRUMB' in TAG_SET
    print("✓ AI_BREADCRUMB tag exists in TAG_SET")
    return True


def test_parse_ai_breadcrumb():
    """Test parsing AI_BREADCRUMB tag from source file"""
    print("\n=== Testing AI_BREADCRUMB Parsing ===")
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
// AI_PHASE: GRAPHICS_PIPELINE
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: shader_compilation_v1
// AI_NOTE: Basic shader compilation working
static void compile_shader() {
    // Implementation
}
""")
        test_file = f.name
    
    try:
        parser = BreadcrumbParser()
        breadcrumbs = parser.parse_file(test_file)
        
        assert len(breadcrumbs) > 0, "Should parse at least one breadcrumb"
        
        bc = breadcrumbs[0]
        assert bc.ai_breadcrumb == "shader_compilation_v1", f"Expected 'shader_compilation_v1', got {bc.ai_breadcrumb}"
        assert bc.phase == "GRAPHICS_PIPELINE"
        assert bc.status == "IMPLEMENTED"
        
        print(f"✓ Parsed AI_BREADCRUMB: {bc.ai_breadcrumb}")
        print(f"✓ Breadcrumb location: {bc.file_path}:{bc.line_number}")
        return True
        
    finally:
        Path(test_file).unlink()


def test_breadcrumb_map():
    """Test bidirectional breadcrumb mapping"""
    print("\n=== Testing Breadcrumb Map ===")
    
    # Create temporary test files with related breadcrumbs
    with tempfile.NamedTemporaryFile(mode='w', suffix='_a.c', delete=False) as f:
        f.write("""
// AI_PHASE: SHADER_INIT
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: shader_system
// AI_NOTE: Shader initialization
void init_shader() {}
""")
        test_file_a = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_b.c', delete=False) as f:
        f.write("""
// AI_PHASE: SHADER_COMPILE
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: shader_system
// AI_NOTE: Shader compilation
void compile_shader() {}
""")
        test_file_b = f.name
    
    try:
        parser = BreadcrumbParser()
        parser.parse_file(test_file_a)
        parser.parse_file(test_file_b)
        
        breadcrumb_map = parser.get_breadcrumb_map()
        
        assert 'shader_system' in breadcrumb_map, "Should have shader_system marker in map"
        assert len(breadcrumb_map['shader_system']) == 2, "Should have 2 breadcrumbs with shader_system marker"
        
        print(f"✓ Breadcrumb map created with {len(breadcrumb_map)} markers")
        print(f"✓ 'shader_system' marker has {len(breadcrumb_map['shader_system'])} breadcrumbs")
        return True
        
    finally:
        Path(test_file_a).unlink()
        Path(test_file_b).unlink()


def test_find_related_breadcrumbs():
    """Test finding related breadcrumbs bidirectionally"""
    print("\n=== Testing Find Related Breadcrumbs ===")
    
    # Create test files with various relationships
    with tempfile.NamedTemporaryFile(mode='w', suffix='_init.c', delete=False) as f:
        f.write("""
// AI_PHASE: MEMORY_INIT
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: memory_system
// AI_BLOCKS: SHADER_COMPILE
void init_memory() {}
""")
        test_file_init = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_compile.c', delete=False) as f:
        f.write("""
// AI_PHASE: SHADER_COMPILE
// AI_STATUS: PARTIAL
// AI_BREADCRUMB: memory_system
// AI_DEPENDENCIES: MEMORY_INIT
void compile_shader() {}
""")
        test_file_compile = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_alloc.c', delete=False) as f:
        f.write("""
// AI_PHASE: MEMORY_ALLOC
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: memory_system
void alloc_memory() {}
""")
        test_file_alloc = f.name
    
    try:
        parser = BreadcrumbParser()
        parser.parse_file(test_file_init)
        parser.parse_file(test_file_compile)
        parser.parse_file(test_file_alloc)
        
        # Get the first breadcrumb (MEMORY_INIT)
        init_bc = [bc for bc in parser.breadcrumbs if bc.phase == 'MEMORY_INIT'][0]
        
        # Find related breadcrumbs
        related = parser.find_related_breadcrumbs(init_bc)
        
        assert len(related) > 0, "Should find related breadcrumbs"
        
        # Should find at least the SHADER_COMPILE that depends on it
        phases = [bc.phase for bc in related]
        
        print(f"✓ Found {len(related)} related breadcrumbs")
        print(f"✓ Related phases: {', '.join(phases)}")
        
        # Verify bidirectional relationship
        compile_bc = [bc for bc in parser.breadcrumbs if bc.phase == 'SHADER_COMPILE'][0]
        related_to_compile = parser.find_related_breadcrumbs(compile_bc)
        
        # Should find MEMORY_INIT since SHADER_COMPILE depends on it
        init_phases = [bc.phase for bc in related_to_compile if bc.phase == 'MEMORY_INIT']
        assert len(init_phases) > 0, "Should find MEMORY_INIT from SHADER_COMPILE (bidirectional)"
        
        print("✓ Bidirectional relationships verified")
        return True
        
    finally:
        Path(test_file_init).unlink()
        Path(test_file_compile).unlink()
        Path(test_file_alloc).unlink()


def test_reference_based_relationships():
    """Test finding relationships based on reference tags"""
    print("\n=== Testing Reference-Based Relationships ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_a.c', delete=False) as f:
        f.write("""
// AI_PHASE: GPU_INIT
// AI_STATUS: IMPLEMENTED
// LINUX_REF: drivers/gpu/drm/amd/amdgpu/amdgpu_device.c
void init_gpu() {}
""")
        test_file_a = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_b.c', delete=False) as f:
        f.write("""
// AI_PHASE: GPU_PROBE
// AI_STATUS: IMPLEMENTED
// LINUX_REF: drivers/gpu/drm/amd/amdgpu/amdgpu_device.c
void probe_gpu() {}
""")
        test_file_b = f.name
    
    try:
        parser = BreadcrumbParser()
        parser.parse_file(test_file_a)
        parser.parse_file(test_file_b)
        
        # Get GPU_INIT breadcrumb
        init_bc = [bc for bc in parser.breadcrumbs if bc.phase == 'GPU_INIT'][0]
        
        # Find related by LINUX_REF
        related = parser.find_related_breadcrumbs(init_bc)
        
        # Should find GPU_PROBE with same LINUX_REF
        phases = [bc.phase for bc in related]
        assert 'GPU_PROBE' in phases, "Should find GPU_PROBE with same LINUX_REF"
        
        print(f"✓ Found related breadcrumbs by LINUX_REF: {', '.join(phases)}")
        return True
        
    finally:
        Path(test_file_a).unlink()
        Path(test_file_b).unlink()


def test_block_comment_ai_breadcrumb():
    """Test AI_BREADCRUMB in block comments"""
    print("\n=== Testing AI_BREADCRUMB in Block Comments ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
/*
 * AI_PHASE: TEXTURE_UPLOAD
 * AI_STATUS: IMPLEMENTED
 * AI_BREADCRUMB: texture_system
 * AI_NOTE: Texture upload implementation
 */
void upload_texture() {}
""")
        test_file = f.name
    
    try:
        parser = BreadcrumbParser()
        breadcrumbs = parser.parse_file(test_file)
        
        assert len(breadcrumbs) > 0, "Should parse breadcrumb from block comment"
        
        bc = breadcrumbs[0]
        assert bc.ai_breadcrumb == "texture_system"
        assert bc.phase == "TEXTURE_UPLOAD"
        
        print(f"✓ Parsed AI_BREADCRUMB from block comment: {bc.ai_breadcrumb}")
        return True
        
    finally:
        Path(test_file).unlink()


def test_multiple_markers():
    """Test handling multiple different AI_BREADCRUMB markers"""
    print("\n=== Testing Multiple Markers ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write("""
// AI_PHASE: INIT_A
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: system_a
void init_a() {}

// AI_PHASE: INIT_B
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: system_b
void init_b() {}

// AI_PHASE: UTIL_A
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: system_a
void util_a() {}
""")
        test_file = f.name
    
    try:
        parser = BreadcrumbParser()
        breadcrumbs = parser.parse_file(test_file)
        
        assert len(breadcrumbs) == 3, f"Should parse 3 breadcrumbs, got {len(breadcrumbs)}"
        
        breadcrumb_map = parser.get_breadcrumb_map()
        
        assert 'system_a' in breadcrumb_map, "Should have system_a marker"
        assert 'system_b' in breadcrumb_map, "Should have system_b marker"
        assert len(breadcrumb_map['system_a']) == 2, "system_a should have 2 breadcrumbs"
        assert len(breadcrumb_map['system_b']) == 1, "system_b should have 1 breadcrumb"
        
        print(f"✓ Handled multiple markers correctly")
        print(f"✓ system_a: {len(breadcrumb_map['system_a'])} breadcrumbs")
        print(f"✓ system_b: {len(breadcrumb_map['system_b'])} breadcrumbs")
        return True
        
    finally:
        Path(test_file).unlink()


def run_all_tests():
    """Run all breadcrumb enhancement tests"""
    print("=" * 60)
    print("  Breadcrumb Enhancement Test Suite")
    print("=" * 60)
    
    tests = [
        test_ai_breadcrumb_tag_in_tagset,
        test_parse_ai_breadcrumb,
        test_breadcrumb_map,
        test_find_related_breadcrumbs,
        test_reference_based_relationships,
        test_block_comment_ai_breadcrumb,
        test_multiple_markers,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
