"""
Local LLM Interface
Provides reasoning and exploration capabilities using local LLM
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Chat message"""
    role: str  # 'system', 'user', 'assistant'
    content: str


class LocalLLM:
    """Interface for local Large Language Models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = config.get('device', 'cpu')
        self.max_length = config.get('max_length', 2048)
        self.temperature = config.get('temperature', 0.8)
        self.context_window = config.get('context_window', 4096)
        
        self.conversation_history: List[Message] = []
        
        self._load_model()
    
    def _load_model(self):
        """Load the LLM model"""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model_path = self.config.get('model_path', 'meta-llama/Llama-2-7b-chat-hf')
            
            logger.info(f"Loading LLM from {model_path}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float32 if self.device == 'cpu' else torch.float16,
                low_cpu_mem_usage=True
            )
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"LLM loaded successfully on {self.device}")
            
        except ImportError as e:
            logger.error(f"Failed to import required libraries: {e}")
            logger.info("Please install: pip install torch transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            raise
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        reset_history: bool = False
    ) -> str:
        """
        Chat with the LLM
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            reset_history: Reset conversation history
            
        Returns:
            LLM response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        if reset_history:
            self.conversation_history = []
        
        # Add system prompt if provided and history is empty
        if system_prompt and not self.conversation_history:
            self.conversation_history.append(
                Message(role='system', content=system_prompt)
            )
        
        # Add user message
        self.conversation_history.append(
            Message(role='user', content=message)
        )
        
        # Generate response
        response = self._generate_response()
        
        # Add assistant response to history
        self.conversation_history.append(
            Message(role='assistant', content=response)
        )
        
        return response
    
    def _generate_response(self) -> str:
        """Generate a response based on conversation history"""
        import torch
        
        try:
            # Format conversation for the model
            prompt = self._format_conversation()
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=self.max_length,
                    temperature=self.temperature,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the response (remove prompt)
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _format_conversation(self) -> str:
        """Format conversation history for the model"""
        formatted = ""
        
        for msg in self.conversation_history:
            if msg.role == 'system':
                formatted += f"System: {msg.content}\n\n"
            elif msg.role == 'user':
                formatted += f"User: {msg.content}\n\n"
            elif msg.role == 'assistant':
                formatted += f"Assistant: {msg.content}\n\n"
        
        formatted += "Assistant: "
        return formatted
    
    def explore_codebase(
        self,
        query: str,
        file_contents: List[Dict[str, str]],
        breadcrumbs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Explore codebase to understand context before code generation
        
        Args:
            query: What to explore
            file_contents: List of relevant file contents
            breadcrumbs: Relevant breadcrumbs
            
        Returns:
            Exploration results with insights
        """
        system_prompt = """You are an AI assistant helping to explore and understand a codebase.
Your goal is to analyze the provided code and breadcrumbs to gather context for code generation.
Provide concise, actionable insights."""
        
        # Build exploration prompt
        exploration_prompt = f"""Query: {query}

I have the following files and breadcrumbs to analyze:

Files:
"""
        
        for file_info in file_contents[:5]:  # Limit to 5 files
            exploration_prompt += f"\n{file_info.get('path', 'unknown')}:\n"
            exploration_prompt += f"{file_info.get('content', '')[:500]}...\n"
        
        exploration_prompt += "\nBreadcrumbs:\n"
        for bc in breadcrumbs[:5]:  # Limit to 5 breadcrumbs
            exploration_prompt += f"- Phase: {bc.get('phase', 'unknown')}, "
            exploration_prompt += f"Status: {bc.get('status', 'unknown')}, "
            exploration_prompt += f"Strategy: {bc.get('strategy', 'unknown')}\n"
        
        exploration_prompt += "\nBased on this information, provide:\n"
        exploration_prompt += "1. Key patterns and conventions used\n"
        exploration_prompt += "2. Relevant context for the query\n"
        exploration_prompt += "3. Suggested approach for implementation\n"
        
        # Get LLM insights
        response = self.chat(exploration_prompt, system_prompt=system_prompt, reset_history=True)
        
        return {
            'query': query,
            'insights': response,
            'files_analyzed': len(file_contents),
            'breadcrumbs_analyzed': len(breadcrumbs)
        }
    
    def reason_about_task(
        self,
        task_description: str,
        context: Dict[str, Any],
        previous_attempts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Reason about how to approach a task
        
        Args:
            task_description: Description of the task
            context: Context information
            previous_attempts: Previous attempts if any
            
        Returns:
            Reasoning results with strategy
        """
        system_prompt = """You are an AI assistant helping to plan code implementation.
Provide clear, structured reasoning about how to approach the task."""
        
        reasoning_prompt = f"""Task: {task_description}

Context:
- Phase: {context.get('phase', 'unknown')}
- Project: {context.get('project', 'unknown')}
- Current Status: {context.get('status', 'unknown')}
"""
        
        if previous_attempts:
            reasoning_prompt += "\nPrevious attempts:\n"
            for idx, attempt in enumerate(previous_attempts, 1):
                reasoning_prompt += f"{idx}. {attempt}\n"
        
        reasoning_prompt += "\nProvide:\n"
        reasoning_prompt += "1. Analysis of the task\n"
        reasoning_prompt += "2. Key considerations\n"
        reasoning_prompt += "3. Step-by-step strategy\n"
        reasoning_prompt += "4. Potential challenges\n"
        
        response = self.chat(reasoning_prompt, system_prompt=system_prompt, reset_history=True)
        
        return {
            'task': task_description,
            'reasoning': response,
            'context': context
        }
    
    def review_code(
        self,
        code: str,
        requirements: str,
        errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Review generated code for quality and correctness
        
        Args:
            code: The code to review
            requirements: What the code should accomplish
            errors: Any compilation/runtime errors
            
        Returns:
            Review results with suggestions
        """
        system_prompt = """You are a code review assistant. Analyze the code and provide constructive feedback."""
        
        review_prompt = f"""Requirements: {requirements}

Code to review:
```
{code}
```
"""
        
        if errors:
            review_prompt += "\nErrors encountered:\n"
            for error in errors:
                review_prompt += f"- {error}\n"
        
        review_prompt += "\nProvide:\n"
        review_prompt += "1. Assessment of correctness\n"
        review_prompt += "2. Code quality issues\n"
        review_prompt += "3. Suggestions for improvement\n"
        review_prompt += "4. Missing breadcrumb metadata\n"
        
        response = self.chat(review_prompt, system_prompt=system_prompt, reset_history=True)
        
        return {
            'code': code,
            'review': response,
            'has_errors': bool(errors)
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in self.conversation_history
        ]
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
