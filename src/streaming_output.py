"""
Streaming Output Handler
Provides real-time streaming of model generation like GitHub Copilot
"""

import sys
import time
from typing import Callable, Optional, Iterator
from threading import Thread
from queue import Queue


class StreamingHandler:
    """Handles streaming output for real-time feedback"""
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        """
        Initialize streaming handler
        
        Args:
            callback: Optional callback function for each token
        """
        self.callback = callback or self._default_callback
        self.is_streaming = False
        self.buffer = Queue()
        
    def _default_callback(self, token: str):
        """Default callback: print to stdout"""
        print(token, end='', flush=True)
    
    def stream_generation(
        self,
        model,
        tokenizer,
        input_ids,
        max_length: int = 512,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """
        Stream model generation token by token
        
        Args:
            model: The model to generate from
            tokenizer: The tokenizer
            input_ids: Input token IDs
            max_length: Maximum generation length
            temperature: Sampling temperature
            
        Yields:
            Generated tokens as strings
        """
        import torch
        
        self.is_streaming = True
        generated_ids = input_ids.clone()
        
        try:
            with torch.no_grad():
                for _ in range(max_length - len(input_ids[0])):
                    if not self.is_streaming:
                        break
                    
                    # Generate next token
                    outputs = model(generated_ids)
                    next_token_logits = outputs.logits[0, -1, :]
                    
                    # Apply temperature
                    next_token_logits = next_token_logits / temperature
                    
                    # Sample
                    probs = torch.nn.functional.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                    
                    # Decode token
                    token_str = tokenizer.decode([next_token.item()])
                    
                    # Check for EOS
                    if next_token.item() == tokenizer.eos_token_id:
                        break
                    
                    # Append to generated sequence
                    generated_ids = torch.cat([generated_ids, next_token.unsqueeze(0)], dim=1)
                    
                    # Yield token
                    yield token_str
                    
        finally:
            self.is_streaming = False
    
    def stop_streaming(self):
        """Stop streaming generation"""
        self.is_streaming = False


class ProgressIndicator:
    """Shows progress indicator during long operations"""
    
    def __init__(self, message: str = "Processing"):
        self.message = message
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the progress indicator"""
        self.running = True
        self.thread = Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the progress indicator"""
        self.running = False
        if self.thread:
            self.thread.join()
        print()  # New line after indicator
    
    def _animate(self):
        """Animate the progress indicator"""
        indicators = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        idx = 0
        
        while self.running:
            indicator = indicators[idx % len(indicators)]
            print(f'\r{indicator} {self.message}...', end='', flush=True)
            idx += 1
            time.sleep(0.1)


class OutputFormatter:
    """Formats output for better readability"""
    
    @staticmethod
    def format_code_block(code: str, language: str = 'c') -> str:
        """Format code block with syntax highlighting markers"""
        return f"\n```{language}\n{code}\n```\n"
    
    @staticmethod
    def format_section(title: str, content: str) -> str:
        """Format a section with title"""
        separator = "─" * 60
        return f"\n{separator}\n  {title}\n{separator}\n{content}\n"
    
    @staticmethod
    def format_list(items: list, bullet: str = "•") -> str:
        """Format a bulleted list"""
        return "\n".join(f"{bullet} {item}" for item in items)
    
    @staticmethod
    def format_status(status: str, success: bool) -> str:
        """Format status message with icon"""
        icon = "✓" if success else "✗"
        color_code = "\033[92m" if success else "\033[91m"  # Green or Red
        reset_code = "\033[0m"
        return f"{color_code}{icon}{reset_code} {status}"
    
    @staticmethod
    def format_progress(current: int, total: int, label: str = "") -> str:
        """Format progress indicator"""
        percentage = (current / total * 100) if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"{label} [{bar}] {current}/{total} ({percentage:.1f}%)"


class InteractivePrompt:
    """Handles interactive user input"""
    
    @staticmethod
    def ask_yes_no(question: str, default: bool = True) -> bool:
        """Ask a yes/no question"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} ({default_str}): ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes']
    
    @staticmethod
    def ask_choice(question: str, choices: list) -> int:
        """Ask user to choose from a list"""
        print(question)
        for idx, choice in enumerate(choices, 1):
            print(f"  {idx}. {choice}")
        
        while True:
            try:
                response = input("Enter choice (number): ").strip()
                choice_idx = int(response) - 1
                
                if 0 <= choice_idx < len(choices):
                    return choice_idx
                else:
                    print(f"Please enter a number between 1 and {len(choices)}")
            except (ValueError, KeyboardInterrupt):
                print("Invalid input. Please enter a number.")
    
    @staticmethod
    def ask_string(question: str, default: str = "") -> str:
        """Ask for string input"""
        prompt = f"{question}"
        if default:
            prompt += f" (default: {default})"
        prompt += ": "
        
        response = input(prompt).strip()
        return response if response else default
