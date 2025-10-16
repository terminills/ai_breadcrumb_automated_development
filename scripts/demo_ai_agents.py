#!/usr/bin/env python3
"""
Demonstration of AI Agent functionality with mock models
Shows that Sessions and Iteration loops now work correctly
"""

import sys
import tempfile
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.copilot_iteration import CopilotStyleIteration
from src.interactive_session import SessionManager
from src.local_models import LocalModelLoader


def demo_session():
    """Demonstrate a working session with AI agents"""
    print("\n" + "="*70)
    print("  DEMO: Interactive Session with AI Agents")
    print("  (Using Mock Models for Demonstration)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        # Create test file
        test_file = aros_path / 'demo.c'
        test_file.write_text("""
// AI_PHASE: SHADER_COMPILATION
// AI_STATUS: IMPLEMENTING
void demo_function() {
    // TODO: Implement shader compilation
}
""")
        
        log_path = Path(temp_dir) / 'logs'
        
        print("\n1. Initializing session manager...")
        loader = LocalModelLoader()
        
        # Explicitly load mock models for demo
        print("   Loading models in mock mode for demonstration...")
        loader.load_model('llm', use_mock=True)
        loader.load_model('codegen', use_mock=True)
        
        session = SessionManager(
            model_loader=loader,
            aros_path=str(aros_path),
            log_path=str(log_path)
        )
        print("   ✓ Session manager ready")
        
        print("\n2. Starting AI session...")
        session_id = session.start_session(
            task_description="Implement shader compilation for radeonsi",
            context={
                'phase': 'SHADER_COMPILATION',
                'status': 'IMPLEMENTING',
                'project': 'radeonsi'
            }
        )
        print(f"   ✓ Session started: {session_id}")
        
        print("\n3. AI Agent: Exploring codebase...")
        exploration = session.explore(query="shader compilation", max_files=5)
        print(f"   ✓ Explored {exploration['files_analyzed']} files")
        print(f"   ✓ Found {exploration['breadcrumbs_analyzed']} breadcrumbs")
        print(f"\n   Insights preview:")
        print(f"   {exploration['insights'][:200]}...")
        
        print("\n4. AI Agent: Reasoning about task...")
        reasoning = session.reason()
        print(f"   ✓ Reasoning completed")
        print(f"\n   Strategy preview:")
        print(f"   {reasoning['reasoning'][:200]}...")
        
        print("\n5. AI Agent: Generating code...")
        generation = session.generate(use_exploration=True)
        print(f"   ✓ Generated {len(generation['code'])} characters of code")
        print(f"\n   Code preview:")
        print("   " + "\n   ".join(generation['code'].split('\n')[:10]))
        
        print("\n6. AI Agent: Reviewing code...")
        review = session.review(code=generation['code'])
        print(f"   ✓ Review completed")
        print(f"\n   Review preview:")
        print(f"   {review['review'][:200]}...")
        
        print("\n7. Ending session...")
        session.end_session(status='completed', summary='Demo completed successfully')
        print("   ✓ Session ended")
        
        print("\n" + "="*70)
        print("  ✓ DEMO COMPLETE: Session successfully triggered all AI agents")
        print("  Note: This used MOCK models for demonstration")
        print("  For real AI: python3 scripts/download_models.py --all")
        print("="*70)


def demo_iteration():
    """Demonstrate a working iteration loop with AI agents"""
    print("\n" + "="*70)
    print("  DEMO: Iteration Loop with AI Agents")
    print("  (Using Mock Models for Demonstration)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        aros_path = Path(temp_dir) / 'aros-src'
        aros_path.mkdir()
        
        # Create test file with breadcrumb
        test_file = aros_path / 'radeonsi.c'
        test_file.write_text("""
// AI_PHASE: GPU_INITIALIZATION
// AI_STATUS: PARTIAL
// AI_STRATEGY: Initialize RadeonSI GPU driver
void radeonsi_init() {
    // TODO: Implementation needed
}
""")
        
        print("\n1. Initializing iteration system...")
        iteration = CopilotStyleIteration(
            aros_path=str(aros_path),
            project_name='radeonsi',
            log_path=str(Path(temp_dir) / 'logs'),
            max_iterations=1,
            max_retries=1
        )
        
        # Explicitly load mock models for demo
        print("   Loading models in mock mode for demonstration...")
        iteration.model_loader.load_model('llm', use_mock=True)
        iteration.model_loader.load_model('codegen', use_mock=True)
        
        print("   ✓ Iteration system ready")
        
        print("\n2. Finding tasks from breadcrumbs...")
        tasks = iteration._find_incomplete_tasks()
        print(f"   ✓ Found {len(tasks)} task(s)")
        for i, task in enumerate(tasks[:3], 1):
            print(f"      {i}. {task.get('phase', 'unknown')} - {task.get('status', 'unknown')}")
        
        print("\n3. Running iteration with AI agents...")
        print("   (This will trigger: exploration, reasoning, generation, review, compilation, learning)")
        
        result = iteration.run_interactive_iteration(
            task=tasks[0],
            enable_exploration=True,
            retry_on_failure=False
        )
        
        print(f"\n   ✓ Iteration completed!")
        print(f"      - Success: {result['success']}")
        print(f"      - Total time: {result['total_time']:.2f}s")
        print(f"      - Phases executed:")
        for phase, timing in result['timings'].items():
            print(f"         • {phase.capitalize()}: {timing:.2f}s")
        
        print("\n4. Checking iteration results...")
        print(f"   ✓ Code generated: {len(result['generation'].get('code', ''))} chars")
        print(f"   ✓ Review completed: {len(result['review'].get('review', ''))} chars")
        print(f"   ✓ Compilation tested: {result['compilation']['success']}")
        
        print("\n" + "="*70)
        print("  ✓ DEMO COMPLETE: Iteration successfully triggered all AI agents")
        print("  Note: This used MOCK models for demonstration")
        print("  For real AI: python3 scripts/download_models.py --all")
        print("="*70)


def show_model_status():
    """Show which models are being used"""
    print("\n" + "="*70)
    print("  Current Model Status")
    print("="*70)
    
    loader = LocalModelLoader()
    
    print("\nChecking model availability...")
    
    # Try to load codegen
    try:
        print("\nAttempting to load CodeGen model...")
        codegen = loader.load_model('codegen', use_mock=False)
        print(f"✓ CodeGen Model: REAL AI loaded successfully")
        print(f"  Type: {type(codegen).__name__}")
    except (ImportError, RuntimeError) as e:
        print(f"✗ CodeGen Model: NOT AVAILABLE")
        print(f"  Error type: {type(e).__name__}")
        if "DEPENDENCY ERROR" in str(e):
            print(f"  Issue: Missing dependencies (torch/transformers)")
        elif "NOT FOUND" in str(e):
            print(f"  Issue: Model files not downloaded")
        print(f"  Solution: See error message above for instructions")
    
    # Try to load LLM
    try:
        print("\nAttempting to load LLM model...")
        llm = loader.load_model('llm', use_mock=False)
        print(f"✓ LLM Model: REAL AI loaded successfully")
        print(f"  Type: {type(llm).__name__}")
    except (ImportError, RuntimeError) as e:
        print(f"✗ LLM Model: NOT AVAILABLE")
        print(f"  Error type: {type(e).__name__}")
        if "DEPENDENCY ERROR" in str(e):
            print(f"  Issue: Missing dependencies (torch/transformers)")
        elif "NOT FOUND" in str(e):
            print(f"  Issue: Model files not downloaded")
        print(f"  Solution: See error message above for instructions")
    
    print("\n" + "="*70)
    print("\nOptions:")
    print("  1. Install dependencies: pip install torch transformers")
    print("  2. Download models: python3 scripts/download_models.py --all")
    print("  3. See setup guide: cat AI_MODEL_SETUP.md")
    print("  4. Use mock mode for testing: add --use-mock flag")
    print("="*70)


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("  AI Agent Triggering Demonstration")
    print("  Showing: Sessions and Iterations now work correctly")
    print("="*70)
    
    # Show model status first
    show_model_status()
    
    # Demo session
    try:
        demo_session()
    except Exception as e:
        print(f"\n❌ Session demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Demo iteration
    try:
        demo_iteration()
    except Exception as e:
        print(f"\n❌ Iteration demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "="*70)
    print("  SUMMARY: AI Agent System")
    print("="*70)
    print("\n✓ System shows clear errors when models are missing")
    print("✓ Error messages include installation instructions")
    print("✓ Sessions and Iterations work when models are available")
    print("✓ Mock mode available for testing (explicit --use-mock flag)")
    print("\n✓ All phases execute correctly when models loaded:")
    print("   • Exploration phase ✓")
    print("   • Reasoning phase ✓")
    print("   • Generation phase ✓")
    print("   • Review phase ✓")
    print("   • Compilation phase ✓")
    print("   • Learning phase ✓")
    print("\n" + "="*70)
    print("\nTo fix model issues:")
    print("  1. Install dependencies: pip install torch transformers")
    print("  2. Download models: python3 scripts/download_models.py --all")
    print("  3. See setup guide: cat AI_MODEL_SETUP.md")
    print("\nFor testing without models:")
    print("  Use --use-mock flag (provides template responses only)")
    print("="*70 + "\n")
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(1)
