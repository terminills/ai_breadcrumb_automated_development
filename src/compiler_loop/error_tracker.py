"""
Error Tracker
Tracks and analyzes compilation errors for AI learning
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ErrorTracker:
    """Tracks compilation errors and their resolutions"""
    
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self.error_database: Dict[str, Dict[str, Any]] = {}
        self.load_database()
    
    def load_database(self) -> None:
        """Load error database from disk"""
        db_file = self.log_path / 'error_database.json'
        
        if db_file.exists():
            try:
                with open(db_file, 'r') as f:
                    data = json.load(f)
                    # Ensure we have a dict
                    if isinstance(data, dict):
                        self.error_database = data
                    else:
                        self.error_database = {}
            except (json.JSONDecodeError, IOError):
                # If database is corrupted, start fresh
                self.error_database = {}
    
    def save_database(self) -> None:
        """Save error database to disk"""
        db_file = self.log_path / 'error_database.json'
        
        with open(db_file, 'w') as f:
            json.dump(self.error_database, f, indent=2)
    
    def track_error(self, error_message: str, context: Dict[str, Any]) -> str:
        """
        Track a compilation error
        Returns error hash for reference
        """
        # Generate hash for error
        error_hash = hashlib.sha256(error_message.encode()).hexdigest()[:16]
        
        if error_hash not in self.error_database:
            self.error_database[error_hash] = {
                'message': error_message,
                'first_seen': datetime.now().isoformat(),
                'occurrences': 0,
                'contexts': [],
                'resolutions': [],
                'status': 'unresolved'
            }
        
        self.error_database[error_hash]['occurrences'] += 1
        self.error_database[error_hash]['contexts'].append({
            'timestamp': datetime.now().isoformat(),
            **context
        })
        
        self.save_database()
        return error_hash
    
    def mark_resolved(self, error_hash: str, resolution: str, fix_commit: Optional[str] = None) -> None:
        """Mark an error as resolved"""
        if error_hash in self.error_database:
            self.error_database[error_hash]['status'] = 'resolved'
            self.error_database[error_hash]['resolutions'].append({
                'timestamp': datetime.now().isoformat(),
                'resolution': resolution,
                'fix_commit': fix_commit
            })
            self.save_database()
    
    def get_unresolved_errors(self) -> List[Dict[str, Any]]:
        """Get all unresolved errors"""
        # Ensure error_database is a dict
        if not isinstance(self.error_database, dict):
            return []
        
        return [
            {'hash': k, **v}
            for k, v in self.error_database.items()
            if isinstance(v, dict) and v.get('status') == 'unresolved'
        ]
    
    def get_error_patterns(self) -> Dict[str, int]:
        """Analyze error patterns"""
        patterns = {}
        
        # Ensure error_database is a dict
        if not isinstance(self.error_database, dict):
            return patterns
        
        for error_hash, error_data in self.error_database.items():
            if not isinstance(error_data, dict):
                continue
            
            message = error_data.get('message', '').lower()
            
            # Extract error type
            if 'undefined reference' in message:
                patterns['undefined_reference'] = patterns.get('undefined_reference', 0) + 1
            elif 'implicit declaration' in message:
                patterns['implicit_declaration'] = patterns.get('implicit_declaration', 0) + 1
            elif 'syntax error' in message:
                patterns['syntax_error'] = patterns.get('syntax_error', 0) + 1
            elif 'type mismatch' in message or 'incompatible' in message:
                patterns['type_error'] = patterns.get('type_error', 0) + 1
            else:
                patterns['other'] = patterns.get('other', 0) + 1
        
        return patterns
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get error tracking statistics"""
        # Ensure error_database is a dict
        if not isinstance(self.error_database, dict):
            self.error_database = {}
        
        total_errors = len(self.error_database)
        resolved = sum(1 for e in self.error_database.values() if isinstance(e, dict) and e.get('status') == 'resolved')
        total_occurrences = sum(e.get('occurrences', 0) for e in self.error_database.values() if isinstance(e, dict))
        
        return {
            'total_unique_errors': total_errors,
            'resolved_errors': resolved,
            'unresolved_errors': total_errors - resolved,
            'total_occurrences': total_occurrences,
            'patterns': self.get_error_patterns()
        }
