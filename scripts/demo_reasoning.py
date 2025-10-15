#!/usr/bin/env python3
"""
Demo script to populate reasoning tracker with example data
This demonstrates the thought process logging system in action
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compiler_loop import ReasoningTracker

def demo_thought_process_logging():
    """Demonstrate thought process logging with realistic examples"""
    
    print("="*70)
    print("AI THOUGHT PROCESS LOGGING DEMONSTRATION")
    print("="*70)
    print()
    
    # Initialize tracker
    tracker = ReasoningTracker("logs/reasoning")
    print("✓ Initialized reasoning tracker at logs/reasoning")
    print()
    
    # Example 1: Successful shader compilation reasoning
    print("Example 1: Shader Compilation Error Resolution")
    print("-"*70)
    
    reasoning_id_1 = tracker.start_reasoning(
        task_id="shader_compilation_nir_support",
        phase="analyzing",
        breadcrumbs_consulted=[
            "AI_PHASE: GRAPHICS_PIPELINE",
            "AI_STATUS: PARTIAL",
            "AI_PATTERN: SHADER_V2",
            "AI_NOTE: Basic LLVM working, missing NIR parsing",
            "LINUX_REF: src/gallium/drivers/radeonsi/si_shader.c"
        ],
        error_context="undefined reference to `nir_shader_get_entrypoint`",
        files_considered=["si_shader.c", "si_shader.h", "radeon_shader.h"]
    )
    
    print(f"Started reasoning: {reasoning_id_1}")
    
    # AI's reasoning steps
    tracker.add_reasoning_step("Error indicates missing NIR function")
    tracker.add_reasoning_step("Breadcrumb says NIR parsing not implemented yet")
    tracker.add_reasoning_step("Linux reference shows NIR initialization in si_shader_create()")
    tracker.add_reasoning_step("Need to add NIR parser before LLVM compilation stage")
    
    print("Added 4 reasoning steps")
    
    # Patterns identified
    tracker.add_pattern("SHADER_V2")
    tracker.add_pattern("NIR_INTEGRATION")
    print("Identified patterns: SHADER_V2, NIR_INTEGRATION")
    
    # Decision
    tracker.set_decision(
        decision_type="add_nir_parser",
        approach="follow_linux_pattern_si_shader_c",
        confidence=0.87,
        complexity="MEDIUM",
        raw_thought="Follow Linux pattern in si_shader.c lines 245-267. Add nir_shader_parse() call before LLVM stage."
    )
    
    print("Decision: add_nir_parser (87% confidence)")
    
    # Simulate implementation delay
    time.sleep(0.5)
    
    # Complete successfully
    tracker.complete_reasoning(reasoning_id_1, success=True, iterations=3)
    print("✓ Reasoning completed successfully (3 iterations)")
    print()
    
    # Example 2: Memory allocation pattern
    print("Example 2: Memory Allocation Fix")
    print("-"*70)
    
    reasoning_id_2 = tracker.start_reasoning(
        task_id="memory_alignment_fix",
        phase="implementing",
        breadcrumbs_consulted=[
            "AI_PATTERN: MEMORY_V3",
            "AI_NOTE: All allocations must be 64-byte aligned for DMA",
            "FIX_REASON: Stack corruption due to alignment on 64-bit"
        ],
        error_context="Bus error: alignment fault at 0x12345678",
        files_considered=["radeon_mem.c", "aros_mem.c"]
    )
    
    print(f"Started reasoning: {reasoning_id_2}")
    
    tracker.add_reasoning_step("Memory alignment error detected")
    tracker.add_reasoning_step("Breadcrumb indicates 64-byte alignment requirement")
    tracker.add_reasoning_step("Current allocation not aligned for DMA")
    tracker.add_reasoning_step("Apply MEMORY_V3 pattern with proper alignment")
    
    tracker.add_pattern("MEMORY_V3")
    tracker.add_pattern("DMA_SAFE")
    
    tracker.set_decision(
        decision_type="fix_memory_alignment",
        approach="apply_memory_v3_pattern",
        confidence=0.92,
        complexity="LOW",
        raw_thought="Use AllocVecAligned with 64-byte boundary as per MEMORY_V3 pattern"
    )
    
    print("Decision: fix_memory_alignment (92% confidence)")
    
    time.sleep(0.3)
    
    tracker.complete_reasoning(reasoning_id_2, success=True, iterations=2)
    print("✓ Reasoning completed successfully (2 iterations)")
    print()
    
    # Example 3: Failed reasoning - missing information
    print("Example 3: DMA Initialization (Failed - Missing Info)")
    print("-"*70)
    
    reasoning_id_3 = tracker.start_reasoning(
        task_id="dma_engine_init",
        phase="analyzing",
        breadcrumbs_consulted=[
            "AI_PHASE: DMA_SETUP",
            "AI_STATUS: NOT_STARTED",
            "AI_NOTE: Requires hardware registers"
        ],
        error_context="DMA transfer failed: timeout",
        files_considered=["radeon_dma.c"]
    )
    
    print(f"Started reasoning: {reasoning_id_3}")
    
    tracker.add_reasoning_step("DMA transfer timing out")
    tracker.add_reasoning_step("No specific hardware register addresses in breadcrumbs")
    tracker.add_reasoning_step("Attempted standard DMA initialization")
    tracker.add_reasoning_step("Missing hardware-specific configuration")
    
    tracker.add_pattern("DMA_SAFE")
    
    tracker.set_decision(
        decision_type="init_dma_engine",
        approach="standard_dma_setup",
        confidence=0.45,  # Low confidence - missing info
        complexity="HIGH",
        raw_thought="Attempting standard DMA init, but lacking hardware register addresses"
    )
    
    print("Decision: init_dma_engine (45% confidence - LOW!)")
    
    time.sleep(0.3)
    
    tracker.complete_reasoning(reasoning_id_3, success=False, iterations=5)
    print("✗ Reasoning failed after 5 iterations (missing breadcrumb info)")
    print()
    
    # Example 4: Successful pattern reuse
    print("Example 4: IRQ Handler Pattern Reuse")
    print("-"*70)
    
    reasoning_id_4 = tracker.start_reasoning(
        task_id="vblank_irq_handler",
        phase="implementing",
        breadcrumbs_consulted=[
            "AI_PATTERN: IRQ_HANDLER_V2",
            "AI_STRATEGY: Use atomic operations for IRQ safety",
            "LINUX_REF: drivers/gpu/drm/radeon/radeon_irq.c"
        ],
        error_context=None,  # Proactive implementation
        files_considered=["radeon_irq.c", "vblank.c"]
    )
    
    print(f"Started reasoning: {reasoning_id_4}")
    
    tracker.add_reasoning_step("Implementing VBlank IRQ handler")
    tracker.add_reasoning_step("IRQ_HANDLER_V2 pattern applies")
    tracker.add_reasoning_step("Pattern requires atomic operations")
    tracker.add_reasoning_step("Linux reference confirms approach")
    
    tracker.add_pattern("IRQ_HANDLER_V2")
    tracker.add_pattern("ATOMIC_OPS")
    
    tracker.set_decision(
        decision_type="implement_irq_handler",
        approach="reuse_irq_handler_v2_pattern",
        confidence=0.95,  # High confidence - clear pattern
        complexity="LOW",
        raw_thought="Direct application of proven IRQ_HANDLER_V2 pattern with atomic operations"
    )
    
    print("Decision: implement_irq_handler (95% confidence)")
    
    time.sleep(0.3)
    
    tracker.complete_reasoning(reasoning_id_4, success=True, iterations=1)
    print("✓ Reasoning completed successfully (1 iteration - pattern reuse!)")
    print()
    
    # Display statistics
    print("="*70)
    print("REASONING STATISTICS")
    print("="*70)
    
    stats = tracker.get_statistics()
    print(f"Total Reasoning Events: {stats['total_reasoning_events']}")
    print(f"Successful Decisions: {stats['successful_decisions']}")
    print(f"Failed Decisions: {stats['failed_decisions']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print()
    
    print("Pattern Usage Statistics:")
    print("-"*70)
    for pattern, pattern_stats in stats['pattern_usage'].items():
        print(f"  {pattern}:")
        print(f"    Uses: {pattern_stats['uses']}")
        print(f"    Success Rate: {pattern_stats['success_rate']:.1%}")
    print()
    
    print("Breadcrumb Effectiveness:")
    print("-"*70)
    for bc, bc_stats in stats['breadcrumb_effectiveness'].items():
        if bc_stats['uses'] >= 2:  # Show breadcrumbs used multiple times
            print(f"  {bc}:")
            print(f"    Uses: {bc_stats['uses']}")
            print(f"    Success Rate: {bc_stats['success_rate']:.1%}")
    print()
    
    print("="*70)
    print("View the dashboard at http://localhost:5000 to see this data!")
    print("="*70)

if __name__ == '__main__':
    try:
        demo_thought_process_logging()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
