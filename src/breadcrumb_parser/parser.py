"""
Breadcrumb Parser
Extracts AI breadcrumb metadata from source files
Supports both // line comments and /* */ block comments
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Iterable


# Complete tag set for breadcrumb metadata
TAG_SET = {
    'AI_PHASE', 'AI_STATUS', 'AI_PATTERN', 'AI_STRATEGY', 'AI_DETAILS',
    'AI_NOTE', 'AI_HISTORY', 'AI_CHANGE', 'AI_VERSION', 'AI_TRAIN_HASH',
    'AI_BREADCRUMB',  # File-level feature marker for bidirectional mapping
    'COMPILER_ERR', 'RUNTIME_ERR', 'FIX_REASON',
    'LINUX_REF', 'AMIGAOS_REF', 'AROS_IMPL',
    'REF_GITHUB_ISSUE', 'REF_PR', 'REF_TROUBLE_TICKET',
    'REF_USER_FEEDBACK', 'REF_AUDIT_LOG',
    'HUMAN_OVERRIDE', 'PREVIOUS_IMPLEMENTATION_REF', 'CORRECTION_REF',
    'AI_CONTEXT',
    # Distributed AI Development Fields
    'AI_ASSIGNED_TO', 'AI_CLAIMED_AT', 'AI_ESTIMATED_TIME', 'AI_PRIORITY',
    'AI_DEPENDENCIES', 'AI_BLOCKS', 'AI_COMPLEXITY', 'AI_BOUNTY',
    'AI_TIMEOUT', 'AI_RETRY_COUNT', 'AI_MAX_RETRIES'
}


@dataclass
class Breadcrumb:
    """Represents a single AI breadcrumb metadata block
    
    Breadcrumbs act as a bidirectional map for tracking development context
    and relationships between code components.
    """
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
    ai_breadcrumb: Optional[str] = None  # File-level feature marker for bidirectional mapping
    ai_history: Optional[str] = None
    ai_change: Optional[str] = None
    ai_version: Optional[str] = None
    ai_train_hash: Optional[str] = None
    linux_ref: Optional[str] = None
    amigaos_ref: Optional[str] = None
    aros_impl: Optional[str] = None
    ref_github_issue: Optional[str] = None
    ref_pr: Optional[str] = None
    ref_trouble_ticket: Optional[str] = None
    ref_user_feedback: Optional[str] = None
    ref_audit_log: Optional[str] = None
    human_override: Optional[str] = None
    previous_implementation_ref: Optional[str] = None
    correction_ref: Optional[str] = None
    ai_context: Optional[Dict[str, Any]] = None
    # Distributed AI Development Fields
    ai_assigned_to: Optional[str] = None
    ai_claimed_at: Optional[str] = None
    ai_estimated_time: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_dependencies: Optional[str] = None
    ai_blocks: Optional[str] = None
    ai_complexity: Optional[str] = None
    ai_bounty: Optional[str] = None
    ai_timeout: Optional[str] = None
    ai_retry_count: Optional[str] = None
    ai_max_retries: Optional[str] = None
    raw_tags: Dict[str, str] = field(default_factory=dict)


class BreadcrumbParser:
    """Parser for AI breadcrumb metadata in source files
    
    Supports both // line comments and /* */ block comments.
    Handles JSON AI_CONTEXT blocks and flushes at EOF.
    """
    
    # Use the global TAG_SET
    BREADCRUMB_TAGS = TAG_SET
    
    # Regex patterns for parsing
    _line_tag_re = re.compile(r'^\s*//\s*(?P<tag>\w+):\s*(?P<value>.*)$')
    _block_start_re = re.compile(r'^\s*/\*\s*$')
    _block_tag_re = re.compile(r'^\s*\*?\s*(?P<tag>\w+):\s*(?P<value>.*)$')
    _block_end_re = re.compile(r'^\s*\*/\s*$')
    
    def __init__(self):
        self.breadcrumbs: List[Breadcrumb] = []
        self._in_block_comment = False
        self._current_tags: Dict[str, Any] = {}
        self._start_line: Optional[int] = None
        self._json_buffer: List[str] = []
        self._in_json = False
    
    def parse_file(self, file_path: str) -> List[Breadcrumb]:
        """Parse breadcrumbs from a single file
        
        Supports both // line comments and /* */ block comments.
        Flushes any pending breadcrumb at EOF.
        """
        breadcrumbs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Reset parser state
            self._in_block_comment = False
            self._current_tags = {}
            self._start_line = None
            self._json_buffer = []
            self._in_json = False
            
            for i, line in enumerate(lines, 1):
                self._parse_line(line, i, file_path, breadcrumbs)
            
            # Flush any remaining breadcrumb at EOF
            if self._current_tags:
                breadcrumb = self._create_breadcrumb(
                    file_path, 
                    self._start_line or len(lines), 
                    self._current_tags
                )
                breadcrumbs.append(breadcrumb)
                self._current_tags = {}
                self._start_line = None
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        self.breadcrumbs.extend(breadcrumbs)
        return breadcrumbs
    
    def _parse_line(self, line: str, line_num: int, file_path: str, breadcrumbs: List[Breadcrumb]) -> None:
        """Parse a single line for breadcrumb tags"""
        stripped = line.strip()
        
        # Check for block comment start
        if self._block_start_re.match(line) and not self._in_block_comment:
            self._in_block_comment = True
            if not self._current_tags:
                self._start_line = line_num
            return
        
        # Check for block comment end
        if self._block_end_re.match(line) and self._in_block_comment:
            self._in_block_comment = False
            # Flush breadcrumb if we have tags
            if self._current_tags and not self._in_json:
                breadcrumb = self._create_breadcrumb(file_path, self._start_line or line_num, self._current_tags)
                breadcrumbs.append(breadcrumb)
                self._current_tags = {}
                self._start_line = None
            return
        
        # Parse tags in block comments
        if self._in_block_comment:
            match = self._block_tag_re.match(line)
            if match:
                tag = match.group('tag').upper()
                value = match.group('value').strip()
                
                if tag in self.BREADCRUMB_TAGS:
                    if not self._current_tags:
                        self._start_line = line_num
                    
                    if tag == 'AI_CONTEXT':
                        self._handle_json_start(value)
                    elif self._in_json:
                        self._handle_json_continue(value)
                    else:
                        self._current_tags[tag] = value
            elif self._in_json:
                # Continue JSON collection in block comment
                self._handle_json_continue(stripped.lstrip('*').strip())
            return
        
        # Parse tags in line comments
        if stripped.startswith('//'):
            match = self._line_tag_re.match(line)
            if match:
                tag = match.group('tag').upper()
                value = match.group('value').strip()
                
                if tag in self.BREADCRUMB_TAGS:
                    if not self._current_tags:
                        self._start_line = line_num
                    
                    if tag == 'AI_CONTEXT':
                        self._handle_json_start(value)
                    elif self._in_json:
                        self._handle_json_continue(value)
                    else:
                        self._current_tags[tag] = value
            elif self._in_json and stripped.startswith('//'):
                # Continue JSON collection in line comment
                json_line = stripped[2:].strip()
                self._handle_json_continue(json_line)
        else:
            # Non-comment line: flush breadcrumb if we have tags
            if self._current_tags and not self._in_block_comment and not self._in_json and stripped:
                breadcrumb = self._create_breadcrumb(file_path, self._start_line or line_num, self._current_tags)
                breadcrumbs.append(breadcrumb)
                self._current_tags = {}
                self._start_line = None
    
    def _handle_json_start(self, value: str) -> None:
        """Start collecting JSON context"""
        self._in_json = True
        self._json_buffer = [value]
        
        # Check if it's a single-line JSON
        if value.strip().startswith('{') and value.strip().endswith('}'):
            self._try_parse_json()
    
    def _handle_json_continue(self, value: str) -> None:
        """Continue collecting JSON context"""
        if self._in_json:
            self._json_buffer.append(value)
            
            # Check if JSON is complete
            if '}' in value:
                self._try_parse_json()
    
    def _try_parse_json(self) -> None:
        """Try to parse accumulated JSON buffer"""
        try:
            json_str = ' '.join(self._json_buffer)
            self._current_tags['AI_CONTEXT'] = json.loads(json_str)
            self._in_json = False
            self._json_buffer = []
        except json.JSONDecodeError:
            # Continue collecting
            pass
    
    def _create_breadcrumb(self, file_path: str, line_number: int, tags: Dict[str, Any]) -> Breadcrumb:
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
            ai_breadcrumb=tags.get('AI_BREADCRUMB'),
            ai_history=tags.get('AI_HISTORY'),
            ai_change=tags.get('AI_CHANGE'),
            ai_version=tags.get('AI_VERSION'),
            ai_train_hash=tags.get('AI_TRAIN_HASH'),
            linux_ref=tags.get('LINUX_REF'),
            amigaos_ref=tags.get('AMIGAOS_REF'),
            aros_impl=tags.get('AROS_IMPL'),
            ref_github_issue=tags.get('REF_GITHUB_ISSUE'),
            ref_pr=tags.get('REF_PR'),
            ref_trouble_ticket=tags.get('REF_TROUBLE_TICKET'),
            ref_user_feedback=tags.get('REF_USER_FEEDBACK'),
            ref_audit_log=tags.get('REF_AUDIT_LOG'),
            human_override=tags.get('HUMAN_OVERRIDE'),
            previous_implementation_ref=tags.get('PREVIOUS_IMPLEMENTATION_REF'),
            correction_ref=tags.get('CORRECTION_REF'),
            ai_context=tags.get('AI_CONTEXT'),
            # Distributed AI Development Fields
            ai_assigned_to=tags.get('AI_ASSIGNED_TO'),
            ai_claimed_at=tags.get('AI_CLAIMED_AT'),
            ai_estimated_time=tags.get('AI_ESTIMATED_TIME'),
            ai_priority=tags.get('AI_PRIORITY'),
            ai_dependencies=tags.get('AI_DEPENDENCIES'),
            ai_blocks=tags.get('AI_BLOCKS'),
            ai_complexity=tags.get('AI_COMPLEXITY'),
            ai_bounty=tags.get('AI_BOUNTY'),
            ai_timeout=tags.get('AI_TIMEOUT'),
            ai_retry_count=tags.get('AI_RETRY_COUNT'),
            ai_max_retries=tags.get('AI_MAX_RETRIES'),
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
    
    def get_breadcrumb_map(self) -> Dict[str, List[Breadcrumb]]:
        """Get bidirectional mapping of breadcrumbs by AI_BREADCRUMB markers
        
        Returns a dictionary where keys are AI_BREADCRUMB values and values are
        lists of breadcrumbs with that marker. This enables bidirectional
        navigation between related code components.
        """
        breadcrumb_map = {}
        
        for bc in self.breadcrumbs:
            if bc.ai_breadcrumb:
                marker = bc.ai_breadcrumb
                if marker not in breadcrumb_map:
                    breadcrumb_map[marker] = []
                breadcrumb_map[marker].append(bc)
        
        return breadcrumb_map
    
    def find_related_breadcrumbs(self, breadcrumb: Breadcrumb) -> List[Breadcrumb]:
        """Find all breadcrumbs related to the given breadcrumb
        
        Uses AI_BREADCRUMB markers to find bidirectionally related breadcrumbs.
        Also checks dependencies, blocks, and reference relationships.
        
        Args:
            breadcrumb: The breadcrumb to find relations for
            
        Returns:
            List of related breadcrumbs
        """
        related = []
        
        # Find by AI_BREADCRUMB marker
        if breadcrumb.ai_breadcrumb:
            breadcrumb_map = self.get_breadcrumb_map()
            marker_matches = breadcrumb_map.get(breadcrumb.ai_breadcrumb, [])
            # Don't include the original breadcrumb
            related.extend([bc for bc in marker_matches if bc != breadcrumb])
        
        # Find by dependencies and blocks (bidirectional)
        if breadcrumb.ai_dependencies:
            deps = [d.strip() for d in breadcrumb.ai_dependencies.split(',')]
            for bc in self.breadcrumbs:
                if bc.phase in deps and bc != breadcrumb:
                    related.append(bc)
        
        if breadcrumb.ai_blocks:
            blocks = [b.strip() for b in breadcrumb.ai_blocks.split(',')]
            for bc in self.breadcrumbs:
                if bc.phase in blocks and bc != breadcrumb:
                    related.append(bc)
        
        # Find reverse dependencies (who depends on this breadcrumb)
        if breadcrumb.phase:
            for bc in self.breadcrumbs:
                if bc.ai_dependencies:
                    deps = [d.strip() for d in bc.ai_dependencies.split(',')]
                    if breadcrumb.phase in deps and bc != breadcrumb:
                        related.append(bc)
                if bc.ai_blocks:
                    blocks = [b.strip() for b in bc.ai_blocks.split(',')]
                    if breadcrumb.phase in blocks and bc != breadcrumb:
                        related.append(bc)
        
        # Find by reference relationships (LINUX_REF, AMIGAOS_REF, etc.)
        if breadcrumb.linux_ref:
            for bc in self.breadcrumbs:
                if bc.linux_ref == breadcrumb.linux_ref and bc != breadcrumb:
                    related.append(bc)
        
        if breadcrumb.amigaos_ref:
            for bc in self.breadcrumbs:
                if bc.amigaos_ref == breadcrumb.amigaos_ref and bc != breadcrumb:
                    related.append(bc)
        
        # Find by correction/previous implementation relationships
        if breadcrumb.previous_implementation_ref:
            # This breadcrumb references a previous implementation
            for bc in self.breadcrumbs:
                if bc.correction_ref == breadcrumb.file_path and bc != breadcrumb:
                    related.append(bc)
        
        if breadcrumb.correction_ref:
            # This breadcrumb is a correction
            for bc in self.breadcrumbs:
                if bc.previous_implementation_ref == breadcrumb.file_path and bc != breadcrumb:
                    related.append(bc)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_related = []
        for bc in related:
            key = (bc.file_path, bc.line_number)
            if key not in seen:
                seen.add(key)
                unique_related.append(bc)
        
        return unique_related
