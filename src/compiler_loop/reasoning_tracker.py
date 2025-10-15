"""
AI Reasoning Tracker
Captures and logs AI thought processes, decision-making, and reasoning chains
for research, debugging, and system improvement
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ReasoningEntry:
    """Represents a single AI reasoning/thinking event"""
    timestamp: str
    task_id: str
    phase: str  # 'analyzing', 'deciding', 'implementing', 'evaluating'
    
    # Context
    breadcrumbs_consulted: List[str]
    error_context: Optional[str]
    files_considered: List[str]
    
    # Reasoning chain
    reasoning_steps: List[str]
    patterns_identified: List[str]
    
    # Decision
    decision_type: str
    approach_chosen: str
    confidence: float  # 0.0 to 1.0
    estimated_complexity: str  # 'LOW', 'MEDIUM', 'HIGH'
    
    # Outcome (filled in later)
    success: Optional[bool] = None
    iterations_taken: Optional[int] = None
    completion_time: Optional[str] = None
    
    # Raw data
    raw_thought_process: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class ReasoningTracker:
    """Tracks and logs AI reasoning processes"""
    
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self.reasoning_database: Dict[str, ReasoningEntry] = {}
        self.current_reasoning: Optional[ReasoningEntry] = None
        
        # Statistics
        self.total_reasoning_events = 0
        self.successful_decisions = 0
        self.failed_decisions = 0
        
        # Load existing database
        self.load_database()
    
    def load_database(self) -> None:
        """Load reasoning database from disk"""
        db_file = self.log_path / 'reasoning_database.json'
        
        if db_file.exists():
            try:
                with open(db_file, 'r') as f:
                    data = json.load(f)
                    self.total_reasoning_events = data.get('total_events', 0)
                    self.successful_decisions = data.get('successful', 0)
                    self.failed_decisions = data.get('failed', 0)
                    # Reasoning entries are stored in individual files
            except Exception as e:
                print(f"Warning: Could not load reasoning database: {e}")
    
    def save_database(self) -> None:
        """Save reasoning database metadata to disk"""
        db_file = self.log_path / 'reasoning_database.json'
        
        metadata = {
            'total_events': self.total_reasoning_events,
            'successful': self.successful_decisions,
            'failed': self.failed_decisions,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(db_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def start_reasoning(
        self,
        task_id: str,
        phase: str,
        breadcrumbs_consulted: List[str],
        error_context: Optional[str] = None,
        files_considered: Optional[List[str]] = None
    ) -> str:
        """
        Start capturing a new reasoning event
        Returns reasoning ID for reference
        """
        reasoning_id = f"{task_id}_{int(datetime.now().timestamp())}"
        
        self.current_reasoning = ReasoningEntry(
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            phase=phase,
            breadcrumbs_consulted=breadcrumbs_consulted or [],
            error_context=error_context,
            files_considered=files_considered or [],
            reasoning_steps=[],
            patterns_identified=[],
            decision_type='',
            approach_chosen='',
            confidence=0.0,
            estimated_complexity='MEDIUM'
        )
        
        self.reasoning_database[reasoning_id] = self.current_reasoning
        self.total_reasoning_events += 1
        
        return reasoning_id
    
    def add_reasoning_step(self, step: str) -> None:
        """Add a step to the current reasoning chain"""
        if self.current_reasoning:
            self.current_reasoning.reasoning_steps.append(step)
    
    def add_pattern(self, pattern: str) -> None:
        """Add an identified pattern to current reasoning"""
        if self.current_reasoning:
            self.current_reasoning.patterns_identified.append(pattern)
    
    def set_decision(
        self,
        decision_type: str,
        approach: str,
        confidence: float,
        complexity: str = 'MEDIUM',
        raw_thought: Optional[str] = None
    ) -> None:
        """Record the decision made"""
        if self.current_reasoning:
            self.current_reasoning.decision_type = decision_type
            self.current_reasoning.approach_chosen = approach
            self.current_reasoning.confidence = confidence
            self.current_reasoning.estimated_complexity = complexity
            self.current_reasoning.raw_thought_process = raw_thought
    
    def complete_reasoning(
        self,
        reasoning_id: str,
        success: bool,
        iterations: int = 1
    ) -> None:
        """Mark reasoning as complete with outcome"""
        if reasoning_id in self.reasoning_database:
            entry = self.reasoning_database[reasoning_id]
            entry.success = success
            entry.iterations_taken = iterations
            entry.completion_time = datetime.now().isoformat()
            
            if success:
                self.successful_decisions += 1
            else:
                self.failed_decisions += 1
            
            # Save to individual file
            self._save_reasoning_entry(reasoning_id, entry)
            self.save_database()
    
    def _save_reasoning_entry(self, reasoning_id: str, entry: ReasoningEntry) -> None:
        """Save individual reasoning entry to file"""
        entry_file = self.log_path / f"reasoning_{reasoning_id}.json"
        
        with open(entry_file, 'w') as f:
            json.dump(entry.to_dict(), f, indent=2)
    
    def get_current_reasoning(self) -> Optional[Dict[str, Any]]:
        """Get current reasoning in progress"""
        if self.current_reasoning:
            return self.current_reasoning.to_dict()
        return None
    
    def get_recent_reasoning(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent reasoning entries"""
        # Get recent reasoning files
        reasoning_files = sorted(
            self.log_path.glob('reasoning_*.json'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        entries = []
        for file in reasoning_files:
            try:
                with open(file, 'r') as f:
                    entries.append(json.load(f))
            except Exception as e:
                print(f"Warning: Could not load {file}: {e}")
        
        return entries
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics on pattern usage"""
        pattern_counts = {}
        pattern_success_rates = {}
        
        # Analyze all reasoning files
        for reasoning_file in self.log_path.glob('reasoning_*.json'):
            try:
                with open(reasoning_file, 'r') as f:
                    entry = json.load(f)
                    
                for pattern in entry.get('patterns_identified', []):
                    if pattern not in pattern_counts:
                        pattern_counts[pattern] = {'total': 0, 'successful': 0}
                    
                    pattern_counts[pattern]['total'] += 1
                    if entry.get('success'):
                        pattern_counts[pattern]['successful'] += 1
            except Exception:
                continue
        
        # Calculate success rates
        for pattern, counts in pattern_counts.items():
            if counts['total'] > 0:
                pattern_success_rates[pattern] = {
                    'uses': counts['total'],
                    'success_rate': counts['successful'] / counts['total']
                }
        
        return pattern_success_rates
    
    def get_breadcrumb_effectiveness(self) -> Dict[str, Any]:
        """Analyze breadcrumb effectiveness in decision making"""
        breadcrumb_stats = {}
        
        for reasoning_file in self.log_path.glob('reasoning_*.json'):
            try:
                with open(reasoning_file, 'r') as f:
                    entry = json.load(f)
                    
                for breadcrumb in entry.get('breadcrumbs_consulted', []):
                    if breadcrumb not in breadcrumb_stats:
                        breadcrumb_stats[breadcrumb] = {'uses': 0, 'successful': 0}
                    
                    breadcrumb_stats[breadcrumb]['uses'] += 1
                    if entry.get('success'):
                        breadcrumb_stats[breadcrumb]['successful'] += 1
            except Exception:
                continue
        
        # Calculate effectiveness
        effectiveness = {}
        for bc, stats in breadcrumb_stats.items():
            if stats['uses'] > 0:
                effectiveness[bc] = {
                    'uses': stats['uses'],
                    'success_rate': stats['successful'] / stats['uses']
                }
        
        return effectiveness
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive reasoning statistics"""
        return {
            'total_reasoning_events': self.total_reasoning_events,
            'successful_decisions': self.successful_decisions,
            'failed_decisions': self.failed_decisions,
            'success_rate': (
                self.successful_decisions / self.total_reasoning_events 
                if self.total_reasoning_events > 0 else 0.0
            ),
            'pattern_usage': self.get_pattern_statistics(),
            'breadcrumb_effectiveness': self.get_breadcrumb_effectiveness()
        }
    
    def query_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        """Query reasoning entries by phase"""
        results = []
        
        for reasoning_file in self.log_path.glob('reasoning_*.json'):
            try:
                with open(reasoning_file, 'r') as f:
                    entry = json.load(f)
                    if entry.get('phase') == phase:
                        results.append(entry)
            except Exception:
                continue
        
        return results
    
    def query_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Query reasoning entries that used a specific pattern"""
        results = []
        
        for reasoning_file in self.log_path.glob('reasoning_*.json'):
            try:
                with open(reasoning_file, 'r') as f:
                    entry = json.load(f)
                    if pattern in entry.get('patterns_identified', []):
                        results.append(entry)
            except Exception:
                continue
        
        return results
    
    def get_failed_reasoning_patterns(self) -> List[Dict[str, Any]]:
        """Get reasoning chains that led to failures for analysis"""
        failed = []
        
        for reasoning_file in self.log_path.glob('reasoning_*.json'):
            try:
                with open(reasoning_file, 'r') as f:
                    entry = json.load(f)
                    if entry.get('success') is False:
                        failed.append(entry)
            except Exception:
                continue
        
        return failed
