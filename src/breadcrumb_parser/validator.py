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
    
    VALID_COMPLEXITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def validate_breadcrumb(self, breadcrumb: Breadcrumb) -> bool:
        """Validate a single breadcrumb"""
        is_valid = True
        
        # Check required tags
        # Map tag names to attribute names
        tag_to_attr = {
            'AI_PHASE': 'phase',
            'AI_STATUS': 'status'
        }
        
        for tag in self.REQUIRED_TAGS:
            attr_name = tag_to_attr.get(tag, tag.lower())
            if not getattr(breadcrumb, attr_name, None):
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
        
        # Validate distributed AI fields
        if breadcrumb.ai_complexity:
            if breadcrumb.ai_complexity not in self.VALID_COMPLEXITIES:
                self.warnings.append({
                    'file': breadcrumb.file_path,
                    'line': breadcrumb.line_number,
                    'warning': f'Invalid complexity: {breadcrumb.ai_complexity}. Expected one of {self.VALID_COMPLEXITIES}'
                })
        
        if breadcrumb.ai_priority:
            try:
                priority = int(breadcrumb.ai_priority)
                if not 1 <= priority <= 10:
                    self.warnings.append({
                        'file': breadcrumb.file_path,
                        'line': breadcrumb.line_number,
                        'warning': f'Priority should be between 1-10, got {priority}'
                    })
            except ValueError:
                self.warnings.append({
                    'file': breadcrumb.file_path,
                    'line': breadcrumb.line_number,
                    'warning': f'Priority must be a number, got {breadcrumb.ai_priority}'
                })
        
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
