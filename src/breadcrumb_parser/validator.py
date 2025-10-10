"""
Breadcrumb Validator
Validates AI breadcrumb metadata for completeness and correctness
"""

from typing import List, Dict, Any
from .parser import Breadcrumb


class BreadcrumbValidator:
    """Validator for AI breadcrumb metadata"""
    
    REQUIRED_TAGS = ['AI_PHASE', 'AI_STATUS']
    
    VALID_STATUSES = [
        'NOT_STARTED', 'PARTIAL', 'IMPLEMENTED', 'FIXED', 'NEEDS_REFACTOR'
    ]
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def validate_breadcrumb(self, breadcrumb: Breadcrumb) -> bool:
        """Validate a single breadcrumb"""
        is_valid = True
        
        # Check required tags
        for tag in self.REQUIRED_TAGS:
            if not getattr(breadcrumb, tag.lower().replace('_', '_'), None):
                self.errors.append({
                    'file': breadcrumb.file_path,
                    'line': breadcrumb.line_number,
                    'error': f'Missing required tag: {tag}'
                })
                is_valid = False
        
        # Check valid status
        if breadcrumb.status and breadcrumb.status not in self.VALID_STATUSES:
            self.warnings.append({
                'file': breadcrumb.file_path,
                'line': breadcrumb.line_number,
                'warning': f'Invalid status: {breadcrumb.status}. Expected one of {self.VALID_STATUSES}'
            })
        
        # Check if error tags have corresponding fix reasons
        if (breadcrumb.compiler_err or breadcrumb.runtime_err) and not breadcrumb.fix_reason:
            self.warnings.append({
                'file': breadcrumb.file_path,
                'line': breadcrumb.line_number,
                'warning': 'Error tags present but no FIX_REASON provided'
            })
        
        # Validate JSON context if present
        if breadcrumb.ai_context:
            if not isinstance(breadcrumb.ai_context, dict):
                self.errors.append({
                    'file': breadcrumb.file_path,
                    'line': breadcrumb.line_number,
                    'error': 'AI_CONTEXT must be valid JSON'
                })
                is_valid = False
        
        return is_valid
    
    def validate_breadcrumbs(self, breadcrumbs: List[Breadcrumb]) -> bool:
        """Validate a list of breadcrumbs"""
        self.errors = []
        self.warnings = []
        
        all_valid = True
        for breadcrumb in breadcrumbs:
            if not self.validate_breadcrumb(breadcrumb):
                all_valid = False
        
        return all_valid
    
    def get_report(self) -> Dict[str, Any]:
        """Get validation report"""
        return {
            'valid': len(self.errors) == 0,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }
