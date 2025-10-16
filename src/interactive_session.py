"""
Interactive Session Manager
Manages Copilot-style interactive development sessions with exploration
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages interactive development sessions with exploration"""
    
    def __init__(
        self,
        model_loader,
        aros_path: str,
        log_path: str
    ):
        self.model_loader = model_loader
        self.aros_path = Path(aros_path)
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self.current_session = None
        self.session_history = []
        self.iteration_context = {}  # Track context across iterations
        
        # Load models
        self.codegen = None
        self.llm = None
        
    def start_session(
        self,
        task_description: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Start a new interactive session
        
        Args:
            task_description: Description of the task
            context: Context information
            
        Returns:
            Session ID
        """
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        self.current_session = {
            'id': session_id,
            'task': task_description,
            'context': context,
            'started_at': datetime.now().isoformat(),
            'turns': [],
            'exploration_results': [],
            'generated_code': [],
            'status': 'active'
        }
        
        logger.info(f"Started session {session_id}: {task_description}")
        
        return session_id
    
    def explore(
        self,
        query: str,
        max_files: int = 10
    ) -> Dict[str, Any]:
        """
        Explore the codebase to gather context
        
        Args:
            query: What to explore
            max_files: Maximum files to analyze
            
        Returns:
            Exploration results
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        logger.info(f"Exploring: {query}")
        
        # Ensure LLM is loaded
        if not self.llm:
            self.llm = self.model_loader.load_model('llm')
        
        # Find relevant files
        relevant_files = self._find_relevant_files(query, max_files)
        
        # Load file contents
        file_contents = []
        for file_path in relevant_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    file_contents.append({
                        'path': str(file_path.relative_to(self.aros_path)),
                        'content': content
                    })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        # Find relevant breadcrumbs
        breadcrumbs = self._find_relevant_breadcrumbs(query)
        
        # Use LLM to explore
        exploration = self.llm.explore_codebase(
            query=query,
            file_contents=file_contents,
            breadcrumbs=breadcrumbs
        )
        
        # Add to session
        exploration['timestamp'] = datetime.now().isoformat()
        self.current_session['exploration_results'].append(exploration)
        
        # Add turn to session
        self._add_turn('explore', query, exploration)
        
        return exploration
    
    def reason(
        self,
        specific_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reason about the current task
        
        Args:
            specific_question: Optional specific question to reason about
            
        Returns:
            Reasoning results
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        # Ensure LLM is loaded
        if not self.llm:
            self.llm = self.model_loader.load_model('llm')
        
        task = specific_question or self.current_session['task']
        
        # Gather previous attempts from session
        previous_attempts = []
        for turn in self.current_session['turns']:
            if turn['action'] == 'generate' and turn.get('result'):
                previous_attempts.append(turn['result'].get('summary', ''))
        
        # Reason about task
        reasoning = self.llm.reason_about_task(
            task_description=task,
            context=self.current_session['context'],
            previous_attempts=previous_attempts if previous_attempts else None
        )
        
        # Add turn to session
        self._add_turn('reason', task, reasoning)
        
        return reasoning
    
    def generate(
        self,
        prompt: Optional[str] = None,
        use_exploration: bool = True,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate code for the task
        
        Args:
            prompt: Optional custom prompt
            use_exploration: Use exploration results in generation
            stream: Whether to stream generation token by token
            
        Returns:
            Generation results
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        # Ensure codegen is loaded
        if not self.codegen:
            self.codegen = self.model_loader.load_model('codegen')
        
        # Build context from exploration if enabled
        context = self.current_session['context'].copy()
        
        if use_exploration and self.current_session['exploration_results']:
            # Use latest exploration insights
            latest_exploration = self.current_session['exploration_results'][-1]
            context['exploration_insights'] = latest_exploration.get('insights', '')
        
        # Add iteration context for continuity
        if self.iteration_context:
            context['previous_attempts'] = self.iteration_context.get('attempts', [])
            context['learned_patterns'] = self.iteration_context.get('patterns', [])
        
        # Generate code with breadcrumbs
        task_desc = prompt or self.current_session['task']
        
        # Get previous attempts for history
        breadcrumb_history = []
        for gen in self.current_session['generated_code']:
            if gen.get('error'):
                breadcrumb_history.append(f"Failed: {gen['error']}")
            else:
                breadcrumb_history.append("Generated successfully")
        
        generated_code = self.codegen.generate_with_breadcrumbs(
            task_description=task_desc,
            context=context,
            breadcrumb_history=breadcrumb_history if breadcrumb_history else None,
            stream=stream
        )
        
        generation_result = {
            'code': generated_code,
            'timestamp': datetime.now().isoformat(),
            'used_exploration': use_exploration,
            'iteration': len(self.current_session['generated_code']) + 1,
            'streamed': stream
        }
        
        self.current_session['generated_code'].append(generation_result)
        
        # Update iteration context
        self._update_iteration_context(generation_result)
        
        # Add turn to session
        self._add_turn('generate', task_desc, generation_result)
        
        return generation_result
    
    def _update_iteration_context(self, generation_result: Dict[str, Any]):
        """Update context that persists across iterations"""
        if 'attempts' not in self.iteration_context:
            self.iteration_context['attempts'] = []
        if 'patterns' not in self.iteration_context:
            self.iteration_context['patterns'] = []
        
        # Track this attempt
        attempt_summary = {
            'iteration': generation_result['iteration'],
            'timestamp': generation_result['timestamp'],
            'code_length': len(generation_result.get('code', '')),
            'success': not generation_result.get('error')
        }
        self.iteration_context['attempts'].append(attempt_summary)
        
        # Keep only last 5 attempts for context
        self.iteration_context['attempts'] = self.iteration_context['attempts'][-5:]
    
    def review(
        self,
        code: Optional[str] = None,
        errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Review generated code
        
        Args:
            code: Code to review (uses latest if not provided)
            errors: Any errors encountered
            
        Returns:
            Review results
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        # Ensure LLM is loaded
        if not self.llm:
            self.llm = self.model_loader.load_model('llm')
        
        # Use latest generated code if not provided
        if code is None:
            if not self.current_session['generated_code']:
                raise ValueError("No code to review")
            code = self.current_session['generated_code'][-1]['code']
        
        # Review code
        review = self.llm.review_code(
            code=code,
            requirements=self.current_session['task'],
            errors=errors
        )
        
        # Add turn to session
        self._add_turn('review', f"Review generated code", review)
        
        return review
    
    def iterate(
        self,
        feedback: str,
        errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Iterate on the solution based on feedback
        
        Args:
            feedback: Feedback on previous attempt
            errors: Compilation/runtime errors
            
        Returns:
            New generation results
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        logger.info(f"Iterating with feedback: {feedback[:100]}...")
        
        # Update context with feedback
        self.current_session['context']['feedback'] = feedback
        if errors:
            self.current_session['context']['errors'] = errors
        
        # Generate new version
        return self.generate(use_exploration=True)
    
    def end_session(
        self,
        status: str = 'completed',
        summary: Optional[str] = None
    ):
        """
        End the current session
        
        Args:
            status: Final status ('completed', 'failed', 'abandoned')
            summary: Optional summary
        """
        if not self.current_session:
            return
        
        self.current_session['status'] = status
        self.current_session['ended_at'] = datetime.now().isoformat()
        if summary:
            self.current_session['summary'] = summary
        
        # Save session
        self._save_session()
        
        # Add to history
        self.session_history.append(self.current_session)
        
        logger.info(f"Ended session {self.current_session['id']}: {status}")
        
        self.current_session = None
    
    def _add_turn(self, action: str, input_data: str, result: Any):
        """Add a turn to the current session"""
        turn = {
            'action': action,
            'input': input_data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        self.current_session['turns'].append(turn)
    
    def _find_relevant_files(
        self,
        query: str,
        max_files: int
    ) -> List[Path]:
        """Find relevant files based on query"""
        # Simple implementation: search for C files containing query keywords
        keywords = query.lower().split()
        relevant_files = []
        
        # Search in AROS source
        for c_file in self.aros_path.rglob('*.c'):
            if len(relevant_files) >= max_files:
                break
            
            # Check if any keyword is in the path
            path_str = str(c_file).lower()
            if any(keyword in path_str for keyword in keywords):
                relevant_files.append(c_file)
        
        # If not enough files found, add some random C files
        if len(relevant_files) < max_files // 2:
            for c_file in self.aros_path.rglob('*.c'):
                if c_file not in relevant_files:
                    relevant_files.append(c_file)
                    if len(relevant_files) >= max_files:
                        break
        
        return relevant_files[:max_files]
    
    def _find_relevant_breadcrumbs(self, query: str) -> List[Dict[str, Any]]:
        """Find relevant breadcrumbs based on query"""
        # This would integrate with the breadcrumb parser
        # For now, return empty list
        return []
    
    def _save_session(self):
        """Save session to disk"""
        if not self.current_session:
            return
        
        session_file = self.log_path / f"{self.current_session['id']}.json"
        
        try:
            with open(session_file, 'w') as f:
                json.dump(self.current_session, f, indent=2)
            logger.info(f"Saved session to {session_file}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.current_session:
            return {'status': 'no_active_session'}
        
        return {
            'id': self.current_session['id'],
            'task': self.current_session['task'],
            'status': self.current_session['status'],
            'turns': len(self.current_session['turns']),
            'explorations': len(self.current_session['exploration_results']),
            'generations': len(self.current_session['generated_code']),
            'started_at': self.current_session['started_at'],
            'iteration_context': self.iteration_context
        }
    
    def get_iteration_metrics(self) -> Dict[str, Any]:
        """Get metrics across iterations"""
        if not self.iteration_context.get('attempts'):
            return {'total_attempts': 0}
        
        attempts = self.iteration_context['attempts']
        successful = sum(1 for a in attempts if a.get('success', False))
        
        return {
            'total_attempts': len(attempts),
            'successful_attempts': successful,
            'success_rate': successful / len(attempts) if attempts else 0,
            'avg_code_length': sum(a.get('code_length', 0) for a in attempts) / len(attempts) if attempts else 0,
            'recent_attempts': attempts[-3:] if len(attempts) >= 3 else attempts
        }
    
    def save_checkpoint(self, checkpoint_name: Optional[str] = None) -> str:
        """
        Save a checkpoint of the current session
        
        Args:
            checkpoint_name: Optional name for the checkpoint
            
        Returns:
            Checkpoint file path
        """
        if not self.current_session:
            raise RuntimeError("No active session to checkpoint")
        
        if not checkpoint_name:
            checkpoint_name = f"checkpoint_{int(datetime.now().timestamp())}"
        
        checkpoint_data = {
            'session': self.current_session,
            'iteration_context': self.iteration_context,
            'checkpoint_name': checkpoint_name,
            'checkpoint_time': datetime.now().isoformat()
        }
        
        checkpoint_dir = self.log_path / 'checkpoints'
        checkpoint_dir.mkdir(exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"{checkpoint_name}.json"
        
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            logger.info(f"Saved checkpoint to {checkpoint_file}")
            return str(checkpoint_file)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            raise
    
    def load_checkpoint(self, checkpoint_path: str) -> bool:
        """
        Load a checkpoint and resume the session
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            True if checkpoint loaded successfully
        """
        try:
            with open(checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            self.current_session = checkpoint_data['session']
            self.iteration_context = checkpoint_data['iteration_context']
            
            logger.info(f"Loaded checkpoint: {checkpoint_data['checkpoint_name']}")
            logger.info(f"Session: {self.current_session['id']}")
            logger.info(f"Task: {self.current_session['task']}")
            logger.info(f"Turns: {len(self.current_session['turns'])}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List available checkpoints
        
        Returns:
            List of checkpoint information
        """
        checkpoint_dir = self.log_path / 'checkpoints'
        if not checkpoint_dir.exists():
            return []
        
        checkpoints = []
        for checkpoint_file in checkpoint_dir.glob('*.json'):
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                checkpoints.append({
                    'name': data.get('checkpoint_name', checkpoint_file.stem),
                    'path': str(checkpoint_file),
                    'time': data.get('checkpoint_time', 'unknown'),
                    'session_id': data.get('session', {}).get('id', 'unknown'),
                    'task': data.get('session', {}).get('task', 'unknown')
                })
            except Exception as e:
                logger.warning(f"Could not read checkpoint {checkpoint_file}: {e}")
        
        return sorted(checkpoints, key=lambda x: x['time'], reverse=True)
    
    def compare_checkpoints(self, checkpoint1_path: str, checkpoint2_path: str) -> Dict[str, Any]:
        """
        Compare two checkpoints and show differences
        
        Args:
            checkpoint1_path: Path to first checkpoint
            checkpoint2_path: Path to second checkpoint
            
        Returns:
            Dictionary with comparison results including:
            - added_keys: Keys added in checkpoint2
            - removed_keys: Keys removed from checkpoint1
            - changed_values: Values that changed between checkpoints
            - iteration_context_diff: Differences in iteration context
            - summary: Human-readable summary
        """
        try:
            with open(checkpoint1_path, 'r') as f:
                cp1 = json.load(f)
            with open(checkpoint2_path, 'r') as f:
                cp2 = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load checkpoints for comparison: {e}")
            return {'error': str(e)}
        
        diff = {
            'checkpoint1': checkpoint1_path,
            'checkpoint2': checkpoint2_path,
            'added_keys': [],
            'removed_keys': [],
            'changed_values': [],
            'iteration_context_diff': {},
            'summary': []
        }
        
        # Compare session data
        cp1_session = cp1.get('session', {})
        cp2_session = cp2.get('session', {})
        
        # Find added/removed keys
        cp1_keys = set(cp1_session.keys())
        cp2_keys = set(cp2_session.keys())
        
        diff['added_keys'] = list(cp2_keys - cp1_keys)
        diff['removed_keys'] = list(cp1_keys - cp2_keys)
        
        # Find changed values
        for key in cp1_keys & cp2_keys:
            if cp1_session[key] != cp2_session[key]:
                diff['changed_values'].append({
                    'key': key,
                    'old_value': cp1_session[key],
                    'new_value': cp2_session[key]
                })
        
        # Compare iteration contexts
        cp1_context = cp1.get('iteration_context', {})
        cp2_context = cp2.get('iteration_context', {})
        
        for key in set(list(cp1_context.keys()) + list(cp2_context.keys())):
            old_val = cp1_context.get(key)
            new_val = cp2_context.get(key)
            
            if old_val != new_val:
                diff['iteration_context_diff'][key] = {
                    'old': old_val,
                    'new': new_val
                }
        
        # Generate summary
        cp1_name = cp1.get('checkpoint_name', 'checkpoint1')
        cp2_name = cp2.get('checkpoint_name', 'checkpoint2')
        
        diff['summary'].append(f"Comparing {cp1_name} → {cp2_name}")
        
        if diff['added_keys']:
            diff['summary'].append(f"Added {len(diff['added_keys'])} keys: {', '.join(diff['added_keys'])}")
        
        if diff['removed_keys']:
            diff['summary'].append(f"Removed {len(diff['removed_keys'])} keys: {', '.join(diff['removed_keys'])}")
        
        if diff['changed_values']:
            diff['summary'].append(f"Changed {len(diff['changed_values'])} values")
            for change in diff['changed_values'][:3]:  # Show first 3
                diff['summary'].append(f"  - {change['key']}: {change['old_value']} → {change['new_value']}")
        
        if diff['iteration_context_diff']:
            diff['summary'].append(f"Iteration context changes: {len(diff['iteration_context_diff'])} items")
        
        if not any([diff['added_keys'], diff['removed_keys'], diff['changed_values'], diff['iteration_context_diff']]):
            diff['summary'].append("No differences found - checkpoints are identical")
        
        return diff
