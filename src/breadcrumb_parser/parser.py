"""
Breadcrumb Parser
Extracts AI breadcrumb metadata from source files
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class Breadcrumb:
    """Represents a single AI breadcrumb metadata block"""
    file_path: str
    line_number: int
    phase: Optional[str] = None
    status: Optional[str] = None
    pattern: Optional[str] = None
    strategy: Optional[str] = None
    details: Optional[str] = None
    compiler_err: Optional[str] = None
    runtime_err: Optional[str] = None
    fix_reason: Optional[str] = None
    ai_note: Optional[str] = None
    ai_history: Optional[str] = None
    ai_change: Optional[str] = None
    ai_version: Optional[str] = None
    ai_train_hash: Optional[str] = None
    linux_ref: Optional[str] = None
    amigaos_ref: Optional[str] = None
    aros_impl: Optional[str] = None
    ref_github_issue: Optional[str] = None
    ref_pr: Optional[str] = None
    ai_context: Optional[Dict[str, Any]] = None
    raw_tags: Dict[str, str] = field(default_factory=dict)


class BreadcrumbParser:
    """Parser for AI breadcrumb metadata in source files"""
    
    BREADCRUMB_TAGS = [
        'AI_PHASE', 'AI_STATUS', 'AI_PATTERN', 'AI_STRATEGY', 'AI_DETAILS',
        'AI_NOTE', 'AI_HISTORY', 'AI_CHANGE', 'AI_VERSION', 'AI_TRAIN_HASH',
        'COMPILER_ERR', 'RUNTIME_ERR', 'FIX_REASON',
        'LINUX_REF', 'AMIGAOS_REF', 'AROS_IMPL',
        'REF_GITHUB_ISSUE', 'REF_PR', 'REF_TROUBLE_TICKET',
        'REF_USER_FEEDBACK', 'REF_AUDIT_LOG',
        'HUMAN_OVERRIDE', 'PREVIOUS_IMPLEMENTATION_REF', 'CORRECTION_REF',
        'AI_CONTEXT'
    ]
    
    def __init__(self):
        self.breadcrumbs: List[Breadcrumb] = []
    
    def parse_file(self, file_path: str) -> List[Breadcrumb]:
        """Parse breadcrumbs from a single file"""
        breadcrumbs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            current_breadcrumb = None
            current_tags = {}
            start_line = None
            in_json_block = False
            json_buffer = []
            
            for i, line in enumerate(lines, 1):
                # Check for breadcrumb tags
                for tag in self.BREADCRUMB_TAGS:
                    pattern = rf'//\s*{tag}:\s*(.+)'
                    match = re.search(pattern, line)
                    
                    if match:
                        value = match.group(1).strip()
                        
                        # Initialize breadcrumb if this is the first tag
                        if current_tags == {}:
                            start_line = i
                        
                        if tag == 'AI_CONTEXT':
                            # Start JSON block collection
                            in_json_block = True
                            json_buffer = [value]
                        else:
                            current_tags[tag] = value
                        break
                
                # Continue collecting JSON context
                if in_json_block and line.strip().startswith('//'):
                    json_line = line.strip()[2:].strip()
                    json_buffer.append(json_line)
                    
                    # Check if JSON block is complete
                    if '}' in json_line:
                        try:
                            json_str = ' '.join(json_buffer)
                            current_tags['AI_CONTEXT'] = json.loads(json_str)
                            in_json_block = False
                            json_buffer = []
                        except json.JSONDecodeError:
                            # Continue collecting
                            pass
                
                # If we hit a non-comment line and have tags, save breadcrumb
                if current_tags and not line.strip().startswith('//') and line.strip():
                    breadcrumb = self._create_breadcrumb(file_path, start_line or i, current_tags)
                    breadcrumbs.append(breadcrumb)
                    current_tags = {}
                    start_line = None
                    in_json_block = False
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        self.breadcrumbs.extend(breadcrumbs)
        return breadcrumbs
    
    def _create_breadcrumb(self, file_path: str, line_number: int, tags: Dict[str, str]) -> Breadcrumb:
        """Create a Breadcrumb object from parsed tags"""
        return Breadcrumb(
            file_path=file_path,
            line_number=line_number,
            phase=tags.get('AI_PHASE'),
            status=tags.get('AI_STATUS'),
            pattern=tags.get('AI_PATTERN'),
            strategy=tags.get('AI_STRATEGY'),
            details=tags.get('AI_DETAILS'),
            compiler_err=tags.get('COMPILER_ERR'),
            runtime_err=tags.get('RUNTIME_ERR'),
            fix_reason=tags.get('FIX_REASON'),
            ai_note=tags.get('AI_NOTE'),
            ai_history=tags.get('AI_HISTORY'),
            ai_change=tags.get('AI_CHANGE'),
            ai_version=tags.get('AI_VERSION'),
            ai_train_hash=tags.get('AI_TRAIN_HASH'),
            linux_ref=tags.get('LINUX_REF'),
            amigaos_ref=tags.get('AMIGAOS_REF'),
            aros_impl=tags.get('AROS_IMPL'),
            ref_github_issue=tags.get('REF_GITHUB_ISSUE'),
            ref_pr=tags.get('REF_PR'),
            ai_context=tags.get('AI_CONTEXT'),
            raw_tags=tags
        )
    
    def get_breadcrumbs_by_phase(self, phase: str) -> List[Breadcrumb]:
        """Get all breadcrumbs for a specific phase"""
        return [b for b in self.breadcrumbs if b.phase == phase]
    
    def get_breadcrumbs_by_status(self, status: str) -> List[Breadcrumb]:
        """Get all breadcrumbs with a specific status"""
        return [b for b in self.breadcrumbs if b.status == status]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about parsed breadcrumbs"""
        phases = {}
        statuses = {}
        
        for bc in self.breadcrumbs:
            if bc.phase:
                phases[bc.phase] = phases.get(bc.phase, 0) + 1
            if bc.status:
                statuses[bc.status] = statuses.get(bc.status, 0) + 1
        
        return {
            'total_breadcrumbs': len(self.breadcrumbs),
            'phases': phases,
            'statuses': statuses,
            'files_with_breadcrumbs': len(set(b.file_path for b in self.breadcrumbs))
        }
