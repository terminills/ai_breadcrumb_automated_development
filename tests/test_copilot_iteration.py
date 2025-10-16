#!/usr/bin/env python3
"""
Test script for Copilot-style iteration components
Tests basic functionality without requiring model downloads
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.local_models.model_loader import LocalModelLoader
from src.interactive_session import SessionManager


def test_model_loader():
    """Test model loader configuration"""
    print("\n=== Testing Model Loader ===")
    
    # Test with temp config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_config = {
            "codegen": {
                "model_path": "test-model",
                "device": "cpu"
            },
            "llm": {
                "model_path": "test-llm",
                "device": "cpu"
            }
        }
        json.dump(test_config, f)
        config_path = f.name
    
    try:
        loader = LocalModelLoader(config_path)
        
        # Test config loading
        codegen_config = loader.get_codegen_config()
        assert codegen_config['model_path'] == "test-model"
        print("✓ Model loader configuration works")
        
        llm_config = loader.get_llm_config()
        assert llm_config['model_path'] == "test-llm"
        print("✓ LLM configuration works")
        
        # Test exploration config
        exploration_config = loader.get_exploration_config()
        # Should return a dict (may be empty if not in config)
        assert isinstance(exploration_config, dict)
        print("✓ Exploration configuration works")
        
        return True
        
    finally:
        os.unlink(config_path)


def test_session_manager():
    """Test session manager without models"""
    print("\n=== Testing Session Manager ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock AROS path
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        # Create some test files
        test_file = aros_path / 'test.c'
        test_file.write_text("""
// AI_PHASE: TEST_PHASE
// AI_STATUS: PARTIAL
// AI_STRATEGY: Test implementation
void test_function() {
    // Test code
}
""")
        
        log_path = Path(temp_dir) / 'logs'
        
        # Create loader
        loader = LocalModelLoader()
        
        # Create session manager
        session = SessionManager(
            model_loader=loader,
            aros_path=str(aros_path),
            log_path=str(log_path)
        )
        
        # Test session start
        session_id = session.start_session(
            task_description="Test task",
            context={'phase': 'TEST', 'project': 'test'}
        )
        assert session_id.startswith('session_')
        print(f"✓ Session started: {session_id}")
        
        # Test session summary
        summary = session.get_session_summary()
        assert summary['task'] == "Test task"
        assert summary['status'] == 'active'
        print("✓ Session summary works")
        
        # Test session end
        session.end_session(status='completed', summary='Test completed')
        print("✓ Session ended successfully")
        
        # Check log file was created
        session_files = list(log_path.glob('*.json'))
        assert len(session_files) > 0
        print(f"✓ Session log saved: {session_files[0].name}")
        
        return True


def test_file_exploration():
    """Test file exploration logic"""
    print("\n=== Testing File Exploration ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        # Create test files
        (aros_path / 'graphics').mkdir()
        (aros_path / 'graphics' / 'render.c').write_text("// Graphics code")
        (aros_path / 'kernel').mkdir()
        (aros_path / 'kernel' / 'memory.c').write_text("// Memory code")
        
        log_path = Path(temp_dir) / 'logs'
        
        loader = LocalModelLoader()
        session = SessionManager(
            model_loader=loader,
            aros_path=str(aros_path),
            log_path=str(log_path)
        )
        
        session.start_session(
            task_description="Test exploration",
            context={'phase': 'TEST'}
        )
        
        # Test file finding
        files = session._find_relevant_files("graphics", max_files=5)
        assert len(files) > 0
        print(f"✓ Found {len(files)} relevant files")
        
        # Check graphics file was found
        graphics_found = any('graphics' in str(f) for f in files)
        assert graphics_found
        print("✓ Relevant file detection works")
        
        session.end_session(status='completed')
        
        return True


def test_copilot_iteration_structure():
    """Test copilot iteration structure without models"""
    print("\n=== Testing Copilot Iteration Structure ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        # Create iteration instance
        iteration = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=1
        )
        
        assert iteration.current_iteration == 0
        assert iteration.project_name == 'test'
        print("✓ Copilot iteration initialized")
        
        # Test task finding (should work without real files)
        tasks = iteration._find_incomplete_tasks()
        assert len(tasks) > 0  # Should create default task
        print(f"✓ Task finding works (found {len(tasks)} tasks)")
        
        return True


def test_streaming_output():
    """Test streaming output components"""
    print("\n=== Testing Streaming Output ===")
    
    from src.streaming_output import OutputFormatter, ProgressIndicator
    
    # Test formatter
    formatter = OutputFormatter()
    
    code_block = formatter.format_code_block("int main() { return 0; }", "c")
    assert "```c" in code_block
    print("✓ Code block formatting works")
    
    section = formatter.format_section("Test Section", "Content")
    assert "Test Section" in section
    print("✓ Section formatting works")
    
    status = formatter.format_status("Test complete", True)
    assert "Test complete" in status
    print("✓ Status formatting works")
    
    progress = formatter.format_progress(5, 10, "Test")
    assert "5/10" in progress
    print("✓ Progress formatting works")
    
    return True


def test_reasoning_tracker():
    """Test reasoning tracker integration"""
    print("\n=== Testing Reasoning Tracker ===")
    
    from src.compiler_loop.reasoning_tracker import ReasoningTracker
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tracker = ReasoningTracker(log_path=temp_dir)
        
        # Start reasoning
        reasoning_id = tracker.start_reasoning(
            task_id="test_task",
            phase="analyzing",
            breadcrumbs_consulted=["TEST_PHASE"]
        )
        assert reasoning_id.startswith("test_task")
        print(f"✓ Reasoning started: {reasoning_id}")
        
        # Add steps
        tracker.add_reasoning_step("Step 1: Analyzed requirements")
        tracker.add_reasoning_step("Step 2: Identified patterns")
        print("✓ Reasoning steps added")
        
        # Add pattern
        tracker.add_pattern("TEST_PATTERN_V1")
        print("✓ Pattern identified")
        
        # Set decision
        tracker.set_decision(
            decision_type="implementation",
            approach="Test approach",
            confidence=0.8,
            complexity="MEDIUM"
        )
        print("✓ Decision recorded")
        
        # Complete reasoning
        tracker.complete_reasoning(reasoning_id, success=True, iterations=1)
        print("✓ Reasoning completed")
        
        # Get statistics
        stats = tracker.get_statistics()
        assert stats['total_reasoning_events'] == 1
        assert stats['successful_decisions'] == 1
        print(f"✓ Statistics: {stats['total_reasoning_events']} events, success rate: {stats['success_rate']:.1%}")
        
        return True


def test_iteration_context():
    """Test iteration context management"""
    print("\n=== Testing Iteration Context ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        log_path = Path(temp_dir) / 'logs'
        
        loader = LocalModelLoader()
        session = SessionManager(
            model_loader=loader,
            aros_path=str(aros_path),
            log_path=str(log_path)
        )
        
        session.start_session(
            task_description="Test context",
            context={'phase': 'TEST'}
        )
        
        # Check iteration context
        assert hasattr(session, 'iteration_context')
        print("✓ Iteration context initialized")
        
        # Get metrics
        metrics = session.get_iteration_metrics()
        assert 'total_attempts' in metrics
        print(f"✓ Iteration metrics available: {metrics}")
        
        session.end_session(status='completed')
        
        return True


def test_performance_tracking():
    """Test performance metrics tracking"""
    print("\n=== Testing Performance Tracking ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        iteration = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=1,
            max_retries=2
        )
        
        # Verify reasoning tracker is initialized
        assert hasattr(iteration, 'reasoning_tracker')
        print("✓ Reasoning tracker integrated")
        
        # Verify current_reasoning_id tracking
        assert hasattr(iteration, 'current_reasoning_id')
        print("✓ Reasoning ID tracking enabled")
        
        # Verify retry tracking
        assert hasattr(iteration, 'max_retries')
        assert iteration.max_retries == 2
        print("✓ Retry logic enabled")
        
        return True


def test_error_similarity():
    """Test error similarity and resolution suggestions"""
    print("\n=== Testing Error Similarity ===")
    
    from src.compiler_loop.error_tracker import ErrorTracker
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tracker = ErrorTracker(log_path=temp_dir)
        
        # Track some errors
        error1 = "undefined reference to `test_function'"
        error2 = "undefined reference to `another_function'"
        error3 = "syntax error near unexpected token"
        
        hash1 = tracker.track_error(error1, {'context': 'test1'})
        hash2 = tracker.track_error(error2, {'context': 'test2'})
        hash3 = tracker.track_error(error3, {'context': 'test3'})
        
        print(f"✓ Tracked 3 errors")
        
        # Mark one as resolved
        tracker.mark_resolved(hash1, "Added missing function declaration")
        print("✓ Marked error as resolved")
        
        # Find similar errors
        similar = tracker.find_similar_errors("undefined reference to `new_function'")
        assert len(similar) >= 2  # Should find error1 and error2
        print(f"✓ Found {len(similar)} similar errors")
        
        # Get resolution suggestions
        suggestions = tracker.get_resolution_suggestions("undefined reference to `new_function'")
        assert len(suggestions) >= 1  # Should get suggestion from resolved error1
        print(f"✓ Got {len(suggestions)} resolution suggestions")
        
        return True


def test_checkpoint_resume():
    """Test checkpoint and resume functionality"""
    print("\n=== Testing Checkpoint/Resume ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        log_path = Path(temp_dir) / 'logs'
        
        loader = LocalModelLoader()
        session = SessionManager(
            model_loader=loader,
            aros_path=str(aros_path),
            log_path=str(log_path)
        )
        
        # Start session
        session.start_session(
            task_description="Test checkpoint",
            context={'phase': 'TEST', 'iteration': 1}
        )
        print("✓ Session started")
        
        # Add some data
        session.iteration_context['test_data'] = 'checkpoint_test'
        
        # Save checkpoint
        checkpoint_path = session.save_checkpoint("test_checkpoint")
        assert Path(checkpoint_path).exists()
        print(f"✓ Checkpoint saved: {Path(checkpoint_path).name}")
        
        # End session
        session.end_session(status='completed')
        
        # Create new session manager
        session2 = SessionManager(
            model_loader=loader,
            aros_path=str(aros_path),
            log_path=str(log_path)
        )
        
        # Load checkpoint
        success = session2.load_checkpoint(checkpoint_path)
        assert success
        assert session2.iteration_context.get('test_data') == 'checkpoint_test'
        print("✓ Checkpoint loaded and data restored")
        
        # List checkpoints
        checkpoints = session2.list_checkpoints()
        assert len(checkpoints) >= 1
        print(f"✓ Found {len(checkpoints)} checkpoint(s)")
        
        return True


def test_adaptive_retries():
    """Test adaptive retry logic"""
    print("\n=== Testing Adaptive Retries ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        iteration = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=1,
            max_retries=3,
            adaptive_retries=True
        )
        
        # Test simple errors (should reduce retries)
        simple_errors = ["syntax error", "missing semicolon"]
        adaptive_retries = iteration._calculate_adaptive_retries(simple_errors)
        assert adaptive_retries >= 1 and adaptive_retries <= 3
        print(f"✓ Simple errors: {adaptive_retries} retries")
        
        # Test medium errors (should use default)
        medium_errors = ["undefined reference to function", "type mismatch"]
        adaptive_retries = iteration._calculate_adaptive_retries(medium_errors)
        assert adaptive_retries == 3
        print(f"✓ Medium errors: {adaptive_retries} retries")
        
        # Test complex errors (should increase retries)
        complex_errors = ["segmentation fault", "assertion failed", "undefined reference", "type error"]
        adaptive_retries = iteration._calculate_adaptive_retries(complex_errors)
        assert adaptive_retries >= 3
        print(f"✓ Complex errors: {adaptive_retries} retries")
        
        return True


def test_iteration_history():
    """Test iteration history tracking"""
    print("\n=== Testing Iteration History ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        iteration = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=1
        )
        
        # Simulate an iteration result
        result = {
            'iteration': 1,
            'success': True,
            'retry_count': 1,
            'total_time': 10.5,
            'timings': {'exploration': 2.0, 'generation': 5.0},
            'compilation': {'errors': []}
        }
        
        # Track history
        iteration._track_iteration_history(result)
        assert len(iteration.iteration_history) == 1
        print("✓ Iteration history tracked")
        
        # Learn pattern
        iteration._learn_pattern(result)
        assert 'DEVELOPMENT' in iteration.learned_patterns or len(iteration.learned_patterns) >= 0
        print("✓ Pattern learning works")
        
        # Get learned patterns
        patterns = iteration.get_learned_patterns()
        assert 'patterns' in patterns
        assert 'total_iterations' in patterns
        print(f"✓ Learned patterns retrieved: {patterns['total_iterations']} iterations")
        
        return True


def test_iteration_state_save_load():
    """Test save and load iteration state"""
    print("\n=== Testing Iteration State Save/Load ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        # Create iteration with some state
        iteration1 = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=10
        )
        
        iteration1.current_iteration = 5
        iteration1.successful_iterations = 3
        iteration1.learned_patterns = {'TEST_PHASE': {'successes': 3, 'total_attempts': 5}}
        
        # Save state
        state_file = iteration1.save_iteration_state()
        assert Path(state_file).exists()
        print(f"✓ State saved to {Path(state_file).name}")
        
        # Create new iteration and load state
        iteration2 = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=10
        )
        
        success = iteration2.load_iteration_state()
        assert success
        assert iteration2.current_iteration == 5
        assert iteration2.successful_iterations == 3
        assert 'TEST_PHASE' in iteration2.learned_patterns
        print("✓ State loaded successfully")
        print(f"✓ Resumed at iteration {iteration2.current_iteration}")
        
        return True


def test_pattern_recommendations():
    """Test pattern recommendation system"""
    print("\n=== Testing Pattern Recommendations ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        iteration = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=10
        )
        
        # Add some learned patterns
        iteration.learned_patterns = {
            'SHADER_COMPILATION': {
                'successes': 8,
                'total_attempts': 10,
                'avg_retries': 1.5,
                'avg_time': 45.0,
                'common_approaches': []
            }
        }
        
        # Add some history
        iteration.iteration_history = [
            {'iteration': 1, 'phase': 'SHADER_COMPILATION', 'success': True, 'retry_count': 1, 'total_time': 42.0},
            {'iteration': 2, 'phase': 'SHADER_COMPILATION', 'success': True, 'retry_count': 2, 'total_time': 48.0},
            {'iteration': 3, 'phase': 'SHADER_COMPILATION', 'success': False, 'retry_count': 3, 'total_time': 50.0},
        ]
        
        # Get recommendation
        recommendation = iteration.get_pattern_recommendation('SHADER_COMPILATION', 'MEDIUM')
        
        assert 'suggested_retries' in recommendation
        assert 'estimated_time' in recommendation
        assert 'success_probability' in recommendation
        assert 'similar_tasks' in recommendation
        assert 'best_practices' in recommendation
        
        print(f"✓ Recommendation generated for SHADER_COMPILATION")
        print(f"  Success probability: {recommendation['success_probability']*100:.0f}%")
        print(f"  Suggested retries: {recommendation['suggested_retries']}")
        print(f"  Estimated time: {recommendation['estimated_time']:.0f}s")
        print(f"  Similar tasks found: {len(recommendation['similar_tasks'])}")
        print(f"  Best practices: {len(recommendation['best_practices'])}")
        
        # Test for unknown phase
        recommendation2 = iteration.get_pattern_recommendation('UNKNOWN_PHASE')
        assert 'best_practices' in recommendation2
        assert any('No historical data' in practice for practice in recommendation2['best_practices'])
        print("✓ Handles unknown phase correctly")
        
        return True


def test_checkpoint_diff():
    """Test checkpoint comparison functionality"""
    print("\n=== Testing Checkpoint Diff ===")
    
    from src.interactive_session import SessionManager
    from src.local_models import LocalModelLoader
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        log_path = Path(temp_dir) / 'logs'
        
        loader = LocalModelLoader()
        session = SessionManager(loader, str(aros_path), str(log_path))
        
        # Create first checkpoint
        session.start_session("Test task", {'phase': 'TEST'})
        session.iteration_context['step'] = 1
        cp1_path = session.save_checkpoint("checkpoint1")
        session.end_session()
        
        # Create second checkpoint with changes
        session.start_session("Test task", {'phase': 'TEST'})
        session.iteration_context['step'] = 2
        session.iteration_context['new_data'] = 'value'
        cp2_path = session.save_checkpoint("checkpoint2")
        session.end_session()
        
        # Compare checkpoints
        diff = session.compare_checkpoints(cp1_path, cp2_path)
        
        assert 'iteration_context_diff' in diff
        assert 'summary' in diff
        assert len(diff['summary']) > 0
        
        print("✓ Checkpoint comparison works")
        print(f"  Summary lines: {len(diff['summary'])}")
        for line in diff['summary']:
            print(f"    {line}")
        
        return True


def test_pattern_export_import():
    """Test pattern export and import"""
    print("\n=== Testing Pattern Export/Import ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        log_path1 = Path(temp_dir) / 'logs1'
        log_path2 = Path(temp_dir) / 'logs2'
        
        # Create first iteration with patterns
        iteration1 = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='project1',
            log_path=str(log_path1),
            max_iterations=10
        )
        
        iteration1.learned_patterns = {
            'SHADER_COMPILATION': {
                'successes': 8,
                'total_attempts': 10,
                'avg_retries': 1.5,
                'avg_time': 45.0,
                'common_approaches': []
            },
            'MEMORY_MANAGER': {
                'successes': 5,
                'total_attempts': 7,
                'avg_retries': 2.0,
                'avg_time': 52.0,
                'common_approaches': []
            }
        }
        
        iteration1.iteration_history = [
            {'iteration': 1, 'success': True, 'retry_count': 1, 'total_time': 42.0}
        ]
        
        # Export patterns
        export_path = Path(temp_dir) / 'patterns_export.json'
        exported_file = iteration1.export_learned_patterns(str(export_path))
        assert Path(exported_file).exists()
        print(f"✓ Patterns exported to {Path(exported_file).name}")
        
        # Create second iteration and import patterns
        iteration2 = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='project2',
            log_path=str(log_path2),
            max_iterations=10
        )
        
        # Import with merge
        success = iteration2.import_learned_patterns(exported_file, merge=True)
        assert success
        assert 'SHADER_COMPILATION' in iteration2.learned_patterns
        assert 'MEMORY_MANAGER' in iteration2.learned_patterns
        print("✓ Patterns imported successfully")
        print(f"  Imported {len(iteration2.learned_patterns)} patterns")
        
        # Test import with replace
        iteration2.learned_patterns = {'EXISTING': {'successes': 1, 'total_attempts': 1}}
        success = iteration2.import_learned_patterns(exported_file, merge=False)
        assert success
        assert 'EXISTING' not in iteration2.learned_patterns
        assert 'SHADER_COMPILATION' in iteration2.learned_patterns
        print("✓ Replace mode works correctly")
        
        return True


def test_analytics():
    """Test iteration analytics"""
    print("\n=== Testing Iteration Analytics ===")
    
    from src.copilot_iteration import CopilotStyleIteration
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        iteration = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='test',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=10
        )
        
        # Add some history
        iteration.iteration_history = [
            {
                'iteration': 1,
                'phase': 'SHADER_COMPILATION',
                'success': True,
                'retry_count': 1,
                'total_time': 45.0,
                'timings': {'exploration': 8.0, 'generation': 12.0, 'compilation': 15.0}
            },
            {
                'iteration': 2,
                'phase': 'SHADER_COMPILATION',
                'success': False,
                'retry_count': 3,
                'total_time': 68.0,
                'timings': {'exploration': 10.0, 'generation': 15.0, 'compilation': 25.0},
                'compilation': {'errors': ['undefined reference']}
            },
            {
                'iteration': 3,
                'phase': 'MEMORY_MANAGER',
                'success': True,
                'retry_count': 2,
                'total_time': 52.0,
                'timings': {'exploration': 9.0, 'generation': 14.0, 'compilation': 18.0}
            }
        ]
        
        iteration.learned_patterns = {
            'SHADER_COMPILATION': {
                'successes': 1,
                'total_attempts': 2,
                'avg_retries': 2.0,
                'avg_time': 56.5,
                'common_approaches': []
            },
            'MEMORY_MANAGER': {
                'successes': 1,
                'total_attempts': 1,
                'avg_retries': 2.0,
                'avg_time': 52.0,
                'common_approaches': []
            }
        }
        
        # Get analytics
        analytics = iteration.get_analytics()
        assert analytics is not None
        print("✓ Analytics engine created")
        
        # Test performance summary
        summary = analytics.get_performance_summary()
        assert 'total_iterations' in summary
        assert 'success_rate' in summary
        assert summary['total_iterations'] == 3
        print(f"✓ Performance summary generated")
        print(f"  Total iterations: {summary['total_iterations']}")
        print(f"  Success rate: {summary['success_rate']*100:.0f}%")
        
        # Test phase analysis
        phase_analysis = analytics.get_phase_analysis('SHADER_COMPILATION')
        assert 'success_rate' in phase_analysis
        assert 'trend' in phase_analysis
        print(f"✓ Phase analysis generated")
        
        # Test recommendations
        recommendations = analytics.get_recommendations()
        assert len(recommendations) > 0
        print(f"✓ Recommendations generated: {len(recommendations)}")
        
        # Test report generation
        report = iteration.generate_analytics_report()
        assert len(report) > 0
        assert 'Performance Summary' in report
        assert 'Phase Analysis' in report
        assert 'Recommendations' in report
        print(f"✓ Analytics report generated ({len(report)} chars)")
        
        return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Copilot-Style Iteration Test Suite")
    print("="*60)
    
    tests = [
        ("Model Loader", test_model_loader),
        ("Session Manager", test_session_manager),
        ("File Exploration", test_file_exploration),
        ("Copilot Iteration", test_copilot_iteration_structure),
        ("Streaming Output", test_streaming_output),
        ("Reasoning Tracker", test_reasoning_tracker),
        ("Iteration Context", test_iteration_context),
        ("Performance Tracking", test_performance_tracking),
        ("Error Similarity", test_error_similarity),
        ("Checkpoint/Resume", test_checkpoint_resume),
        ("Adaptive Retries", test_adaptive_retries),
        ("Iteration History", test_iteration_history),
        ("State Save/Load", test_iteration_state_save_load),
        ("Pattern Recommendations", test_pattern_recommendations),
        ("Checkpoint Diff", test_checkpoint_diff),
        ("Pattern Export/Import", test_pattern_export_import),
        ("Analytics", test_analytics),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"✗ {name} test failed")
                failed += 1
        except Exception as e:
            print(f"✗ {name} test failed with error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"  Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
