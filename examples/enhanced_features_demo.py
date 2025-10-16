#!/usr/bin/env python3
"""
Example: Using Enhanced Copilot Iteration Features

Demonstrates the new checkpoint/resume, adaptive retries, and pattern learning features.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.copilot_iteration import CopilotStyleIteration
from src.interactive_session import SessionManager
from src.local_models import LocalModelLoader


def example_checkpoint_resume():
    """Example: Using checkpoint and resume"""
    print("\n" + "="*60)
    print("Example 1: Checkpoint and Resume")
    print("="*60 + "\n")
    
    loader = LocalModelLoader()
    session = SessionManager(
        model_loader=loader,
        aros_path='aros-src',
        log_path='logs/examples'
    )
    
    # Start a session
    session.start_session(
        task_description="Implement shader compilation",
        context={'phase': 'SHADER_COMPILATION', 'project': 'radeonsi'}
    )
    print("✓ Session started")
    
    # Simulate some work
    session.iteration_context['work_done'] = ['step1', 'step2', 'step3']
    print("✓ Simulated work completed")
    
    # Save checkpoint
    checkpoint_path = session.save_checkpoint("shader_v1")
    print(f"✓ Checkpoint saved: {checkpoint_path}")
    
    # End session
    session.end_session(status='in_progress', summary='Checkpoint before break')
    
    # Later, resume from checkpoint
    print("\n--- Resuming from checkpoint ---\n")
    
    session2 = SessionManager(
        model_loader=loader,
        aros_path='aros-src',
        log_path='logs/examples'
    )
    
    if session2.load_checkpoint(checkpoint_path):
        print("✓ Checkpoint loaded successfully")
        print(f"✓ Restored work: {session2.iteration_context['work_done']}")
        print(f"✓ Task: {session2.current_session['task']}")
        
        # Continue working
        session2.iteration_context['work_done'].append('step4')
        print("✓ Continued work from checkpoint")
        
        session2.end_session(status='completed')
    
    # List all checkpoints
    checkpoints = session2.list_checkpoints()
    print(f"\n✓ Total checkpoints available: {len(checkpoints)}")
    for cp in checkpoints:
        print(f"  - {cp['name']}: {cp['task']}")


def example_adaptive_retries():
    """Example: Adaptive retry logic"""
    print("\n" + "="*60)
    print("Example 2: Adaptive Retry Logic")
    print("="*60 + "\n")
    
    iteration = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/examples',
        max_iterations=1,
        max_retries=3,
        adaptive_retries=True
    )
    
    # Test different error types
    test_cases = [
        ("Simple syntax errors", ["syntax error", "missing semicolon"]),
        ("Medium complexity errors", ["undefined reference", "type mismatch"]),
        ("Complex runtime errors", ["segmentation fault", "assertion failed", "deadlock"])
    ]
    
    for name, errors in test_cases:
        retries = iteration._calculate_adaptive_retries(errors)
        print(f"{name}:")
        print(f"  Errors: {errors}")
        print(f"  Adaptive retries: {retries}")
        print()


def example_pattern_learning():
    """Example: Pattern learning and history"""
    print("\n" + "="*60)
    print("Example 3: Pattern Learning")
    print("="*60 + "\n")
    
    iteration = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/examples',
        max_iterations=5,
        max_retries=3
    )
    
    # Simulate some iterations with results
    simulated_results = [
        {
            'iteration': 1,
            'success': True,
            'retry_count': 1,
            'total_time': 45.2,
            'timings': {'exploration': 8.5, 'generation': 12.8},
            'compilation': {'errors': []},
            'generation': {'context': {'phase': 'SHADER_COMPILATION'}}
        },
        {
            'iteration': 2,
            'success': False,
            'retry_count': 3,
            'total_time': 68.5,
            'timings': {'exploration': 10.2, 'generation': 15.3},
            'compilation': {'errors': ['type error']},
            'generation': {'context': {'phase': 'SHADER_COMPILATION'}}
        },
        {
            'iteration': 3,
            'success': True,
            'retry_count': 2,
            'total_time': 52.1,
            'timings': {'exploration': 9.1, 'generation': 14.2},
            'compilation': {'errors': []},
            'generation': {'context': {'phase': 'MEMORY_MANAGER'}}
        }
    ]
    
    print("Simulating iterations and learning patterns...\n")
    
    for result in simulated_results:
        iteration.current_iteration = result['iteration']
        iteration._track_iteration_history(result)
        iteration._learn_pattern(result)
        
        status = "✓" if result['success'] else "✗"
        print(f"Iteration {result['iteration']}: {status} "
              f"({result['retry_count']} retries, {result['total_time']:.1f}s)")
    
    # Display learned patterns
    print("\n--- Learned Patterns ---\n")
    patterns = iteration.get_learned_patterns()
    
    print(f"Total iterations: {patterns['total_iterations']}")
    print(f"Overall success rate: {patterns['overall_success_rate']*100:.1f}%\n")
    
    for phase, data in patterns['patterns'].items():
        success_rate = data['successes'] / data['total_attempts'] * 100
        print(f"{phase}:")
        print(f"  Success rate: {data['successes']}/{data['total_attempts']} ({success_rate:.1f}%)")
        print(f"  Avg retries: {data['avg_retries']:.1f}")
        print(f"  Avg time: {data['avg_time']:.1f}s")
        print()


def example_state_persistence():
    """Example: State persistence and recovery"""
    print("\n" + "="*60)
    print("Example 4: State Persistence & Recovery")
    print("="*60 + "\n")
    
    # Create iteration with some state
    iteration1 = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/examples',
        max_iterations=20
    )
    
    # Simulate progress
    iteration1.current_iteration = 8
    iteration1.successful_iterations = 6
    iteration1.learned_patterns = {
        'SHADER_COMPILATION': {
            'successes': 4,
            'total_attempts': 5,
            'avg_retries': 1.2,
            'avg_time': 45.5
        },
        'MEMORY_MANAGER': {
            'successes': 2,
            'total_attempts': 3,
            'avg_retries': 2.0,
            'avg_time': 52.3
        }
    }
    
    print(f"Current state:")
    print(f"  Iteration: {iteration1.current_iteration}")
    print(f"  Successful: {iteration1.successful_iterations}")
    print(f"  Learned patterns: {len(iteration1.learned_patterns)}")
    
    # Save state
    state_file = iteration1.save_iteration_state()
    print(f"\n✓ State saved to: {state_file}")
    
    # Simulate recovery
    print("\n--- Simulating recovery after interruption ---\n")
    
    iteration2 = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/examples',
        max_iterations=20
    )
    
    if iteration2.load_iteration_state():
        print("✓ State loaded successfully")
        print(f"\nRecovered state:")
        print(f"  Iteration: {iteration2.current_iteration}")
        print(f"  Successful: {iteration2.successful_iterations}")
        print(f"  Learned patterns: {len(iteration2.learned_patterns)}")
        
        print("\n✓ Ready to continue from iteration", iteration2.current_iteration + 1)
        
        # Show pattern details
        patterns = iteration2.get_learned_patterns()
        print(f"\nPattern details:")
        for phase, data in patterns['patterns'].items():
            print(f"  {phase}: {data['successes']}/{data['total_attempts']} success")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  Enhanced Copilot Iteration Examples")
    print("="*70)
    
    try:
        example_checkpoint_resume()
        example_adaptive_retries()
        example_pattern_learning()
        example_state_persistence()
        
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
