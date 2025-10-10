"""
Compiler Loop Implementation
Executes the compile -> error -> learn feedback cycle
"""

import subprocess
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class CompilerLoop:
    """Manages the compilation and error feedback loop"""
    
    def __init__(self, aros_path: str, log_path: str):
        self.aros_path = Path(aros_path)
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self.compile_history: List[Dict[str, Any]] = []
        self.current_iteration = 0
    
    def compile_aros(self, target: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
        """
        Compile AROS or a specific target
        Returns compilation result with errors
        """
        self.current_iteration += 1
        start_time = time.time()
        
        compile_cmd = ['make']
        if target:
            compile_cmd.append(target)
        
        result = {
            'iteration': self.current_iteration,
            'timestamp': datetime.now().isoformat(),
            'target': target or 'all',
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': '',
            'errors': [],
            'warnings': []
        }
        
        try:
            # Run compilation
            process = subprocess.Popen(
                compile_cmd,
                cwd=self.aros_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                result['stdout'] = stdout
                result['stderr'] = stderr
                result['success'] = process.returncode == 0
            except subprocess.TimeoutExpired:
                process.kill()
                result['stderr'] = f'Compilation timeout after {timeout} seconds'
        
        except Exception as e:
            result['stderr'] = f'Compilation error: {str(e)}'
        
        result['duration'] = time.time() - start_time
        
        # Parse errors and warnings
        result['errors'] = self._parse_errors(result['stderr'])
        result['warnings'] = self._parse_warnings(result['stderr'])
        
        # Log the compilation
        self._log_compilation(result)
        self.compile_history.append(result)
        
        return result
    
    def _parse_errors(self, stderr: str) -> List[Dict[str, str]]:
        """Parse compiler errors from stderr"""
        errors = []
        
        for line in stderr.split('\n'):
            # Match common compiler error patterns
            if 'error:' in line.lower():
                errors.append({
                    'type': 'error',
                    'message': line.strip()
                })
        
        return errors
    
    def _parse_warnings(self, stderr: str) -> List[Dict[str, str]]:
        """Parse compiler warnings from stderr"""
        warnings = []
        
        for line in stderr.split('\n'):
            if 'warning:' in line.lower():
                warnings.append({
                    'type': 'warning',
                    'message': line.strip()
                })
        
        return warnings
    
    def _log_compilation(self, result: Dict[str, Any]) -> None:
        """Log compilation result to file"""
        log_file = self.log_path / f"compile_{result['iteration']}_{int(time.time())}.json"
        
        with open(log_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    def get_latest_errors(self) -> List[Dict[str, str]]:
        """Get errors from the most recent compilation"""
        if not self.compile_history:
            return []
        
        return self.compile_history[-1]['errors']
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of compilation errors across iterations"""
        total_errors = sum(len(c['errors']) for c in self.compile_history)
        total_warnings = sum(len(c['warnings']) for c in self.compile_history)
        successful = sum(1 for c in self.compile_history if c['success'])
        
        return {
            'total_iterations': len(self.compile_history),
            'successful_compiles': successful,
            'failed_compiles': len(self.compile_history) - successful,
            'total_errors': total_errors,
            'total_warnings': total_warnings
        }
