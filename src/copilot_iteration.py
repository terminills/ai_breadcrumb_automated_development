"""
Copilot-Style Iteration Loop
Interactive development loop with exploration, reasoning, and local models
"""

import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.local_models import LocalModelLoader
from src.interactive_session import SessionManager
from src.breadcrumb_parser import BreadcrumbParser
from src.compiler_loop import CompilerLoop, ErrorTracker, ReasoningTracker
from src.iteration_analytics import IterationAnalytics

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
        max_iterations: int = 10,
        max_retries: int = 3,
        adaptive_retries: bool = True
    ):
        self.aros_path = Path(aros_path)
        self.project_name = project_name
        self.log_path = Path(log_path)
        self.max_iterations = max_iterations
        self.max_retries = max_retries
        self.adaptive_retries = adaptive_retries
        
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        # State file for UI
        self.state_file = self.log_path / 'iteration_state.json'
        self.history_file = self.log_path / 'iteration_history.json'
        
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
        self.retry_count = 0
        self.iteration_history = []  # Track history across iterations
        self.learned_patterns = {}  # Track learned patterns
        
        # Current state for UI
        self.current_state = {
            'current_iteration': 0,
            'total_iterations': max_iterations,
            'current_phase': 'none',
            'phase_progress': {},
            'session_id': None,
            'task_description': '',
            'retry_count': 0,
            'last_update': datetime.now().isoformat()
        }
    
    def run_interactive_iteration(
        self,
        task: Dict[str, Any],
        enable_exploration: bool = True,
        retry_on_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Run one interactive iteration with exploration
        
        Args:
            task: Task information from breadcrumb
            enable_exploration: Enable exploration phase
            retry_on_failure: Retry on compilation/review failures
            
        Returns:
            Iteration results
        """
        self.current_iteration += 1
        iteration_start_time = datetime.now()
        self.retry_count = 0
        
        # Update state for UI
        self.current_state.update({
            'current_iteration': self.current_iteration,
            'total_iterations': self.max_iterations,
            'task_description': task.get('strategy', task.get('phase', 'unknown')),
            'current_phase': 'starting',
            'retry_count': 0,
            'last_update': datetime.now().isoformat()
        })
        self._save_state()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Iteration {self.current_iteration}/{self.max_iterations}")
        logger.info(f"Task: {task.get('phase', 'unknown')}")
        logger.info(f"{'='*60}\n")
        
        # Determine max retries (adaptive or fixed)
        effective_max_retries = self.max_retries
        result = None
        
        while self.retry_count <= effective_max_retries:
            try:
                result = self._execute_iteration(
                    task, 
                    enable_exploration, 
                    iteration_start_time
                )
                
                # On first failure with adaptive retries, recalculate retry limit
                if not result['success'] and self.retry_count == 0 and self.adaptive_retries:
                    errors = result.get('compilation', {}).get('errors', [])
                    effective_max_retries = self._calculate_adaptive_retries(errors)
                    logger.info(f"Adjusted max retries to {effective_max_retries} based on error complexity")
                
                # If successful or max retries reached, return
                if result['success'] or not retry_on_failure or self.retry_count >= effective_max_retries:
                    break
                
                # Otherwise, retry
                self.retry_count += 1
                logger.info(f"\n⚠ Iteration failed, retrying ({self.retry_count}/{effective_max_retries})...")
                
                # Add retry context to session
                if self.session_manager.current_session:
                    retry_context = {
                        'retry_count': self.retry_count,
                        'previous_errors': result.get('compilation', {}).get('errors', []),
                        'previous_review': result.get('review', {}).get('review', '')
                    }
                    self.session_manager.current_session['context'].update(retry_context)
                
            except Exception as e:
                logger.error(f"Error in iteration: {e}")
                if self.session_manager.current_session:
                    self.session_manager.end_session(status='failed', summary=str(e))
                raise
        
        # Track iteration history and learn patterns
        if result:
            self._track_iteration_history(result)
            self._learn_pattern(result)
            self._add_to_history(result)  # Add to history file for UI
            
            # Save state periodically
            if self.current_iteration % 5 == 0:
                self.save_iteration_state()
        
        # Max retries reached
        if self.retry_count >= effective_max_retries and not result['success']:
            logger.warning(f"\n⚠ Max retries ({effective_max_retries}) reached")
        
        # Mark iteration as complete in state
        self.current_state['current_phase'] = 'complete'
        self._save_state()
        
        return result
    
    def _execute_iteration(
        self,
        task: Dict[str, Any],
        enable_exploration: bool,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Execute a single iteration attempt"""
        
        # Start session on first attempt
        if self.retry_count == 0:
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
        
        # Phase 1: Exploration (like Copilot gathering context)
        if enable_exploration and self.retry_count == 0:  # Only explore on first attempt
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
        
        # End session on success or final retry
        if success or self.retry_count >= self.max_retries:
            status = 'completed' if success else 'needs_iteration'
            if self.session_manager.current_session:
                self.session_manager.end_session(
                    status=status,
                    summary=f"Iteration {self.current_iteration} {status} (retries: {self.retry_count})"
                )
            
            if success:
                self.successful_iterations += 1
        
        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Log performance metrics
        logger.info(f"\n--- Performance Metrics ---")
        logger.info(f"Total iteration time: {total_time:.2f}s")
        logger.info(f"Retry count: {self.retry_count}/{self.max_retries}")
        for phase, timing in phase_timings.items():
            logger.info(f"{phase.capitalize()}: {timing:.2f}s ({timing/total_time*100:.1f}%)")
        
        return {
            'iteration': self.current_iteration,
            'session_id': self.session_manager.current_session['id'] if self.session_manager.current_session else None,
            'success': success,
            'generation': generation_result,
            'review': review_result,
            'compilation': compile_result,
            'timings': phase_timings,
            'total_time': total_time,
            'retry_count': self.retry_count
        }
    
    def _exploration_phase(self, task: Dict[str, Any]):
        """Phase 1: Explore codebase like Copilot gathering context"""
        logger.info("\n--- Phase 1: Exploration ---")
        
        # Update state
        self.current_state['current_phase'] = 'exploration'
        self.current_state['phase_progress']['exploration'] = 'running'
        self._save_state()
        
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
            
            # Update state with exploration results
            self.current_state['exploration'] = {
                'files_analyzed': exploration['files_analyzed'],
                'breadcrumbs_analyzed': exploration['breadcrumbs_analyzed'],
                'insights': exploration['insights'][:500]  # Truncate for UI
            }
            self.current_state['phase_progress']['exploration'] = 'completed'
            self._save_state()
            
        except Exception as e:
            logger.warning(f"Exploration failed: {e}")
            logger.info("Continuing without exploration insights...")
            self.reasoning_tracker.add_reasoning_step(f"Exploration failed: {e}")
            self.current_state['phase_progress']['exploration'] = 'failed'
            self._save_state()
    
    def _reasoning_phase(self):
        """Phase 2: Reason about the task like Copilot analyzing"""
        logger.info("\n--- Phase 2: Reasoning ---")
        
        # Update state
        self.current_state['current_phase'] = 'reasoning'
        self.current_state['phase_progress']['reasoning'] = 'running'
        self._save_state()
        
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
            
            # Update state
            self.current_state['reasoning'] = {
                'strategy': reasoning['reasoning'][:500]
            }
            self.current_state['phase_progress']['reasoning'] = 'completed'
            self._save_state()
            
        except Exception as e:
            logger.warning(f"Reasoning failed: {e}")
            logger.info("Continuing with default strategy...")
            self.reasoning_tracker.add_reasoning_step(f"Reasoning failed: {e}")
            self.current_state['phase_progress']['reasoning'] = 'failed'
            self._save_state()
    
    def _generation_phase(self) -> Dict[str, Any]:
        """Phase 3: Generate code like Copilot suggesting"""
        logger.info("\n--- Phase 3: Code Generation ---")
        
        # Update state
        self.current_state['current_phase'] = 'generation'
        self.current_state['phase_progress']['generation'] = 'running'
        self._save_state()
        
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
            
            # Update state
            self.current_state['generation'] = {
                'code': generation['code'][:1000],  # Truncate for UI
                'status': 'completed',
                'length': len(generation['code'])
            }
            self.current_state['phase_progress']['generation'] = 'completed'
            self._save_state()
            
            return generation
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            self.reasoning_tracker.add_reasoning_step(f"Generation failed: {e}")
            self.current_state['phase_progress']['generation'] = 'failed'
            self._save_state()
            return {
                'code': '',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _review_phase(self, generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Review generated code"""
        logger.info("\n--- Phase 4: Code Review ---")
        
        # Update state
        self.current_state['current_phase'] = 'review'
        self.current_state['phase_progress']['review'] = 'running'
        self._save_state()
        
        if not generation_result.get('code'):
            logger.warning("No code to review")
            self.current_state['phase_progress']['review'] = 'skipped'
            self._save_state()
            return {'review': 'No code generated', 'has_errors': True}
        
        try:
            review = self.session_manager.review(
                code=generation_result['code']
            )
            
            logger.info("Code review completed")
            logger.info(f"Review preview: {review['review'][:200]}...")
            
            # Update state
            self.current_state['review'] = {
                'review': review['review'][:500],
                'status': 'completed',
                'has_errors': review.get('has_errors', False)
            }
            self.current_state['phase_progress']['review'] = 'completed'
            self._save_state()
            
            return review
            
        except Exception as e:
            logger.warning(f"Review failed: {e}")
            self.current_state['phase_progress']['review'] = 'failed'
            self._save_state()
            return {
                'review': f'Review failed: {e}',
                'has_errors': True
            }
    
    def _compilation_phase(self, generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: Compile and test the generated code"""
        logger.info("\n--- Phase 5: Compilation & Testing ---")
        
        # Update state
        self.current_state['current_phase'] = 'compilation'
        self.current_state['phase_progress']['compilation'] = 'running'
        self._save_state()
        
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
        
        # Update state
        self.current_state['compilation'] = {
            'success': success,
            'errors': compile_result['errors'],
            'warnings': compile_result['warnings']
        }
        self.current_state['phase_progress']['compilation'] = 'completed' if success else 'failed'
        self._save_state()
        
        return compile_result
    
    def _learning_phase(
        self,
        compile_result: Dict[str, Any],
        review_result: Dict[str, Any]
    ) -> bool:
        """Phase 6: Learn from compilation and review results"""
        logger.info("\n--- Phase 6: Learning ---")
        
        # Update state
        self.current_state['current_phase'] = 'learning'
        self.current_state['phase_progress']['learning'] = 'running'
        self._save_state()
        
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
            self.current_state['phase_progress']['learning'] = 'completed'
            self._save_state()
            return True
        
        # Track errors and get suggestions
        if compile_result.get('errors'):
            for error in compile_result['errors']:
                error_hash = self.error_tracker.track_error(
                    error_message=error,
                    context={
                        'iteration': self.current_iteration,
                        'project': self.project_name,
                        'reasoning_id': self.current_reasoning_id,
                        'retry_count': self.retry_count
                    }
                )
                logger.info(f"Tracked error: {error_hash[:8]}")
                
                # Get resolution suggestions from similar errors
                suggestions = self.error_tracker.get_resolution_suggestions(error)
                if suggestions:
                    logger.info(f"Found {len(suggestions)} resolution suggestions:")
                    for idx, suggestion in enumerate(suggestions[:3], 1):
                        logger.info(f"  {idx}. {suggestion[:100]}")
                    
                    # Add suggestions to session context for next retry
                    if self.session_manager.current_session:
                        if 'error_suggestions' not in self.session_manager.current_session['context']:
                            self.session_manager.current_session['context']['error_suggestions'] = []
                        self.session_manager.current_session['context']['error_suggestions'].extend(suggestions[:3])
                
                # Add to reasoning
                if self.current_reasoning_id:
                    self.reasoning_tracker.add_reasoning_step(
                        f"Encountered error: {error[:100]}"
                    )
                    if suggestions:
                        self.reasoning_tracker.add_reasoning_step(
                            f"Found {len(suggestions)} resolution suggestions from similar errors"
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


    def _calculate_adaptive_retries(self, errors: List[str]) -> int:
        """
        Calculate adaptive retry count based on error complexity
        
        Args:
            errors: List of error messages
            
        Returns:
            Adaptive retry count
        """
        if not self.adaptive_retries or not errors:
            return self.max_retries
        
        # Analyze error complexity
        complexity_score = 0
        
        for error in errors:
            error_lower = error.lower()
            
            # Simple errors (syntax, typos) - low complexity
            if any(keyword in error_lower for keyword in ['syntax error', 'unexpected token', 'missing semicolon']):
                complexity_score += 1
            
            # Medium complexity errors
            elif any(keyword in error_lower for keyword in ['undefined reference', 'type mismatch', 'incompatible']):
                complexity_score += 2
            
            # Complex errors (logic, architecture)
            elif any(keyword in error_lower for keyword in ['segmentation fault', 'assertion failed', 'deadlock']):
                complexity_score += 3
            
            # Very complex errors
            else:
                complexity_score += 2
        
        # Calculate adaptive retry count
        # Low complexity (score 1-3): fewer retries
        # Medium complexity (score 4-6): default retries
        # High complexity (score 7+): more retries
        
        if complexity_score <= 3:
            adaptive_retries = max(1, self.max_retries - 1)
        elif complexity_score <= 6:
            adaptive_retries = self.max_retries
        else:
            adaptive_retries = min(self.max_retries + 2, 8)  # Cap at 8 retries
        
        logger.info(f"Adaptive retries: {adaptive_retries} (complexity score: {complexity_score})")
        
        return adaptive_retries
    
    def _track_iteration_history(self, result: Dict[str, Any]):
        """
        Track iteration history for learning and analysis
        
        Args:
            result: Iteration result
        """
        history_entry = {
            'iteration': self.current_iteration,
            'timestamp': datetime.now().isoformat(),
            'success': result['success'],
            'retry_count': result['retry_count'],
            'total_time': result['total_time'],
            'phase_timings': result['timings'],
            'errors': result.get('compilation', {}).get('errors', [])
        }
        
        self.iteration_history.append(history_entry)
        
        # Keep only last 20 iterations in memory
        if len(self.iteration_history) > 20:
            self.iteration_history = self.iteration_history[-20:]
        
        # Save to disk
        history_file = self.log_path / 'iteration_history.json'
        try:
            with open(history_file, 'w') as f:
                json.dump(self.iteration_history, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save iteration history: {e}")
    
    def _learn_pattern(self, result: Dict[str, Any]):
        """
        Learn patterns from successful iterations
        
        Args:
            result: Iteration result
        """
        if not result['success']:
            return
        
        # Extract pattern information
        phase = result.get('generation', {}).get('context', {}).get('phase', 'unknown')
        
        if phase not in self.learned_patterns:
            self.learned_patterns[phase] = {
                'successes': 0,
                'total_attempts': 0,
                'avg_retries': 0,
                'avg_time': 0,
                'common_approaches': []
            }
        
        pattern = self.learned_patterns[phase]
        pattern['successes'] += 1
        pattern['total_attempts'] += 1
        pattern['avg_retries'] = (pattern['avg_retries'] * (pattern['total_attempts'] - 1) + result['retry_count']) / pattern['total_attempts']
        pattern['avg_time'] = (pattern['avg_time'] * (pattern['total_attempts'] - 1) + result['total_time']) / pattern['total_attempts']
        
        logger.info(f"Learned pattern for {phase}: {pattern['successes']}/{pattern['total_attempts']} success rate")
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """
        Get learned patterns summary
        
        Returns:
            Dictionary of learned patterns
        """
        return {
            'patterns': self.learned_patterns,
            'total_iterations': len(self.iteration_history),
            'overall_success_rate': sum(1 for h in self.iteration_history if h['success']) / len(self.iteration_history) if self.iteration_history else 0
        }
    
    def get_pattern_recommendation(self, phase: str, complexity: str = 'MEDIUM') -> Dict[str, Any]:
        """
        Get recommendations based on learned patterns for a specific phase
        
        Args:
            phase: The phase/task type to get recommendations for
            complexity: Estimated task complexity (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            Dictionary with recommendations including:
            - suggested_retries: Recommended retry count
            - estimated_time: Estimated completion time
            - success_probability: Estimated success probability
            - similar_tasks: List of similar completed tasks
            - best_practices: Recommendations based on history
        """
        recommendation = {
            'phase': phase,
            'complexity': complexity,
            'suggested_retries': self.max_retries,
            'estimated_time': 60.0,
            'success_probability': 0.5,
            'similar_tasks': [],
            'best_practices': []
        }
        
        # Check if we have learned patterns for this phase
        if phase in self.learned_patterns:
            pattern = self.learned_patterns[phase]
            
            # Calculate success probability
            if pattern['total_attempts'] > 0:
                recommendation['success_probability'] = pattern['successes'] / pattern['total_attempts']
            
            # Suggest retry count based on historical average
            if pattern['avg_retries'] > 0:
                # Adjust based on complexity
                complexity_multiplier = {
                    'LOW': 0.7,
                    'MEDIUM': 1.0,
                    'HIGH': 1.3,
                    'CRITICAL': 1.5
                }.get(complexity, 1.0)
                
                recommended_retries = int(pattern['avg_retries'] * complexity_multiplier)
                recommendation['suggested_retries'] = max(1, min(recommended_retries, 8))
            
            # Estimate time based on historical average
            if pattern['avg_time'] > 0:
                complexity_multiplier = {
                    'LOW': 0.8,
                    'MEDIUM': 1.0,
                    'HIGH': 1.4,
                    'CRITICAL': 2.0
                }.get(complexity, 1.0)
                
                recommendation['estimated_time'] = pattern['avg_time'] * complexity_multiplier
            
            # Add best practices based on success rate
            if recommendation['success_probability'] >= 0.8:
                recommendation['best_practices'].append(
                    f"High success rate ({recommendation['success_probability']*100:.0f}%) for this phase. "
                    f"Average completion time is {pattern['avg_time']:.1f}s."
                )
            elif recommendation['success_probability'] >= 0.5:
                recommendation['best_practices'].append(
                    f"Moderate success rate ({recommendation['success_probability']*100:.0f}%). "
                    f"Consider using {recommendation['suggested_retries']} retries for better outcomes."
                )
            else:
                recommendation['best_practices'].append(
                    f"Low success rate ({recommendation['success_probability']*100:.0f}%) for this phase. "
                    f"Review approach carefully and consider increasing exploration depth."
                )
        else:
            # No pattern data available - use defaults with warnings
            recommendation['best_practices'].append(
                f"No historical data for {phase}. Using default settings."
            )
            recommendation['best_practices'].append(
                "Consider starting with thorough exploration to establish patterns."
            )
        
        # Find similar tasks from history
        similar_tasks = [
            {
                'iteration': h['iteration'],
                'success': h['success'],
                'retry_count': h['retry_count'],
                'time': h['total_time'],
                'phase': h.get('phase', 'unknown')
            }
            for h in self.iteration_history
            if h.get('phase') == phase
        ]
        
        recommendation['similar_tasks'] = similar_tasks[-5:]  # Last 5 similar tasks
        
        # Add recommendations based on recent trends
        if len(similar_tasks) >= 3:
            recent_success_rate = sum(1 for t in similar_tasks[-3:] if t['success']) / 3
            if recent_success_rate > recommendation['success_probability']:
                recommendation['best_practices'].append(
                    "Recent trend shows improving success rate. Current approach is working well."
                )
            elif recent_success_rate < recommendation['success_probability']:
                recommendation['best_practices'].append(
                    "Recent trend shows declining success rate. Consider reviewing approach."
                )
        
        return recommendation
    
    def save_iteration_state(self) -> str:
        """
        Save the current iteration state for recovery
        
        Returns:
            Path to saved state file
        """
        state = {
            'current_iteration': self.current_iteration,
            'successful_iterations': self.successful_iterations,
            'iteration_history': self.iteration_history,
            'learned_patterns': self.learned_patterns,
            'project_name': self.project_name,
            'timestamp': datetime.now().isoformat()
        }
        
        state_file = self.log_path / 'iteration_state.json'
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Saved iteration state to {state_file}")
            return str(state_file)
        except Exception as e:
            logger.error(f"Failed to save iteration state: {e}")
            raise
    
    def load_iteration_state(self, state_file: Optional[str] = None) -> bool:
        """
        Load iteration state for recovery
        
        Args:
            state_file: Optional path to state file (uses default if not provided)
            
        Returns:
            True if state loaded successfully
        """
        if not state_file:
            state_file = self.log_path / 'iteration_state.json'
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            self.current_iteration = state['current_iteration']
            self.successful_iterations = state['successful_iterations']
            self.iteration_history = state['iteration_history']
            self.learned_patterns = state['learned_patterns']
            
            logger.info(f"Loaded iteration state from {state_file}")
            logger.info(f"Resuming at iteration {self.current_iteration}")
            logger.info(f"Learned patterns: {len(self.learned_patterns)}")
            
            return True
        except Exception as e:
            logger.warning(f"Could not load iteration state: {e}")
            return False
    
    def export_learned_patterns(self, export_path: Optional[str] = None) -> str:
        """
        Export learned patterns to a file for sharing between projects
        
        Args:
            export_path: Optional path to export file (uses default if not provided)
            
        Returns:
            Path to exported patterns file
        """
        if not export_path:
            export_path = self.log_path / 'learned_patterns_export.json'
        
        export_data = {
            'project_name': self.project_name,
            'export_time': datetime.now().isoformat(),
            'learned_patterns': self.learned_patterns,
            'total_iterations': len(self.iteration_history),
            'overall_success_rate': sum(1 for h in self.iteration_history if h['success']) / len(self.iteration_history) if self.iteration_history else 0,
            'metadata': {
                'version': '1.0',
                'format': 'copilot_iteration_patterns'
            }
        }
        
        try:
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            logger.info(f"Exported learned patterns to {export_path}")
            return str(export_path)
        except Exception as e:
            logger.error(f"Failed to export patterns: {e}")
            raise
    
    def import_learned_patterns(self, import_path: str, merge: bool = True) -> bool:
        """
        Import learned patterns from another project
        
        Args:
            import_path: Path to patterns export file
            merge: If True, merge with existing patterns; if False, replace them
            
        Returns:
            True if patterns imported successfully
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            # Validate format
            if import_data.get('metadata', {}).get('format') != 'copilot_iteration_patterns':
                logger.warning(f"Import file may not be in correct format")
            
            imported_patterns = import_data.get('learned_patterns', {})
            
            if merge:
                # Merge patterns - average the values for existing patterns
                for phase, pattern in imported_patterns.items():
                    if phase in self.learned_patterns:
                        # Merge existing pattern
                        existing = self.learned_patterns[phase]
                        
                        # Calculate weighted average based on total attempts
                        total_attempts = existing['total_attempts'] + pattern['total_attempts']
                        
                        merged = {
                            'successes': existing['successes'] + pattern['successes'],
                            'total_attempts': total_attempts,
                            'avg_retries': (
                                existing['avg_retries'] * existing['total_attempts'] +
                                pattern['avg_retries'] * pattern['total_attempts']
                            ) / total_attempts,
                            'avg_time': (
                                existing['avg_time'] * existing['total_attempts'] +
                                pattern['avg_time'] * pattern['total_attempts']
                            ) / total_attempts,
                            'common_approaches': list(set(
                                existing.get('common_approaches', []) +
                                pattern.get('common_approaches', [])
                            ))
                        }
                        
                        self.learned_patterns[phase] = merged
                        logger.info(f"Merged pattern for {phase}")
                    else:
                        # Add new pattern
                        self.learned_patterns[phase] = pattern
                        logger.info(f"Added new pattern for {phase}")
            else:
                # Replace all patterns
                self.learned_patterns = imported_patterns
                logger.info(f"Replaced all patterns with imported data")
            
            # Save updated patterns
            self.save_iteration_state()
            
            logger.info(f"Successfully imported patterns from {import_path}")
            logger.info(f"Imported patterns for {len(imported_patterns)} phases")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to import patterns: {e}")
            return False
    
    def _save_state(self):
        """Save current iteration state to file for UI"""
        try:
            self.current_state['last_update'] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.current_state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _add_to_history(self, iteration_result: Dict[str, Any]):
        """Add iteration result to history file"""
        try:
            # Load existing history
            history = []
            if self.history_file.exists():
                with open(self.history_file) as f:
                    history = json.load(f)
            
            # Add new iteration
            history.append({
                'iteration': iteration_result.get('iteration'),
                'success': iteration_result.get('success'),
                'timestamp': datetime.now().isoformat(),
                'timings': iteration_result.get('timings', {}),
                'retry_count': iteration_result.get('retry_count', 0)
            })
            
            # Keep last 100 iterations
            if len(history) > 100:
                history = history[-100:]
            
            # Save back
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to add to history: {e}")
    
    def get_analytics(self) -> IterationAnalytics:
        """
        Get analytics engine for detailed performance analysis
        
        Returns:
            IterationAnalytics instance with current data
        """
        return IterationAnalytics(self.iteration_history, self.learned_patterns)
    
    def generate_analytics_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate comprehensive analytics report
        
        Args:
            output_path: Optional path to save report
            
        Returns:
            Report as formatted string
        """
        analytics = self.get_analytics()
        return analytics.generate_report(output_path)


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
