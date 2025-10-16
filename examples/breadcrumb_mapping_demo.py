#!/usr/bin/env python3
"""
Demonstration of AI Breadcrumb Bidirectional Mapping
Shows how breadcrumbs act as a map for navigating related code components
"""

import sys
import tempfile
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.breadcrumb_parser.parser import BreadcrumbParser


def create_demo_files():
    """Create demo files with breadcrumb relationships"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create shader initialization file
    (temp_dir / 'shader_init.c').write_text("""
// AI_PHASE: SHADER_INIT
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: graphics_pipeline_v2
// AI_NOTE: Initialize shader compilation system
// AI_BLOCKS: SHADER_COMPILE, RENDER_PIPELINE
// LINUX_REF: drivers/gpu/drm/amd/amdgpu/amdgpu_shader.c
static void init_shader_system(void) {
    // Initialize shader compiler
}
""")
    
    # Create shader compilation file
    (temp_dir / 'shader_compile.c').write_text("""
// AI_PHASE: SHADER_COMPILE
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: graphics_pipeline_v2
// AI_DEPENDENCIES: SHADER_INIT
// AI_NOTE: Compile shader programs
// LINUX_REF: drivers/gpu/drm/amd/amdgpu/amdgpu_shader.c
static void compile_shader(const char *source) {
    // Shader compilation logic
}
""")
    
    # Create render pipeline file
    (temp_dir / 'render_pipeline.c').write_text("""
// AI_PHASE: RENDER_PIPELINE
// AI_STATUS: PARTIAL
// AI_BREADCRUMB: graphics_pipeline_v2
// AI_DEPENDENCIES: SHADER_INIT, SHADER_COMPILE
// AI_NOTE: Main rendering pipeline
static void render_frame(void) {
    // Rendering logic
}
""")
    
    # Create texture system file (different breadcrumb)
    (temp_dir / 'texture_upload.c').write_text("""
// AI_PHASE: TEXTURE_UPLOAD
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: texture_system_v1
// AI_NOTE: Texture upload and management
static void upload_texture(void *data, int width, int height) {
    // Texture upload logic
}
""")
    
    # Create memory management file (related through reference)
    (temp_dir / 'memory_manager.c').write_text("""
// AI_PHASE: MEMORY_INIT
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: memory_system
// AI_BLOCKS: SHADER_INIT
// AI_NOTE: Memory pool initialization
static void init_memory_pools(void) {
    // Memory initialization
}
""")
    
    return temp_dir


def demo_bidirectional_mapping():
    """Demonstrate bidirectional breadcrumb mapping"""
    print("=" * 70)
    print("  AI Breadcrumb Bidirectional Mapping Demo")
    print("=" * 70)
    
    # Create demo files
    temp_dir = create_demo_files()
    
    try:
        # Parse all files
        parser = BreadcrumbParser()
        for file in temp_dir.glob('*.c'):
            parser.parse_file(str(file))
        
        print(f"\n📁 Parsed {len(parser.breadcrumbs)} breadcrumbs from {len(list(temp_dir.glob('*.c')))} files\n")
        
        # Show breadcrumb map
        print("🗺️  Breadcrumb Map (grouping by AI_BREADCRUMB markers):")
        print("-" * 70)
        breadcrumb_map = parser.get_breadcrumb_map()
        
        for marker, breadcrumbs in breadcrumb_map.items():
            print(f"\n  Marker: '{marker}'")
            print(f"  Components: {len(breadcrumbs)}")
            for bc in breadcrumbs:
                file_name = Path(bc.file_path).name
                print(f"    - {bc.phase} in {file_name} (line {bc.line_number})")
        
        # Demonstrate finding related breadcrumbs
        print("\n\n🔗 Finding Related Breadcrumbs:")
        print("-" * 70)
        
        # Find SHADER_INIT breadcrumb
        shader_init = [bc for bc in parser.breadcrumbs if bc.phase == 'SHADER_INIT'][0]
        print(f"\n  Starting from: {shader_init.phase}")
        print(f"  File: {Path(shader_init.file_path).name}")
        print(f"  Breadcrumb: {shader_init.ai_breadcrumb}")
        
        # Find related breadcrumbs
        related = parser.find_related_breadcrumbs(shader_init)
        
        print(f"\n  Found {len(related)} related breadcrumbs:")
        for bc in related:
            file_name = Path(bc.file_path).name
            relationship = []
            
            # Determine relationship type
            if bc.ai_breadcrumb == shader_init.ai_breadcrumb:
                relationship.append("same marker")
            if bc.ai_dependencies:
                deps = [d.strip() for d in bc.ai_dependencies.split(',')]
                if shader_init.phase in deps:
                    relationship.append("depends on this")
            if shader_init.ai_blocks:
                blocks = [b.strip() for b in shader_init.ai_blocks.split(',')]
                if bc.phase in blocks:
                    relationship.append("blocked by this")
            if bc.linux_ref == shader_init.linux_ref:
                relationship.append("same LINUX_REF")
            
            rel_str = ", ".join(relationship) if relationship else "indirect"
            print(f"    - {bc.phase} in {file_name} ({rel_str})")
        
        # Demonstrate bidirectional navigation
        print("\n\n🔄 Bidirectional Navigation:")
        print("-" * 70)
        
        render_pipeline = [bc for bc in parser.breadcrumbs if bc.phase == 'RENDER_PIPELINE'][0]
        print(f"\n  Starting from: {render_pipeline.phase}")
        print(f"  Dependencies: {render_pipeline.ai_dependencies}")
        
        related_to_render = parser.find_related_breadcrumbs(render_pipeline)
        print(f"\n  Found {len(related_to_render)} related breadcrumbs:")
        for bc in related_to_render:
            file_name = Path(bc.file_path).name
            print(f"    - {bc.phase} in {file_name}")
        
        # Show statistics
        print("\n\n📊 Statistics:")
        print("-" * 70)
        stats = parser.get_statistics()
        print(f"  Total breadcrumbs: {stats['total_breadcrumbs']}")
        print(f"  Files with breadcrumbs: {stats['files_with_breadcrumbs']}")
        print(f"  Unique phases: {len(stats['phases'])}")
        print(f"  Breadcrumb markers: {len(breadcrumb_map)}")
        
        print("\n  Phases:")
        for phase, count in stats['phases'].items():
            print(f"    - {phase}: {count}")
        
        print("\n  Statuses:")
        for status, count in stats['statuses'].items():
            print(f"    - {status}: {count}")
        
        print("\n" + "=" * 70)
        print("✅ Demo complete! Breadcrumbs successfully act as a bidirectional map.")
        print("=" * 70)
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    demo_bidirectional_mapping()
