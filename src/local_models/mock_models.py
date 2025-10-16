"""
Mock Models for Fallback
Provides simulated AI functionality when real models are unavailable
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MockCodegenModel:
    """Mock code generation model for testing/fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = config.get('device', 'cpu')
        self.max_length = config.get('max_length', 512)
        logger.info("Mock codegen model initialized (AI features simulated)")
    
    def generate_code(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        num_return_sequences: int = 1,
        stop_sequences: Optional[List[str]] = None
    ) -> List[str]:
        """Generate mock code based on prompt"""
        logger.debug("Generating mock code")
        
        # Generate a simple template response
        code = f"""// Mock generated code
// Based on prompt: {prompt[:50]}...
void generated_function() {{
    // TODO: Implement functionality
    // This is a mock response - real AI models need to be installed
    printf("Mock implementation\\n");
}}"""
        
        return [code] * num_return_sequences
    
    def generate_with_breadcrumbs(
        self,
        task_description: str,
        context: Dict[str, Any],
        breadcrumb_history: Optional[List[str]] = None,
        stream: bool = False
    ) -> str:
        """Generate mock code with breadcrumbs"""
        logger.debug(f"Generating mock code for task: {task_description}")
        
        phase = context.get('phase', 'DEVELOPMENT')
        status = context.get('status', 'IMPLEMENTING')
        strategy = context.get('strategy', 'Implement the requested functionality')
        
        code = f"""// AI_PHASE: {phase}
// AI_STATUS: {status}
// AI_STRATEGY: {strategy}
// AI_TIMESTAMP: {datetime.now().isoformat()}
// NOTE: This is MOCK code - install real AI models for actual generation

/*
 * Task: {task_description}
 */

"""
        
        if breadcrumb_history:
            code += "// Previous attempts:\n"
            for idx, history_item in enumerate(breadcrumb_history[-3:], 1):
                code += f"// Iteration {idx}: {history_item}\n"
            code += "\n"
        
        code += """// Mock Implementation
void mock_implementation() {
    // TODO: Install real AI models for actual code generation
    // Current response is a template placeholder
    
    printf("Mock implementation - install AI models for real generation\\n");
}
"""
        
        return code
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text"""
        return len(text) // 4
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return True  # Mock is always "loaded"


class MockLLM:
    """Mock LLM for testing/fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = config.get('device', 'cpu')
        self.conversation_history = []
        logger.info("Mock LLM initialized (AI features simulated)")
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        reset_history: bool = False
    ) -> str:
        """Mock chat response"""
        if reset_history:
            self.conversation_history = []
        
        logger.debug(f"Mock LLM responding to: {message[:50]}...")
        
        # Simple template-based response
        response = f"""Based on your request: "{message[:100]}..."

I would suggest the following approach:

1. Analyze the requirements carefully
2. Review similar code patterns in the codebase
3. Implement a clean, maintainable solution
4. Add appropriate error handling
5. Document the implementation with breadcrumbs

Note: This is a MOCK response. Install real AI models for actual intelligent responses.
"""
        
        return response
    
    def explore_codebase(
        self,
        query: str,
        file_contents: List[Dict[str, str]],
        breadcrumbs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock codebase exploration"""
        logger.debug(f"Mock exploration for query: {query}")
        
        insights = f"""Mock Exploration Results for: {query}

Key Patterns Found:
- Files analyzed: {len(file_contents)}
- Breadcrumbs found: {len(breadcrumbs)}
- Common patterns: Standard C coding conventions

Recommendations:
1. Follow existing code structure
2. Use breadcrumb metadata consistently
3. Implement error handling

Note: This is a MOCK exploration. Install real AI models for intelligent codebase analysis.
"""
        
        return {
            'query': query,
            'insights': insights,
            'files_analyzed': len(file_contents),
            'breadcrumbs_analyzed': len(breadcrumbs)
        }
    
    def reason_about_task(
        self,
        task_description: str,
        context: Dict[str, Any],
        previous_attempts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock reasoning about task"""
        logger.debug(f"Mock reasoning for task: {task_description}")
        
        reasoning = f"""Mock Reasoning for: {task_description}

Analysis:
- Phase: {context.get('phase', 'unknown')}
- Project: {context.get('project', 'unknown')}

Strategy:
1. Review task requirements
2. Identify key components
3. Plan implementation steps
4. Consider edge cases

Note: This is a MOCK reasoning. Install real AI models for intelligent task analysis.
"""
        
        return {
            'task': task_description,
            'reasoning': reasoning,
            'context': context
        }
    
    def review_code(
        self,
        code: str,
        requirements: str,
        errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock code review"""
        logger.debug(f"Mock code review for {len(code)} chars")
        
        review = f"""Mock Code Review

Requirements: {requirements[:100]}...

Assessment:
- Code structure: Appears reasonable
- Style: Standard formatting
- Documentation: Could be improved

"""
        
        if errors:
            review += f"\nErrors found ({len(errors)}):\n"
            for error in errors[:3]:
                review += f"- {error}\n"
            review += "\nSuggestions:\n- Review error messages\n- Check function signatures\n"
        
        review += "\nNote: This is a MOCK review. Install real AI models for intelligent code review."
        
        return {
            'code': code,
            'review': review,
            'has_errors': bool(errors)
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return True  # Mock is always "loaded"
