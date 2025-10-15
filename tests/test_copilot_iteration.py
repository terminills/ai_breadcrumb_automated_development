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
            max_iterations=1
        )
        
        # Verify reasoning tracker is initialized
        assert hasattr(iteration, 'reasoning_tracker')
        print("✓ Reasoning tracker integrated")
        
        # Verify current_reasoning_id tracking
        assert hasattr(iteration, 'current_reasoning_id')
        print("✓ Reasoning ID tracking enabled")
        
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
