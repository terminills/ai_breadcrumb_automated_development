#!/usr/bin/env python3
"""
Test script to verify mock model fallback functionality
"""

import sys
import tempfile
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.local_models import LocalModelLoader
from src.interactive_session import SessionManager
from src.copilot_iteration import CopilotStyleIteration


def test_mock_models():
    """Test that mock models work when explicitly requested"""
    print("\n=== Testing Mock Model (Explicit Use) ===")
    
    # Create loader
    loader = LocalModelLoader()
    
    # Explicitly request mock models
    print("Loading codegen model in mock mode...")
    codegen = loader.load_model('codegen', use_mock=True)
    print(f"✓ Codegen loaded: {type(codegen).__name__}")
    
    print("Loading LLM model in mock mode...")
    llm = loader.load_model('llm', use_mock=True)
    print(f"✓ LLM loaded: {type(llm).__name__}")
    
    # Test basic functionality
    print("\nTesting mock codegen generation...")
    code = codegen.generate_with_breadcrumbs(
        task_description="Test function",
        context={'phase': 'TEST', 'status': 'IMPLEMENTING'}
    )
    assert len(code) > 0
    assert 'AI_PHASE' in code
    assert 'MOCK' in code.upper() or 'TODO' in code
    print(f"✓ Mock code generated ({len(code)} chars)")
    
    print("\nTesting mock LLM reasoning...")
    reasoning = llm.reason_about_task(
        task_description="Test task",
        context={'phase': 'TEST', 'project': 'test'}
    )
    assert 'reasoning' in reasoning
    assert len(reasoning['reasoning']) > 0
    print(f"✓ Mock reasoning generated ({len(reasoning['reasoning'])} chars)")
    
    print("\nTesting mock LLM exploration...")
    exploration = llm.explore_codebase(
        query="test query",
        file_contents=[{'path': 'test.c', 'content': 'test'}],
        breadcrumbs=[]
    )
    assert 'insights' in exploration
    print(f"✓ Mock exploration completed")
    
    return True


def test_error_messages():
    """Test that helpful error messages are shown when models aren't available"""
    print("\n=== Testing Error Messages (Without Torch) ===")
    
    loader = LocalModelLoader()
    
    # Try to load without torch (should fail with helpful message)
    try:
        print("Attempting to load codegen without torch...")
        codegen = loader.load_model('codegen', use_mock=False)
        print("✗ Should have failed but didn't")
        return False
    except ImportError as e:
        error_msg = str(e)
        print(f"✓ Got ImportError as expected")
        
        # Check that error message is helpful
        assert "AI MODEL" in error_msg.upper()
        assert "pip install" in error_msg
        assert "AI_MODEL_SETUP.md" in error_msg
        print("✓ Error message contains installation instructions")
        print(f"\nError message preview:\n{error_msg[:300]}...")
    
    return True


def test_session_with_mocks():
    """Test session manager with mock models (explicit)"""
    print("\n=== Testing Session with Mock Models (Explicit) ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        log_path = Path(temp_dir) / 'logs'
        
        # Create test file
        test_file = aros_path / 'test.c'
        test_file.write_text("void test() {}")
        
        # Create loader - will need to explicitly use mocks
        loader = LocalModelLoader()
        
        # Pre-load mock models explicitly
        loader.load_model('llm', use_mock=True)
        loader.load_model('codegen', use_mock=True)
        
        # Create session
        session = SessionManager(
            model_loader=loader,
            aros_path=str(aros_path),
            log_path=str(log_path)
        )
        
        # Start session
        session_id = session.start_session(
            task_description="Test with mocks",
            context={'phase': 'TEST'}
        )
        print(f"✓ Session started: {session_id}")
        
        # Test exploration (will use pre-loaded mock LLM)
        exploration = session.explore(query="test", max_files=5)
        print(f"✓ Exploration completed: {exploration['files_analyzed']} files")
        
        # Test reasoning (will use pre-loaded mock LLM)
        reasoning = session.reason()
        print(f"✓ Reasoning completed")
        
        # Test generation (will use pre-loaded mock codegen)
        generation = session.generate(use_exploration=True)
        assert len(generation['code']) > 0
        print(f"✓ Generation completed: {len(generation['code'])} chars")
        
        # Test review (will use pre-loaded mock LLM)
        review = session.review(code="void test() {}")
        print(f"✓ Review completed")
        
        session.end_session(status='completed')
        print("✓ Session completed successfully")
        
    return True


def test_iteration_with_mocks():
    """Test full iteration loop with mock models (explicit)"""
    print("\n=== Testing Iteration Loop with Mock Models (Explicit) ===")
    
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
        
        # Pre-load mock models explicitly
        iteration.model_loader.load_model('llm', use_mock=True)
        iteration.model_loader.load_model('codegen', use_mock=True)
        
        print("✓ Iteration system initialized with mock models")
        
        # Find tasks
        tasks = iteration._find_incomplete_tasks()
        print(f"✓ Found {len(tasks)} task(s)")
        
        # Run one iteration (will use pre-loaded mock models)
        result = iteration.run_interactive_iteration(
            task=tasks[0],
            enable_exploration=True,
            retry_on_failure=False
        )
        
        print(f"✓ Iteration completed")
        print(f"  - Success: {result['success']}")
        print(f"  - Total time: {result['total_time']:.2f}s")
        print(f"  - Retry count: {result['retry_count']}")
        
        # Check that phases ran
        assert 'generation' in result
        assert 'review' in result
        assert 'compilation' in result
        print("✓ All phases executed")
        
    return True


def main():
    """Run all mock model tests"""
    print("\n" + "="*60)
    print("  Mock Model Test Suite (Explicit Use)")
    print("="*60)
    
    tests = [
        ("Mock Models (Explicit)", test_mock_models),
        ("Error Messages", test_error_messages),
        ("Session with Mocks (Explicit)", test_session_with_mocks),
        ("Iteration with Mocks (Explicit)", test_iteration_with_mocks),
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
    
    if failed == 0:
        print("✓ All tests passed!")
        print("✓ Mock models work when explicitly requested")
        print("✓ Helpful error messages shown when models missing")
        print("✓ System will NOT silently fall back to mocks")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
