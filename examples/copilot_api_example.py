#!/usr/bin/env python3
"""
Example: Using the Copilot-Style Iteration API
Demonstrates how to use the interactive session API
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.local_models import LocalModelLoader
from src.interactive_session import SessionManager


def example_simple_session():
    """Example 1: Simple session with exploration and generation"""
    print("\n" + "="*60)
    print("Example 1: Simple Session")
    print("="*60 + "\n")
    
    # Initialize components
    loader = LocalModelLoader()
    session = SessionManager(
        model_loader=loader,
        aros_path='aros-src',
        log_path='logs/examples'
    )
    
    # Start session
    print("Starting session...")
    session_id = session.start_session(
        task_description="Implement GPU memory allocation",
        context={
            'phase': 'MEMORY_MANAGER',
            'project': 'radeonsi',
            'status': 'IMPLEMENTING'
        }
    )
    print(f"Session ID: {session_id}")
    
    # Note: Actual model loading commented out for demo
    # In production, uncomment to use real models:
    # exploration = session.explore("GPU memory allocation")
    # print(f"\nExploration insights:\n{exploration['insights']}")
    
    # generation = session.generate(use_exploration=True)
    # print(f"\nGenerated code:\n{generation['code']}")
    
    # End session
    session.end_session(status='completed', summary='Demo completed')
    print(f"\nSession saved to: logs/examples/{session_id}.json")
    
    return session_id


def example_multi_turn_session():
    """Example 2: Multi-turn session with iteration"""
    print("\n" + "="*60)
    print("Example 2: Multi-Turn Session")
    print("="*60 + "\n")
    
    loader = LocalModelLoader()
    session = SessionManager(
        model_loader=loader,
        aros_path='aros-src',
        log_path='logs/examples'
    )
    
    # Start session
    session_id = session.start_session(
        task_description="Implement shader compilation",
        context={'phase': 'SHADER_PIPELINE', 'project': 'radeonsi'}
    )
    
    print("Turn 1: Initial exploration")
    # session.explore("shader compilation")
    
    print("Turn 2: Generate first attempt")
    # generation1 = session.generate()
    
    print("Turn 3: Iterate with feedback")
    # generation2 = session.iterate(
    #     feedback="Add error handling",
    #     errors=["Missing null check"]
    # )
    
    # Get session summary
    summary = session.get_session_summary()
    print(f"\nSession Summary:")
    print(f"  ID: {summary['id']}")
    print(f"  Task: {summary['task']}")
    print(f"  Status: {summary['status']}")
    print(f"  Turns: {summary['turns']}")
    
    session.end_session(status='completed')
    return session_id


def example_with_review():
    """Example 3: Session with code review"""
    print("\n" + "="*60)
    print("Example 3: Code Review Session")
    print("="*60 + "\n")
    
    loader = LocalModelLoader()
    session = SessionManager(
        model_loader=loader,
        aros_path='aros-src',
        log_path='logs/examples'
    )
    
    session_id = session.start_session(
        task_description="Implement buffer management",
        context={'phase': 'BUFFER_MANAGER', 'project': 'radeonsi'}
    )
    
    # Simulate code generation
    sample_code = """
// AI_PHASE: BUFFER_MANAGER
// AI_STATUS: IMPLEMENTING
// AI_STRATEGY: Implement buffer allocation with reference counting

struct Buffer {
    void *data;
    size_t size;
    int ref_count;
};

struct Buffer* buffer_create(size_t size) {
    struct Buffer *buf = malloc(sizeof(struct Buffer));
    buf->data = malloc(size);
    buf->size = size;
    buf->ref_count = 1;
    return buf;
}

void buffer_destroy(struct Buffer *buf) {
    if (--buf->ref_count == 0) {
        free(buf->data);
        free(buf);
    }
}
"""
    
    print("Generated code sample (simulated)")
    print(sample_code)
    
    # Review the code (would use real LLM in production)
    # review = session.review(code=sample_code)
    # print(f"\nReview Results:\n{review['review']}")
    
    session.end_session(status='completed')
    return session_id


def example_configuration():
    """Example 4: Custom configuration"""
    print("\n" + "="*60)
    print("Example 4: Custom Configuration")
    print("="*60 + "\n")
    
    # Load with custom config
    loader = LocalModelLoader()
    
    # Get configurations
    codegen_config = loader.get_codegen_config()
    llm_config = loader.get_llm_config()
    exploration_config = loader.get_exploration_config()
    
    print("Current Configuration:")
    print(f"\nCodegen Model:")
    print(f"  Path: {codegen_config.get('model_path', 'default')}")
    print(f"  Device: {codegen_config.get('device', 'cpu')}")
    print(f"  Max Length: {codegen_config.get('max_length', 512)}")
    
    print(f"\nLLM Model:")
    print(f"  Path: {llm_config.get('model_path', 'default')}")
    print(f"  Device: {llm_config.get('device', 'cpu')}")
    print(f"  Context Window: {llm_config.get('context_window', 4096)}")
    
    print(f"\nExploration:")
    print(f"  Enabled: {exploration_config.get('enabled', True)}")
    print(f"  Max Files: {exploration_config.get('max_files_to_scan', 50)}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  Copilot-Style Iteration API Examples")
    print("="*70)
    
    print("\nNote: These examples demonstrate the API structure.")
    print("Actual model loading is commented out to avoid requiring model downloads.")
    print("In production, uncomment the model calls to use real AI models.")
    
    try:
        # Run examples
        example_simple_session()
        example_multi_turn_session()
        example_with_review()
        example_configuration()
        
        print("\n" + "="*70)
        print("  All Examples Completed Successfully!")
        print("="*70)
        print("\nCheck logs/examples/ for session logs")
        print("\nTo use with real models:")
        print("  1. Ensure torch and transformers are installed")
        print("  2. Uncomment model loading calls in examples")
        print("  3. Run: python examples/copilot_api_example.py")
        print("\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
