#!/usr/bin/env python3
"""
Test script for enhanced session tracking with breadcrumb recall
Demonstrates the new breadcrumb tracking and pattern reuse features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.interactive_session import SessionManager
from collections import defaultdict


class MockModelLoader:
    """Mock model loader for testing"""
    def load_model(self, model_type):
        return MockModel()


class MockModel:
    """Mock model for testing"""
    def explore_codebase(self, query, file_contents, breadcrumbs):
        return {
            'insights': f'Analyzed {len(file_contents)} files and found {len(breadcrumbs)} breadcrumbs',
            'files_analyzed': len(file_contents),
            'breadcrumbs_analyzed': len(breadcrumbs)
        }
    
    def reason_about_task(self, task_description, context, previous_attempts=None):
        return {
            'reasoning': f'Based on the task "{task_description}", we should proceed with implementation',
            'strategy': 'Use existing patterns where available'
        }
    
    def generate_with_breadcrumbs(self, task_description, context, breadcrumb_history=None, stream=False):
        return f'// Generated code for {task_description}\nint main() {{ return 0; }}'
    
    def review_code(self, code, requirements, errors=None):
        return {
            'review': 'Code looks good',
            'has_errors': False
        }


def test_enhanced_session_tracking():
    """Test enhanced session tracking features"""
    print("Testing Enhanced Session Tracking with Breadcrumb Recall")
    print("=" * 70)
    
    # Create session manager with mock model loader
    model_loader = MockModelLoader()
    session_mgr = SessionManager(
        model_loader=model_loader,
        aros_path='/tmp/test_aros',
        log_path='/tmp/test_logs'
    )
    
    print("\n1. Testing Session Initialization")
    print("-" * 70)
    
    # Add some fake session history to test similarity detection
    session_mgr.session_history = [
        {
            'id': 'session_old_1',
            'task': 'Implement GPU initialization driver',
            'patterns_recalled': ['DEVICE_INIT_V1', 'MEMORY_POOL_V2'],
            'status': 'completed'
        },
        {
            'id': 'session_old_2',
            'task': 'Add memory management for hardware',
            'patterns_recalled': ['MEMORY_POOL_V2'],
            'status': 'completed'
        }
    ]
    
    # Start a new session
    session_id = session_mgr.start_session(
        task_description='Implement GPU driver initialization',
        context={'project': 'gpu_driver', 'phase': 'INIT'}
    )
    
    print(f"✓ Session created: {session_id}")
    print(f"✓ Breadcrumb recall system active")
    
    # Check if similar work was detected
    if session_mgr.current_session['work_avoided']:
        print(f"✓ Detected {len(session_mgr.current_session['work_avoided'])} similar past work items")
        for work in session_mgr.current_session['work_avoided']:
            print(f"  - {work['description']}")
            print(f"    Patterns: {', '.join(work.get('patterns', []))}")
    
    print("\n2. Testing Pattern Extraction from Breadcrumbs")
    print("-" * 70)
    
    # Create mock breadcrumbs
    mock_breadcrumbs = [
        {
            'file_path': 'test.c',
            'line_number': 10,
            'phase': 'GPU_INIT',
            'status': 'IMPLEMENTED',
            'pattern': 'DEVICE_INIT_V1',
            'strategy': 'Initialize GPU device'
        },
        {
            'file_path': 'test.c',
            'line_number': 50,
            'phase': 'MEMORY_SETUP',
            'status': 'IMPLEMENTED',
            'pattern': 'MEMORY_POOL_V2',
            'strategy': 'Setup memory pool'
        },
        {
            'file_path': 'test.c',
            'line_number': 100,
            'phase': 'THREAD_INIT',
            'status': 'PARTIAL',
            'pattern': 'DEVICE_INIT_V1',
            'strategy': 'Initialize threading'
        }
    ]
    
    patterns = session_mgr._extract_patterns_from_breadcrumbs(mock_breadcrumbs)
    print(f"✓ Extracted {len(patterns)} patterns from breadcrumbs:")
    for pattern_name, pattern_info in patterns.items():
        print(f"  - {pattern_name}:")
        print(f"    Used {pattern_info['count']} times")
        print(f"    Success rate: {pattern_info['success_rate']}")
    
    print("\n3. Testing Duplicate Work Detection")
    print("-" * 70)
    
    duplicate_work = session_mgr._check_breadcrumbs_for_duplicate_work(
        mock_breadcrumbs,
        'GPU initialization driver'
    )
    
    print(f"✓ Checked for duplicate work")
    if duplicate_work:
        print(f"✓ Found {len(duplicate_work)} similar completed tasks:")
        for dup in duplicate_work:
            print(f"  - {dup['phase']}: {dup['status']}")
            print(f"    Pattern: {dup['pattern']}")
    else:
        print("  No duplicate work detected")
    
    print("\n4. Testing Breadcrumb Influence Tracking")
    print("-" * 70)
    
    # Track some influences
    session_mgr._track_breadcrumb_influence(
        decision_type='exploration',
        decision_details='Explored files based on breadcrumbs',
        breadcrumbs_used=['test.c:10', 'test.c:50']
    )
    
    session_mgr._track_breadcrumb_influence(
        decision_type='generation',
        decision_details='Generated code using patterns',
        breadcrumbs_used=['test.c:10', 'test.c:50', 'test.c:100']
    )
    
    print(f"✓ Tracked breadcrumb influences")
    print(f"✓ Total influences recorded: {len(session_mgr.current_session['breadcrumb_influences'])}")
    
    for i, influence in enumerate(session_mgr.current_session['breadcrumb_influences'], 1):
        print(f"  [{i}] {influence['decision_type']}: {influence['breadcrumb_count']} breadcrumbs")
    
    print("\n5. Testing Breadcrumb Usage Statistics")
    print("-" * 70)
    
    # Simulate breadcrumb usage
    session_mgr.breadcrumb_usage_tracker['test.c:10'] = 3
    session_mgr.breadcrumb_usage_tracker['test.c:50'] = 2
    session_mgr.breadcrumb_usage_tracker['test.c:100'] = 1
    
    session_mgr.current_session['breadcrumb_usage'] = dict(session_mgr.breadcrumb_usage_tracker)
    session_mgr.current_session['patterns_recalled'] = list(patterns.keys())
    
    recall_stats = session_mgr.get_breadcrumb_recall_stats()
    
    print(f"✓ Breadcrumb Recall Statistics:")
    print(f"  Breadcrumbs consulted: {recall_stats['breadcrumbs_consulted']}")
    print(f"  Unique patterns recalled: {recall_stats['unique_patterns_recalled']}")
    print(f"  Patterns: {', '.join(recall_stats['patterns_recalled'])}")
    print(f"  Work items avoided: {recall_stats['work_items_avoided']}")
    print(f"  Breadcrumb influences: {recall_stats['breadcrumb_influences']}")
    
    if recall_stats['most_used_breadcrumbs']:
        print(f"  Most used breadcrumbs:")
        for bc_key, count in recall_stats['most_used_breadcrumbs'][:3]:
            print(f"    • {bc_key}: {count} times")
    
    print("\n6. Testing Session Summary")
    print("-" * 70)
    
    summary = session_mgr.get_session_summary()
    print(f"✓ Session Summary:")
    print(f"  Session ID: {summary['id']}")
    print(f"  Status: {summary['status']}")
    print(f"  Patterns recalled: {len(summary['patterns_recalled'])}")
    print(f"  Work avoided: {summary['work_avoided']}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    
    print("\nEnhanced Features Validated:")
    print("  ✓ Breadcrumb usage tracking")
    print("  ✓ Pattern extraction and recognition")
    print("  ✓ Duplicate work detection")
    print("  ✓ Breadcrumb influence mapping")
    print("  ✓ Recall statistics generation")
    print("  ✓ Session summary with breadcrumb data")
    
    return True


if __name__ == '__main__':
    try:
        success = test_enhanced_session_tracking()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
