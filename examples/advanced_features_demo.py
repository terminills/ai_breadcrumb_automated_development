#!/usr/bin/env python3
"""
Example: Advanced Copilot Iteration Features

Demonstrates the newly added features:
1. Pattern recommendations
2. Checkpoint diff
3. Pattern export/import
4. Enhanced analytics
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.copilot_iteration import CopilotStyleIteration
from src.interactive_session import SessionManager
from src.local_models import LocalModelLoader


def example_pattern_recommendations():
    """Example: Using pattern recommendations"""
    print("\n" + "="*70)
    print("Example 1: Pattern Recommendations")
    print("="*70 + "\n")
    
    iteration = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/examples',
        max_iterations=10
    )
    
    # Simulate some learned patterns
    iteration.learned_patterns = {
        'SHADER_COMPILATION': {
            'successes': 8,
            'total_attempts': 10,
            'avg_retries': 1.5,
            'avg_time': 45.0,
            'common_approaches': []
        },
        'MEMORY_MANAGER': {
            'successes': 3,
            'total_attempts': 6,
            'avg_retries': 2.8,
            'avg_time': 72.0,
            'common_approaches': []
        }
    }
    
    iteration.iteration_history = [
        {'iteration': 1, 'phase': 'SHADER_COMPILATION', 'success': True, 'retry_count': 1, 'total_time': 42.0},
        {'iteration': 2, 'phase': 'SHADER_COMPILATION', 'success': True, 'retry_count': 2, 'total_time': 48.0},
        {'iteration': 3, 'phase': 'MEMORY_MANAGER', 'success': False, 'retry_count': 3, 'total_time': 78.0},
    ]
    
    # Get recommendations for different phases and complexities
    print("Getting recommendations for different scenarios:\n")
    
    scenarios = [
        ('SHADER_COMPILATION', 'LOW'),
        ('SHADER_COMPILATION', 'HIGH'),
        ('MEMORY_MANAGER', 'MEDIUM'),
        ('NEW_FEATURE', 'MEDIUM'),  # Unknown phase
    ]
    
    for phase, complexity in scenarios:
        rec = iteration.get_pattern_recommendation(phase, complexity)
        
        print(f"Phase: {phase} (Complexity: {complexity})")
        print(f"  Success Probability: {rec['success_probability']*100:.0f}%")
        print(f"  Suggested Retries: {rec['suggested_retries']}")
        print(f"  Estimated Time: {rec['estimated_time']:.0f}s")
        print(f"  Similar Tasks: {len(rec['similar_tasks'])}")
        
        if rec['best_practices']:
            print(f"  Best Practices:")
            for practice in rec['best_practices']:
                print(f"    • {practice}")
        print()


def example_checkpoint_diff():
    """Example: Comparing checkpoints"""
    print("\n" + "="*70)
    print("Example 2: Checkpoint Diff")
    print("="*70 + "\n")
    
    loader = LocalModelLoader()
    session = SessionManager(
        model_loader=loader,
        aros_path='aros-src',
        log_path='logs/examples'
    )
    
    # Create first checkpoint
    print("Creating checkpoint 1...")
    session.start_session(
        task_description="Implement shader pipeline",
        context={'phase': 'SHADER_COMPILATION', 'version': '1.0'}
    )
    session.iteration_context['steps_completed'] = ['init', 'parse']
    session.iteration_context['code_lines'] = 150
    cp1 = session.save_checkpoint("shader_v1")
    print(f"✓ Saved: {Path(cp1).name}")
    session.end_session()
    
    # Make some progress and create second checkpoint
    print("\nMaking progress and creating checkpoint 2...")
    session.start_session(
        task_description="Implement shader pipeline",
        context={'phase': 'SHADER_COMPILATION', 'version': '1.1'}
    )
    session.iteration_context['steps_completed'] = ['init', 'parse', 'compile', 'optimize']
    session.iteration_context['code_lines'] = 287
    session.iteration_context['tests_added'] = 12
    cp2 = session.save_checkpoint("shader_v2")
    print(f"✓ Saved: {Path(cp2).name}")
    session.end_session()
    
    # Compare checkpoints
    print("\nComparing checkpoints...")
    diff = session.compare_checkpoints(cp1, cp2)
    
    print("\n--- Checkpoint Comparison ---\n")
    for line in diff['summary']:
        print(f"  {line}")
    
    if diff['iteration_context_diff']:
        print("\n  Detailed Context Changes:")
        for key, change in diff['iteration_context_diff'].items():
            print(f"    {key}:")
            print(f"      Before: {change['old']}")
            print(f"      After:  {change['new']}")


def example_pattern_export_import():
    """Example: Sharing patterns between projects"""
    print("\n" + "="*70)
    print("Example 3: Pattern Export/Import")
    print("="*70 + "\n")
    
    # Project 1: Export patterns
    print("Project 1: Creating and exporting patterns...")
    
    project1 = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/examples/project1',
        max_iterations=10
    )
    
    # Simulate learned patterns
    project1.learned_patterns = {
        'SHADER_COMPILATION': {
            'successes': 15,
            'total_attempts': 18,
            'avg_retries': 1.3,
            'avg_time': 42.0,
            'common_approaches': ['LLVM_BACKEND', 'SPIR_V']
        },
        'TEXTURE_UPLOAD': {
            'successes': 12,
            'total_attempts': 14,
            'avg_retries': 1.5,
            'avg_time': 38.0,
            'common_approaches': ['DMA_TRANSFER']
        },
        'MEMORY_MANAGER': {
            'successes': 8,
            'total_attempts': 12,
            'avg_retries': 2.1,
            'avg_time': 55.0,
            'common_approaches': ['BUDDY_ALLOCATOR']
        }
    }
    
    project1.iteration_history = [
        {'iteration': i, 'success': True, 'retry_count': 1, 'total_time': 40.0}
        for i in range(1, 16)
    ]
    
    export_path = project1.export_learned_patterns('logs/examples/shared_patterns.json')
    print(f"✓ Exported {len(project1.learned_patterns)} patterns")
    print(f"  File: {Path(export_path).name}")
    print(f"  Phases: {', '.join(project1.learned_patterns.keys())}")
    
    # Project 2: Import and merge patterns
    print("\nProject 2: Importing patterns...")
    
    project2 = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='nouveau',
        log_path='logs/examples/project2',
        max_iterations=10
    )
    
    # Project 2 has some of its own patterns
    project2.learned_patterns = {
        'SHADER_COMPILATION': {
            'successes': 5,
            'total_attempts': 8,
            'avg_retries': 2.0,
            'avg_time': 50.0,
            'common_approaches': ['TGSI']
        },
        'RENDER_PIPELINE': {
            'successes': 7,
            'total_attempts': 9,
            'avg_retries': 1.8,
            'avg_time': 45.0,
            'common_approaches': ['DEFERRED']
        }
    }
    
    print(f"  Before import: {len(project2.learned_patterns)} patterns")
    print(f"  Phases: {', '.join(project2.learned_patterns.keys())}")
    
    # Import with merge
    success = project2.import_learned_patterns(export_path, merge=True)
    
    if success:
        print(f"\n✓ Import successful (merge mode)")
        print(f"  After import: {len(project2.learned_patterns)} patterns")
        print(f"  Phases: {', '.join(project2.learned_patterns.keys())}")
        
        # Show merged SHADER_COMPILATION pattern
        merged = project2.learned_patterns['SHADER_COMPILATION']
        print(f"\n  Merged 'SHADER_COMPILATION' pattern:")
        print(f"    Total attempts: {merged['total_attempts']}")
        print(f"    Success rate: {merged['successes']/merged['total_attempts']*100:.0f}%")
        print(f"    Avg retries: {merged['avg_retries']:.1f}")
        print(f"    Avg time: {merged['avg_time']:.1f}s")
        print(f"    Approaches: {', '.join(merged['common_approaches'])}")


def example_enhanced_analytics():
    """Example: Enhanced analytics and reporting"""
    print("\n" + "="*70)
    print("Example 4: Enhanced Analytics")
    print("="*70 + "\n")
    
    iteration = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/examples',
        max_iterations=20
    )
    
    # Simulate a realistic iteration history
    iteration.iteration_history = [
        {
            'iteration': 1,
            'phase': 'SHADER_COMPILATION',
            'success': True,
            'retry_count': 1,
            'total_time': 45.0,
            'timings': {'exploration': 8.0, 'reasoning': 5.0, 'generation': 12.0, 'compilation': 15.0, 'review': 5.0}
        },
        {
            'iteration': 2,
            'phase': 'SHADER_COMPILATION',
            'success': False,
            'retry_count': 3,
            'total_time': 72.0,
            'timings': {'exploration': 10.0, 'reasoning': 6.0, 'generation': 15.0, 'compilation': 28.0, 'review': 13.0},
            'compilation': {'errors': ['undefined reference to llvm_init']}
        },
        {
            'iteration': 3,
            'phase': 'SHADER_COMPILATION',
            'success': True,
            'retry_count': 2,
            'total_time': 58.0,
            'timings': {'exploration': 9.0, 'reasoning': 5.5, 'generation': 13.0, 'compilation': 22.0, 'review': 8.5}
        },
        {
            'iteration': 4,
            'phase': 'MEMORY_MANAGER',
            'success': True,
            'retry_count': 1,
            'total_time': 52.0,
            'timings': {'exploration': 7.0, 'reasoning': 4.0, 'generation': 14.0, 'compilation': 20.0, 'review': 7.0}
        },
        {
            'iteration': 5,
            'phase': 'MEMORY_MANAGER',
            'success': False,
            'retry_count': 4,
            'total_time': 88.0,
            'timings': {'exploration': 8.0, 'reasoning': 7.0, 'generation': 18.0, 'compilation': 38.0, 'review': 17.0},
            'compilation': {'errors': ['segmentation fault in malloc_wrapper']}
        },
        {
            'iteration': 6,
            'phase': 'TEXTURE_UPLOAD',
            'success': True,
            'retry_count': 1,
            'total_time': 41.0,
            'timings': {'exploration': 6.0, 'reasoning': 4.0, 'generation': 11.0, 'compilation': 15.0, 'review': 5.0}
        },
    ]
    
    iteration.learned_patterns = {
        'SHADER_COMPILATION': {
            'successes': 2,
            'total_attempts': 3,
            'avg_retries': 2.0,
            'avg_time': 58.3,
            'common_approaches': []
        },
        'MEMORY_MANAGER': {
            'successes': 1,
            'total_attempts': 2,
            'avg_retries': 2.5,
            'avg_time': 70.0,
            'common_approaches': []
        },
        'TEXTURE_UPLOAD': {
            'successes': 1,
            'total_attempts': 1,
            'avg_retries': 1.0,
            'avg_time': 41.0,
            'common_approaches': []
        }
    }
    
    # Get analytics
    analytics = iteration.get_analytics()
    
    # Performance summary
    print("Performance Summary:")
    print("-" * 70)
    summary = analytics.get_performance_summary()
    print(f"  Total Iterations: {summary['total_iterations']}")
    print(f"  Success Rate: {summary['success_rate']*100:.1f}%")
    print(f"  Average Time: {summary['average_time']:.1f}s")
    print(f"  Average Retries: {summary['average_retries']:.1f}")
    print(f"  Total Time: {summary['total_time']:.0f}s ({summary['total_time']/60:.1f}m)")
    
    print("\n  Time Breakdown by Phase:")
    for phase, timings in summary.get('phase_timings', {}).items():
        print(f"    {phase}: avg={timings['average']:.1f}s, min={timings['min']:.1f}s, max={timings['max']:.1f}s")
    
    # Phase analysis
    print("\nPhase Analysis:")
    print("-" * 70)
    for phase in ['SHADER_COMPILATION', 'MEMORY_MANAGER', 'TEXTURE_UPLOAD']:
        analysis = analytics.get_phase_analysis(phase)
        print(f"  {phase}:")
        print(f"    Success Rate: {analysis['success_rate']*100:.1f}%")
        print(f"    Trend: {analysis['trend']}")
        print(f"    Avg Retries: {analysis['avg_retries']:.1f}")
        print(f"    Avg Time: {analysis['avg_time']:.1f}s")
    
    # Error analysis
    print("\nError Analysis:")
    print("-" * 70)
    error_analysis = analytics.get_error_analysis()
    print(f"  Total Failures: {error_analysis['total_failures']}")
    
    if error_analysis.get('most_common_errors'):
        print("  Most Common Errors:")
        for error in error_analysis['most_common_errors']:
            print(f"    - {error['type']}: {error['count']} times")
    
    # Recommendations
    print("\nRecommendations:")
    print("-" * 70)
    recommendations = analytics.get_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Generate full report
    print("\nGenerating Full Report...")
    report_path = 'logs/examples/analytics_report.txt'
    report = iteration.generate_analytics_report(report_path)
    print(f"✓ Full report saved to: {report_path}")
    print(f"  Report size: {len(report)} characters")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  Advanced Copilot Iteration Features - Examples")
    print("="*70)
    
    try:
        example_pattern_recommendations()
        example_checkpoint_diff()
        example_pattern_export_import()
        example_enhanced_analytics()
        
        print("\n" + "="*70)
        print("  All examples completed successfully!")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
