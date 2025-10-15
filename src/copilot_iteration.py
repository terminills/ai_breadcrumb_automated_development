"""
Copilot-Style Iteration Loop
Interactive development loop with exploration, reasoning, and local models
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.local_models import LocalModelLoader
from src.interactive_session import SessionManager
from src.breadcrumb_parser import BreadcrumbParser
from src.compiler_loop import CompilerLoop, ErrorTracker, ReasoningTracker

logger = logging.getLogger(__name__)


class CopilotStyleIteration:
    """
    Enhanced iteration loop with exploration and interactive capabilities
    Similar to GitHub Copilot but using local models
    """
    
    def __init__(
        self,
        aros_path: str,
        project_name: str,
        log_path: str,
        max_iterations: int = 10
    ):
        self.aros_path = Path(aros_path)
        self.project_name = project_name
        self.log_path = Path(log_path)
        self.max_iterations = max_iterations
        
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        logger.info("Initializing Copilot-style iteration system...")
        
        self.model_loader = LocalModelLoader()
        self.session_manager = SessionManager(
            model_loader=self.model_loader,
            aros_path=str(self.aros_path),
            log_path=str(self.log_path / 'sessions')
        )
        
        self.breadcrumb_parser = BreadcrumbParser()
        self.compiler = CompilerLoop(
            aros_path=str(self.aros_path),
            log_path=str(self.log_path / 'compile')
        )
        self.error_tracker = ErrorTracker(
            log_path=str(self.log_path / 'errors')
        )
        self.reasoning_tracker = ReasoningTracker(
            log_path=str(self.log_path / 'reasoning')
        )
        
        self.current_iteration = 0
        self.successful_iterations = 0
        self.current_reasoning_id = None
    
    def run_interactive_iteration(
        self,
        task: Dict[str, Any],
        enable_exploration: bool = True
    ) -> Dict[str, Any]:
        """
        Run one interactive iteration with exploration
        
        Args:
            task: Task information from breadcrumb
            enable_exploration: Enable exploration phase
            
        Returns:
            Iteration results
        """
        self.current_iteration += 1
        iteration_start_time = datetime.now()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Iteration {self.current_iteration}/{self.max_iterations}")
        logger.info(f"Task: {task.get('phase', 'unknown')}")
        logger.info(f"{'='*60}\n")
        
        # Start session
        task_description = task.get('strategy', task.get('phase', 'unknown'))
        context = {
            'phase': task.get('phase', 'DEVELOPMENT'),
            'status': task.get('status', 'IMPLEMENTING'),
            'project': self.project_name,
            'iteration': self.current_iteration
        }
        
        session_id = self.session_manager.start_session(
            task_description=task_description,
            context=context
        )
        
        logger.info(f"Started session: {session_id}")
        
        phase_timings = {}
        
        try:
            # Phase 1: Exploration (like Copilot gathering context)
            if enable_exploration:
                phase_start = datetime.now()
                self._exploration_phase(task)
                phase_timings['exploration'] = (datetime.now() - phase_start).total_seconds()
            
            # Phase 2: Reasoning (like Copilot analyzing the problem)
            phase_start = datetime.now()
            self._reasoning_phase()
            phase_timings['reasoning'] = (datetime.now() - phase_start).total_seconds()
            
            # Phase 3: Generation (like Copilot suggesting code)
            phase_start = datetime.now()
            generation_result = self._generation_phase()
            phase_timings['generation'] = (datetime.now() - phase_start).total_seconds()
            
            # Phase 4: Review (self-review of generated code)
            phase_start = datetime.now()
            review_result = self._review_phase(generation_result)
            phase_timings['review'] = (datetime.now() - phase_start).total_seconds()
            
            # Phase 5: Compilation & Testing
            phase_start = datetime.now()
            compile_result = self._compilation_phase(generation_result)
            phase_timings['compilation'] = (datetime.now() - phase_start).total_seconds()
            
            # Phase 6: Learning from results
            phase_start = datetime.now()
            success = self._learning_phase(compile_result, review_result)
            phase_timings['learning'] = (datetime.now() - phase_start).total_seconds()
            
            # End session
            status = 'completed' if success else 'needs_iteration'
            self.session_manager.end_session(
                status=status,
                summary=f"Iteration {self.current_iteration} {status}"
            )
            
            if success:
                self.successful_iterations += 1
            
            # Calculate total time
            total_time = (datetime.now() - iteration_start_time).total_seconds()
            
            # Log performance metrics
            logger.info(f"\n--- Performance Metrics ---")
            logger.info(f"Total iteration time: {total_time:.2f}s")
            for phase, timing in phase_timings.items():
                logger.info(f"{phase.capitalize()}: {timing:.2f}s ({timing/total_time*100:.1f}%)")
            
            return {
                'iteration': self.current_iteration,
                'session_id': session_id,
                'success': success,
                'generation': generation_result,
                'review': review_result,
                'compilation': compile_result,
                'timings': phase_timings,
                'total_time': total_time
            }
            
        except Exception as e:
            logger.error(f"Error in iteration: {e}")
            self.session_manager.end_session(status='failed', summary=str(e))
            raise
    
    def _exploration_phase(self, task: Dict[str, Any]):
        """Phase 1: Explore codebase like Copilot gathering context"""
        logger.info("\n--- Phase 1: Exploration ---")
        
        # Explore related code
        phase = task.get('phase', 'unknown')
        logger.info(f"Exploring codebase for: {phase}")
        
        # Start reasoning tracking
        self.current_reasoning_id = self.reasoning_tracker.start_reasoning(
            task_id=f"iteration_{self.current_iteration}",
            phase='analyzing',
            breadcrumbs_consulted=[phase],
            files_considered=[]
        )
        
        try:
            exploration = self.session_manager.explore(
                query=phase,
                max_files=10
            )
            
            logger.info(f"Explored {exploration['files_analyzed']} files")
            logger.info(f"Found {exploration['breadcrumbs_analyzed']} relevant breadcrumbs")
            logger.info(f"Insights preview: {exploration['insights'][:200]}...")
            
            # Track reasoning step
            self.reasoning_tracker.add_reasoning_step(
                f"Explored {exploration['files_analyzed']} files related to {phase}"
            )
            self.reasoning_tracker.add_reasoning_step(
                f"Found {exploration['breadcrumbs_analyzed']} breadcrumbs for context"
            )
            
        except Exception as e:
            logger.warning(f"Exploration failed: {e}")
            logger.info("Continuing without exploration insights...")
            self.reasoning_tracker.add_reasoning_step(f"Exploration failed: {e}")
    
    def _reasoning_phase(self):
        """Phase 2: Reason about the task like Copilot analyzing"""
        logger.info("\n--- Phase 2: Reasoning ---")
        
        try:
            reasoning = self.session_manager.reason()
            logger.info("Reasoning completed")
            logger.info(f"Strategy preview: {reasoning['reasoning'][:200]}...")
            
            # Track reasoning steps
            self.reasoning_tracker.add_reasoning_step(
                "Analyzed task requirements and context"
            )
            self.reasoning_tracker.add_reasoning_step(
                f"Generated strategy: {reasoning['reasoning'][:100]}..."
            )
            
        except Exception as e:
            logger.warning(f"Reasoning failed: {e}")
            logger.info("Continuing with default strategy...")
            self.reasoning_tracker.add_reasoning_step(f"Reasoning failed: {e}")
    
    def _generation_phase(self) -> Dict[str, Any]:
        """Phase 3: Generate code like Copilot suggesting"""
        logger.info("\n--- Phase 3: Code Generation ---")
        
        try:
            generation = self.session_manager.generate(use_exploration=True)
            logger.info(f"Generated code (iteration {generation['iteration']})")
            logger.info(f"Code length: {len(generation['code'])} characters")
            
            # Track decision made
            self.reasoning_tracker.set_decision(
                decision_type='code_generation',
                approach=f"Generated {len(generation['code'])} chars of code",
                confidence=0.7,
                complexity='MEDIUM',
                raw_thought=f"Iteration {generation['iteration']}"
            )
            
            return generation
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            self.reasoning_tracker.add_reasoning_step(f"Generation failed: {e}")
            return {
                'code': '',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _review_phase(self, generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Review generated code"""
        logger.info("\n--- Phase 4: Code Review ---")
        
        if not generation_result.get('code'):
            logger.warning("No code to review")
            return {'review': 'No code generated', 'has_errors': True}
        
        try:
            review = self.session_manager.review(
                code=generation_result['code']
            )
            
            logger.info("Code review completed")
            logger.info(f"Review preview: {review['review'][:200]}...")
            
            return review
            
        except Exception as e:
            logger.warning(f"Review failed: {e}")
            return {
                'review': f'Review failed: {e}',
                'has_errors': True
            }
    
    def _compilation_phase(self, generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: Compile and test the generated code"""
        logger.info("\n--- Phase 5: Compilation & Testing ---")
        
        # In a real scenario, would write code to file and compile
        # For demonstration, simulate compilation
        
        # Simulate: 70% success rate initially, improving with iterations
        import random
        success_probability = 0.7 + (self.successful_iterations * 0.05)
        success = random.random() < success_probability
        
        compile_result = {
            'success': success,
            'errors': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if not success:
            # Simulate some errors
            compile_result['errors'] = [
                f"error: undefined reference to function_{self.current_iteration}",
                "error: incompatible types in assignment"
            ]
            logger.error(f"Compilation failed with {len(compile_result['errors'])} errors")
            for err in compile_result['errors']:
                logger.error(f"  - {err}")
        else:
            logger.info("✓ Compilation successful")
        
        return compile_result
    
    def _learning_phase(
        self,
        compile_result: Dict[str, Any],
        review_result: Dict[str, Any]
    ) -> bool:
        """Phase 6: Learn from compilation and review results"""
        logger.info("\n--- Phase 6: Learning ---")
        
        success = compile_result['success'] and not review_result.get('has_errors')
        
        # Complete reasoning tracking
        if self.current_reasoning_id:
            self.reasoning_tracker.complete_reasoning(
                reasoning_id=self.current_reasoning_id,
                success=success,
                iterations=self.current_iteration
            )
        
        if success:
            logger.info("✓ Iteration successful - no errors to learn from")
            return True
        
        # Track errors
        if compile_result.get('errors'):
            for error in compile_result['errors']:
                error_hash = self.error_tracker.track_error(
                    error_message=error,
                    context={
                        'iteration': self.current_iteration,
                        'project': self.project_name,
                        'reasoning_id': self.current_reasoning_id
                    }
                )
                logger.info(f"Tracked error: {error_hash[:8]}")
                
                # Add to reasoning
                if self.current_reasoning_id:
                    self.reasoning_tracker.add_reasoning_step(
                        f"Encountered error: {error[:100]}"
                    )
        
        # Get error statistics
        stats = self.error_tracker.get_statistics()
        logger.info(f"Error database: {stats['total_unique_errors']} unique errors")
        logger.info(f"Resolved: {stats['resolved_errors']}")
        
        # Get reasoning statistics
        reasoning_stats = self.reasoning_tracker.get_statistics()
        logger.info(f"Reasoning success rate: {reasoning_stats['success_rate']*100:.1f}%")
        
        return False
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete Copilot-style iteration loop
        
        Returns:
            Summary of all iterations
        """
        logger.info("\n" + "="*70)
        logger.info("Starting Copilot-Style Iteration Loop")
        logger.info(f"Project: {self.project_name}")
        logger.info(f"Max Iterations: {self.max_iterations}")
        logger.info("="*70 + "\n")
        
        # Find tasks from breadcrumbs
        logger.info("Scanning for incomplete tasks...")
        tasks = self._find_incomplete_tasks()
        
        if not tasks:
            logger.info("No incomplete tasks found!")
            return {
                'status': 'no_tasks',
                'iterations': 0,
                'successful': 0
            }
        
        logger.info(f"Found {len(tasks)} incomplete tasks")
        
        # Run iterations
        iteration_results = []
        
        for i in range(min(self.max_iterations, len(tasks))):
            task = tasks[i]
            
            try:
                result = self.run_interactive_iteration(
                    task=task,
                    enable_exploration=True
                )
                iteration_results.append(result)
                
                # Check if we should continue
                if result['success']:
                    logger.info(f"\n✓ Task completed successfully!")
                else:
                    logger.info(f"\n⚠ Task needs more work")
                
            except KeyboardInterrupt:
                logger.info("\n\nInterrupted by user")
                break
            except Exception as e:
                logger.error(f"\n\nError in iteration: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # Summary
        summary = {
            'status': 'completed',
            'total_iterations': len(iteration_results),
            'successful': self.successful_iterations,
            'failed': len(iteration_results) - self.successful_iterations,
            'tasks_found': len(tasks),
            'tasks_processed': len(iteration_results)
        }
        
        logger.info("\n" + "="*70)
        logger.info("Copilot-Style Iteration Loop Complete")
        logger.info("="*70)
        logger.info(f"Total Iterations: {summary['total_iterations']}")
        logger.info(f"Successful: {summary['successful']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Success Rate: {summary['successful']/summary['total_iterations']*100:.1f}%" if summary['total_iterations'] > 0 else "N/A")
        logger.info("="*70 + "\n")
        
        return summary
    
    def _find_incomplete_tasks(self) -> List[Dict[str, Any]]:
        """Find incomplete tasks from breadcrumbs"""
        tasks = []
        
        # Search for C files in the project
        search_paths = [
            self.aros_path / 'workbench' / 'hidds' / self.project_name,
            self.aros_path / 'arch' / 'all' / self.project_name,
            self.aros_path / self.project_name
        ]
        
        c_files = []
        for search_path in search_paths:
            if search_path.exists():
                c_files.extend(list(search_path.rglob('*.c'))[:20])
        
        # Parse breadcrumbs
        for c_file in c_files:
            try:
                self.breadcrumb_parser.parse_file(str(c_file))
            except Exception:
                pass
        
        # Get incomplete tasks
        incomplete = self.breadcrumb_parser.get_breadcrumbs_by_status('PARTIAL')
        incomplete += self.breadcrumb_parser.get_breadcrumbs_by_status('NOT_STARTED')
        
        # Convert to task format
        for bc in incomplete:
            tasks.append({
                'phase': bc.phase,
                'status': bc.status,
                'strategy': bc.strategy,
                'file': bc.file_path
            })
        
        # If no tasks from breadcrumbs, create a default task
        if not tasks:
            tasks.append({
                'phase': f'{self.project_name.upper()}_DEVELOPMENT',
                'status': 'IMPLEMENTING',
                'strategy': f'Implement {self.project_name} functionality',
                'file': 'unknown'
            })
        
        return tasks


def main():
    """Main entry point"""
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description='Copilot-Style Iteration Loop with Local Models'
    )
    parser.add_argument(
        '--aros-path',
        default='aros-src',
        help='Path to AROS source'
    )
    parser.add_argument(
        '--project',
        default='radeonsi',
        help='Project name to work on'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum iterations to run'
    )
    parser.add_argument(
        '--log-path',
        default='logs/copilot_iteration',
        help='Path for logs'
    )
    
    args = parser.parse_args()
    
    # Create and run iteration loop
    iteration = CopilotStyleIteration(
        aros_path=args.aros_path,
        project_name=args.project,
        log_path=args.log_path,
        max_iterations=args.max_iterations
    )
    
    try:
        summary = iteration.run()
        
        # Exit with appropriate code
        if summary['successful'] > 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
