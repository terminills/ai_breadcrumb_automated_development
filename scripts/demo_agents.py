#!/usr/bin/env python3
"""
Demo script to simulate AI agent activity
Creates iteration state and reasoning data for UI visualization
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
import random

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_demo_iteration_state(logs_path: Path, iteration: int = 1, total: int = 10):
    """Create a demo iteration state file"""
    state_file = logs_path / 'iteration_state.json'
    
    phases = ['exploration', 'reasoning', 'generation', 'review', 'compilation', 'learning']
    current_phase_idx = iteration % len(phases)
    current_phase = phases[current_phase_idx]
    
    phase_progress = {}
    for i, phase in enumerate(phases):
        if i < current_phase_idx:
            phase_progress[phase] = 'completed'
        elif i == current_phase_idx:
            phase_progress[phase] = 'running'
        else:
            phase_progress[phase] = 'pending'
    
    state = {
        'current_iteration': iteration,
        'total_iterations': total,
        'current_phase': current_phase,
        'phase_progress': phase_progress,
        'session_id': f'demo_session_{int(time.time())}',
        'task_description': f'Implementing {random.choice(["graphics pipeline", "memory manager", "shader compiler", "texture system", "audio driver"])}',
        'retry_count': random.randint(0, 2),
        'last_update': datetime.now().isoformat(),
        'exploration': {
            'files_analyzed': random.randint(5, 20),
            'breadcrumbs_analyzed': random.randint(3, 15),
            'insights': 'Found relevant patterns in RadeonSI driver and Mesa implementation...'
        },
        'reasoning': {
            'approach': 'Using pattern-based implementation with breadcrumb guidance',
            'confidence': random.uniform(0.7, 0.95)
        },
        'generation': {
            'code_lines': random.randint(50, 200),
            'breadcrumbs_added': random.randint(3, 8)
        }
    }
    
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"✓ Created iteration state: iteration {iteration}/{total}, phase: {current_phase}")

def create_demo_reasoning(logs_path: Path):
    """Create demo reasoning tracker data"""
    reasoning_dir = logs_path / 'reasoning'
    reasoning_dir.mkdir(parents=True, exist_ok=True)
    
    # Create current reasoning
    current_file = reasoning_dir / 'current_reasoning.json'
    
    tasks = [
        'Implementing shader compilation pipeline',
        'Adding memory management system',
        'Creating graphics context manager',
        'Building texture upload system',
        'Developing audio buffer handling'
    ]
    
    reasoning = {
        'task_id': f'task_{int(time.time())}',
        'phase': random.choice(['analyzing', 'planning', 'implementing', 'testing']),
        'decision_type': random.choice(['feature_implementation', 'bug_fix', 'refactoring']),
        'approach_chosen': random.choice([
            'Pattern-based implementation with breadcrumb guidance',
            'Direct port from Linux driver with AROS adaptations',
            'Incremental implementation with testing at each step',
            'Refactor existing code with improved patterns'
        ]),
        'confidence': random.uniform(0.6, 0.95),
        'breadcrumbs_consulted': [
            'GRAPHICS_PIPELINE',
            'SHADER_COMPILATION',
            'MEMORY_MANAGEMENT',
            random.choice(['TEXTURE_SYSTEM', 'AUDIO_DRIVER', 'NETWORK_STACK'])
        ],
        'reasoning_steps': [
            'Analyzed existing breadcrumbs for similar implementations',
            'Identified pattern from successful previous iterations',
            'Reviewed Linux reference implementation',
            'Planned AROS-specific adaptations',
            'Estimated complexity and potential issues'
        ],
        'patterns_identified': [
            'MEMORY_ALLOCATION_V2',
            'ERROR_HANDLING_PATTERN',
            random.choice(['DEVICE_INIT_V3', 'CONTEXT_MANAGEMENT_V1', 'BUFFER_HANDLING_V2'])
        ],
        'started_at': datetime.now().isoformat()
    }
    
    with open(current_file, 'w') as f:
        json.dump(reasoning, f, indent=2)
    
    print(f"✓ Created reasoning data: {reasoning['task_id']}, phase: {reasoning['phase']}")

def create_demo_session(logs_path: Path):
    """Create demo session data"""
    sessions_dir = logs_path / 'sessions'
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    session_file = sessions_dir / f'session_{int(time.time())}.json'
    
    session = {
        'id': f'session_{int(time.time())}',
        'task': random.choice([
            'Implement graphics driver initialization',
            'Add memory allocation system',
            'Create shader compilation pipeline',
            'Build texture management system'
        ]),
        'context': {
            'phase': 'DEVELOPMENT',
            'status': 'IMPLEMENTING',
            'project': random.choice(['radeonsi', 'graphics', 'kernel', 'drivers'])
        },
        'started_at': datetime.now().isoformat(),
        'status': 'active',
        'turns': [
            {'type': 'user', 'content': 'Please implement the graphics initialization'},
            {'type': 'assistant', 'content': 'Analyzing breadcrumbs and existing code...'}
        ],
        'exploration_results': ['Found 12 relevant files', 'Identified 8 breadcrumbs'],
        'generated_code': ['init_graphics.c', 'shader_compiler.c']
    }
    
    with open(session_file, 'w') as f:
        json.dump(session, f, indent=2)
    
    print(f"✓ Created session: {session['id']}, task: {session['task']}")

def run_demo_cycle(logs_path: Path, iterations: int = 10, delay: float = 2.0):
    """Run a demo cycle simulating agent activity"""
    print("\n" + "="*60)
    print("AI Agent Demo - Simulating Agent Activity")
    print("="*60 + "\n")
    
    for i in range(1, iterations + 1):
        print(f"\n--- Iteration {i}/{iterations} ---")
        
        # Update iteration state
        create_demo_iteration_state(logs_path, iteration=i, total=iterations)
        
        # Update reasoning (every iteration)
        create_demo_reasoning(logs_path)
        
        # Create/update session (every 3 iterations)
        if i % 3 == 0:
            create_demo_session(logs_path)
        
        print(f"Waiting {delay} seconds...\n")
        time.sleep(delay)
    
    print("\n" + "="*60)
    print("Demo cycle complete!")
    print("="*60 + "\n")
    print("The UI should now show active agents. Check http://localhost:5000")
    print("\nTo clean up demo data, delete the logs/ directory")

def main():
    # Get logs path from config
    config_path = Path(__file__).parent.parent / 'config' / 'config.json'
    
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        logs_path = Path(__file__).parent.parent / config['logs_path']
    else:
        logs_path = Path(__file__).parent.parent / 'logs'
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Demo AI agent activity for UI visualization')
    parser.add_argument('-i', '--iterations', type=int, default=10, help='Number of iterations to simulate')
    parser.add_argument('-d', '--delay', type=float, default=2.0, help='Delay between iterations in seconds')
    parser.add_argument('--once', action='store_true', help='Create demo data once and exit')
    
    args = parser.parse_args()
    
    if args.once:
        print("Creating single demo data snapshot...")
        create_demo_iteration_state(logs_path, iteration=5, total=10)
        create_demo_reasoning(logs_path)
        create_demo_session(logs_path)
        print("\n✓ Demo data created. Check the UI at http://localhost:5000")
    else:
        run_demo_cycle(logs_path, iterations=args.iterations, delay=args.delay)

if __name__ == '__main__':
    main()
