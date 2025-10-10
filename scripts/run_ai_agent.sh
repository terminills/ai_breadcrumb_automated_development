#!/bin/bash
# Run the AI Agent in the Compiler-in-Loop
# Implements: Train -> Develop -> Compile -> Errors -> Learn

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "AROS AI Agent - Compiler-in-Loop"
echo "================================================"
echo ""

# Parse arguments
MODE="${1:-ITERATE}"
PROJECT="${2:-radeonsi}"
MAX_ITERATIONS="${3:-10}"

echo "Configuration:"
echo "  Mode: $MODE"
echo "  Project: $PROJECT"
echo "  Max Iterations: $MAX_ITERATIONS"
echo ""

# Check if AROS is cloned
if [ ! -d "$PROJECT_ROOT/aros-src" ]; then
    echo "Error: AROS repository not found"
    echo "Please run: ./scripts/clone_aros.sh"
    exit 1
fi

# Create log directory
LOG_DIR="$PROJECT_ROOT/logs/agent"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/agent_$TIMESTAMP.log"

echo "Starting AI Agent at $(date)" | tee "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run the AI agent Python script
python3 << 'PYTHON_SCRIPT'
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.breadcrumb_parser import BreadcrumbParser
from src.compiler_loop import CompilerLoop, ErrorTracker

class AIAgent:
    """AI Agent for AROS development loop"""
    
    def __init__(self, aros_path, project_name, max_iterations):
        self.aros_path = Path(aros_path)
        self.project_name = project_name
        self.max_iterations = max_iterations
        
        self.parser = BreadcrumbParser()
        self.compiler = CompilerLoop(str(aros_path), str(project_root / 'logs' / 'compile'))
        self.error_tracker = ErrorTracker(str(project_root / 'logs' / 'errors'))
        
        self.iteration = 0
    
    def analyze_breadcrumbs(self):
        """Phase 1: Analyze existing breadcrumbs to understand current state"""
        print(f"\n{'='*50}")
        print(f"Phase 1: Analyzing Breadcrumbs")
        print(f"{'='*50}")
        
        # Parse C files in target project
        c_files = list(self.aros_path.rglob('*.c'))[:50]  # Sample
        
        for c_file in c_files:
            try:
                self.parser.parse_file(str(c_file))
            except Exception as e:
                pass
        
        stats = self.parser.get_statistics()
        print(f"Found {stats['total_breadcrumbs']} breadcrumbs")
        print(f"Phases: {stats['phases']}")
        print(f"Statuses: {stats['statuses']}")
        
        # Find incomplete tasks
        incomplete = self.parser.get_breadcrumbs_by_status('PARTIAL')
        incomplete += self.parser.get_breadcrumbs_by_status('NOT_STARTED')
        
        if incomplete:
            print(f"\nIncomplete tasks: {len(incomplete)}")
            for bc in incomplete[:3]:
                print(f"  - {bc.phase}: {bc.strategy}")
        
        return incomplete
    
    def generate_code(self, task):
        """Phase 2: Generate code for incomplete task"""
        print(f"\n{'='*50}")
        print(f"Phase 2: Generating Code")
        print(f"{'='*50}")
        
        print(f"Task: {task.phase}")
        print(f"Status: {task.status}")
        print(f"Strategy: {task.strategy}")
        
        # In production, this would use the fine-tuned model
        # For demonstration, we simulate code generation
        print("\nSimulating AI code generation...")
        print("  - Reading task context from breadcrumb")
        print("  - Generating code with breadcrumb metadata")
        print("  - Following AROS patterns and conventions")
        
        return True
    
    def compile_and_test(self):
        """Phase 3: Compile the generated code"""
        print(f"\n{'='*50}")
        print(f"Phase 3: Compiling Code")
        print(f"{'='*50}")
        
        # In a real scenario, this would compile AROS
        # For demonstration, we simulate compilation
        print("Running compilation...")
        
        # Simulate compilation result
        result = {
            'success': self.iteration % 3 != 0,  # Fail every 3rd iteration
            'errors': [],
            'warnings': []
        }
        
        if not result['success']:
            # Simulate some errors
            result['errors'] = [
                {'message': f"error: undefined reference to 'InitAROSModule_{self.iteration}'"},
                {'message': f"error: incompatible pointer type in initialization"}
            ]
            
            print(f"\n❌ Compilation FAILED")
            print(f"   Errors: {len(result['errors'])}")
            for err in result['errors']:
                print(f"   - {err['message']}")
        else:
            print(f"\n✓ Compilation SUCCESSFUL")
        
        return result
    
    def learn_from_errors(self, compile_result):
        """Phase 4: Learn from compilation errors"""
        print(f"\n{'='*50}")
        print(f"Phase 4: Learning from Errors")
        print(f"{'='*50}")
        
        if compile_result['success']:
            print("No errors to learn from - compilation successful!")
            return True
        
        # Track errors
        for error in compile_result['errors']:
            error_hash = self.error_tracker.track_error(
                error['message'],
                {'iteration': self.iteration, 'project': self.project_name}
            )
            print(f"Tracked error: {error_hash}")
        
        # Analyze error patterns
        stats = self.error_tracker.get_statistics()
        print(f"\nError Database Stats:")
        print(f"  Total unique errors: {stats['total_unique_errors']}")
        print(f"  Resolved: {stats['resolved_errors']}")
        print(f"  Patterns: {stats['patterns']}")
        
        return False
    
    def run_iteration(self):
        """Run one complete iteration of the loop"""
        self.iteration += 1
        
        print(f"\n{'#'*60}")
        print(f"# ITERATION {self.iteration}/{self.max_iterations}")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"{'#'*60}")
        
        # 1. Analyze breadcrumbs
        incomplete_tasks = self.analyze_breadcrumbs()
        
        if not incomplete_tasks:
            print("\n✓ No incomplete tasks found!")
            return True
        
        # 2. Select a task and generate code
        task = incomplete_tasks[0]
        self.generate_code(task)
        
        # 3. Compile and test
        compile_result = self.compile_and_test()
        
        # 4. Learn from errors
        success = self.learn_from_errors(compile_result)
        
        print(f"\n{'='*60}")
        print(f"Iteration {self.iteration} {'✓ Complete' if success else '⚠ Needs Retry'}")
        print(f"{'='*60}")
        
        time.sleep(1)  # Pause between iterations
        return success
    
    def run(self):
        """Run the complete agent loop"""
        print(f"\nStarting AI Agent Loop")
        print(f"Project: {self.project_name}")
        print(f"AROS Path: {self.aros_path}")
        
        successful_iterations = 0
        
        for i in range(self.max_iterations):
            if self.run_iteration():
                successful_iterations += 1
        
        print(f"\n{'='*60}")
        print(f"AGENT LOOP COMPLETE")
        print(f"{'='*60}")
        print(f"Total Iterations: {self.max_iterations}")
        print(f"Successful: {successful_iterations}")
        print(f"Failed: {self.max_iterations - successful_iterations}")
        print(f"\nAll logs saved to: logs/")

# Main execution
if __name__ == '__main__':
    agent = AIAgent(
        aros_path=project_root / 'aros-src',
        project_name='radeonsi',
        max_iterations=5  # Demonstration limit
    )
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\nAgent interrupted by user")
    except Exception as e:
        print(f"\n\nError running agent: {e}")
        import traceback
        traceback.print_exc()

PYTHON_SCRIPT

echo "" | tee -a "$LOG_FILE"
echo "AI Agent completed at $(date)" | tee -a "$LOG_FILE"
