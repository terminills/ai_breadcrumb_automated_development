"""
Codegen Model Interface
Handles code generation using local models
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class CodegenModel:
    """Interface for local code generation models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = config.get('device', 'cpu')
        self.max_length = config.get('max_length', 512)
        self.temperature = config.get('temperature', 0.7)
        self.top_p = config.get('top_p', 0.95)
        
        self._load_model()
    
    def _load_model(self):
        """Load the code generation model"""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model_path = self.config.get('model_path', 'Salesforce/codegen-350M-mono')
            
            logger.info(f"Loading codegen model from {model_path}...")
            
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
            
            logger.info(f"Codegen model loaded successfully on {self.device}")
            
        except ImportError as e:
            logger.error(f"Failed to import required libraries: {e}")
            logger.info("Please install: pip install torch transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load codegen model: {e}")
            raise
    
    def generate_code(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        num_return_sequences: int = 1,
        stop_sequences: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate code from a prompt
        
        Args:
            prompt: The code prompt/context
            max_length: Maximum length of generated code
            temperature: Sampling temperature
            num_return_sequences: Number of sequences to generate
            stop_sequences: List of sequences to stop generation
            
        Returns:
            List of generated code strings
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        import torch
        
        max_length = max_length or self.max_length
        temperature = temperature or self.temperature
        
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=self.top_p,
                    num_return_sequences=num_return_sequences,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode outputs
            generated_codes = []
            for output in outputs:
                code = self.tokenizer.decode(output, skip_special_tokens=True)
                
                # Remove the prompt from the output
                if code.startswith(prompt):
                    code = code[len(prompt):]
                
                # Apply stop sequences
                if stop_sequences:
                    for stop_seq in stop_sequences:
                        if stop_seq in code:
                            code = code[:code.index(stop_seq)]
                
                generated_codes.append(code.strip())
            
            return generated_codes
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise
    
    def generate_with_breadcrumbs(
        self,
        task_description: str,
        context: Dict[str, Any],
        breadcrumb_history: Optional[List[str]] = None,
        stream: bool = False
    ) -> str:
        """
        Generate code with AI breadcrumb metadata
        
        Args:
            task_description: Description of the task
            context: Context information (phase, strategy, etc.)
            breadcrumb_history: Previous breadcrumb attempts
            stream: Whether to stream generation token by token
            
        Returns:
            Generated code with breadcrumbs
        """
        # Build prompt with breadcrumb context
        prompt = self._build_breadcrumb_prompt(
            task_description,
            context,
            breadcrumb_history
        )
        
        # Generate code
        if stream:
            return self._generate_streaming(prompt)
        else:
            generated = self.generate_code(prompt, num_return_sequences=1)
            if generated:
                return generated[0]
            return ""
    
    def _generate_streaming(self, prompt: str) -> str:
        """Generate code with streaming output"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        import torch
        from src.streaming_output import StreamingHandler
        
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Create streaming handler
            handler = StreamingHandler()
            
            # Stream generation
            full_text = ""
            for token in handler.stream_generation(
                self.model,
                self.tokenizer,
                inputs['input_ids'],
                max_length=self.max_length,
                temperature=self.temperature
            ):
                full_text += token
                handler.callback(token)
            
            # Remove prompt from output
            if full_text.startswith(prompt):
                full_text = full_text[len(prompt):]
            
            return full_text.strip()
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
    
    def _build_breadcrumb_prompt(
        self,
        task_description: str,
        context: Dict[str, Any],
        breadcrumb_history: Optional[List[str]] = None
    ) -> str:
        """Build a prompt that encourages breadcrumb generation"""
        prompt = f"""// Task: {task_description}
// AI_PHASE: {context.get('phase', 'DEVELOPMENT')}
// AI_STATUS: {context.get('status', 'IMPLEMENTING')}
// AI_STRATEGY: {context.get('strategy', 'Implement the requested functionality')}

"""
        
        if breadcrumb_history:
            prompt += "// Previous attempts:\n"
            for idx, history_item in enumerate(breadcrumb_history[-3:], 1):
                prompt += f"// Iteration {idx}: {history_item}\n"
            prompt += "\n"
        
        prompt += "// Implementation:\n"
        return prompt
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
