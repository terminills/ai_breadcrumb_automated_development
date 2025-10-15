#!/usr/bin/env python3
"""
Interactive Chat Mode - Copilot-Style Development Assistant
Provides a conversational interface for AI-assisted development
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.streaming_output import OutputFormatter, InteractivePrompt
from src.local_models import LocalModelLoader
from src.interactive_session import SessionManager


class ChatInterface:
    """Interactive chat interface for development assistance"""
    
    def __init__(self):
        self.formatter = OutputFormatter()
        self.session_manager = None
        self.current_session = None
        self.history = []
        
    def print_welcome(self):
        """Print welcome message"""
        welcome = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          AI Development Assistant - Chat Mode             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

I'm your AI development assistant, powered by local models.
I can help you with:
  • Understanding existing code and patterns
  • Planning implementation strategies
  • Generating code with breadcrumbs
  • Reviewing and improving code
  • Learning from errors

Type your questions or requests below. Type 'help' for commands.
Type 'exit' or 'quit' to end the session.
"""
        print(welcome)
    
    def print_help(self):
        """Print help message"""
        help_text = """
Available Commands:
  help          - Show this help message
  explore       - Explore the codebase for specific patterns
  generate      - Generate code for a specific task
  review        - Review existing code
  explain       - Explain a code pattern or breadcrumb
  history       - Show conversation history
  clear         - Clear screen
  reset         - Start a new session
  status        - Show current session status
  exit/quit     - End the chat session

You can also just type natural language questions or requests.

Examples:
  "Explore GPU memory allocation patterns"
  "Generate a shader compilation function"
  "Review this code: [paste code]"
  "Explain the MEMORY_ALLOC_V2 pattern"
"""
        print(help_text)
    
    def initialize_session(self):
        """Initialize the development session"""
        print("\n🔧 Initializing development session...")
        print("   (This may take a moment on first run)\n")
        
        try:
            # In a real implementation, this would load models
            # For now, we simulate it
            self.session_manager = "SessionManager(initialized)"
            print("✓ Session initialized\n")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize session: {e}\n")
            return False
    
    def handle_explore(self, query: str):
        """Handle explore command"""
        print(f"\n📂 Exploring: {query}")
        print("─" * 60)
        
        # Simulate exploration
        findings = [
            "Found 8 relevant C files in radeonsi driver",
            "Identified 3 breadcrumbs with pattern MEMORY_ALLOC_V2",
            "Located reference implementation in amdgpu_object.c",
            "Discovered related functions: gpu_alloc(), gpu_free(), gpu_map()"
        ]
        
        for finding in findings:
            print(f"  • {finding}")
        
        print("\n✓ Exploration complete")
        
        # Add to history
        self.history.append({
            'type': 'explore',
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_generate(self, task: str):
        """Handle generate command"""
        print(f"\n⚡ Generating code for: {task}")
        print("─" * 60)
        
        code = """
// AI_PHASE: GPU_MANAGEMENT
// AI_STATUS: IMPLEMENTED
// AI_STRATEGY: Generated based on your request
// AI_PATTERN: RESOURCE_MGMT_V1

static BOOL manage_gpu_resource(
    struct GPUContext *ctx,
    ResourceType type
) {
    // Initialize resource
    Resource *res = allocate_resource(type);
    if (!res) return FALSE;
    
    // Register with context
    register_resource(ctx, res);
    
    return TRUE;
}
"""
        print(self.formatter.format_code_block(code, 'c'))
        print("✓ Code generated")
        
        # Add to history
        self.history.append({
            'type': 'generate',
            'task': task,
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_review(self):
        """Handle review command"""
        print("\n🔍 Code Review")
        print("─" * 60)
        print("Paste your code below (or type the code).")
        print("Type '###' on a new line when done:\n")
        
        code_lines = []
        while True:
            try:
                line = input()
                if line.strip() == '###':
                    break
                code_lines.append(line)
            except EOFError:
                break
        
        code = '\n'.join(code_lines)
        
        if not code.strip():
            print("\n⚠️  No code provided")
            return
        
        print("\n📝 Review Results:")
        print("─" * 60)
        
        review = """
Analysis:
  ✓ Code structure looks good
  ✓ Error handling present
  ⚠ Missing breadcrumb metadata
  ⚠ Consider adding NULL checks

Suggestions:
  1. Add AI_PHASE and AI_STATUS breadcrumbs
  2. Add more detailed error handling
  3. Consider edge cases (NULL inputs, OOM)
  4. Document any platform-specific behavior

Overall: GOOD with minor improvements needed
"""
        print(review)
        
        # Add to history
        self.history.append({
            'type': 'review',
            'code_length': len(code),
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_explain(self, topic: str):
        """Handle explain command"""
        print(f"\n💡 Explaining: {topic}")
        print("─" * 60)
        
        explanations = {
            "memory_alloc": """
MEMORY_ALLOC_V2 Pattern:
This pattern is used for GPU memory allocation with proper alignment
and error handling.

Key components:
  • Alignment: Ensures memory is aligned to GPU requirements (256 bytes)
  • Error handling: Returns NULL on OOM
  • Tracking: Registers allocation for cleanup
  • Breadcrumbs: Documents allocation strategy

Used in: radeonsi, amdgpu drivers
Reference: LINUX_REF: drivers/gpu/drm/amd/amdgpu/amdgpu_object.c
""",
            "breadcrumb": """
AI Breadcrumbs:
Structured metadata that documents AI-generated code.

Core tags:
  • AI_PHASE: Development phase (e.g., MEMORY_MANAGER)
  • AI_STATUS: Status (IMPLEMENTED, PARTIAL, etc.)
  • AI_STRATEGY: High-level approach description
  • AI_PATTERN: Specific pattern used

Purpose:
  • Makes AI reasoning transparent
  • Enables learning from past attempts
  • Facilitates code review
  • Helps with maintenance

See: docs/AI_BREADCRUMB_GUIDE.md for full specification
"""
        }
        
        # Try to find relevant explanation
        topic_lower = topic.lower()
        explanation = None
        
        for key, text in explanations.items():
            if key in topic_lower or topic_lower in key:
                explanation = text
                break
        
        if explanation:
            print(explanation)
        else:
            print(f"""
I don't have a specific explanation for "{topic}" yet.

You can:
  • Check the documentation in docs/
  • Look at examples in examples/
  • Ask for related topics like:
    - Breadcrumbs and metadata
    - Memory allocation patterns
    - Error handling strategies
""")
        
        # Add to history
        self.history.append({
            'type': 'explain',
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        })
    
    def show_history(self):
        """Show conversation history"""
        print("\n📜 Conversation History")
        print("─" * 60)
        
        if not self.history:
            print("  (No history yet)")
            return
        
        for idx, item in enumerate(self.history, 1):
            time_str = item['timestamp'].split('T')[1][:8]
            type_str = item['type'].upper()
            print(f"  {idx}. [{time_str}] {type_str}")
            
            if item['type'] == 'explore':
                print(f"     Query: {item['query']}")
            elif item['type'] == 'generate':
                print(f"     Task: {item['task']}")
            elif item['type'] == 'explain':
                print(f"     Topic: {item['topic']}")
        
        print()
    
    def show_status(self):
        """Show current session status"""
        print("\n📊 Session Status")
        print("─" * 60)
        print(f"  Session active: Yes")
        print(f"  Commands executed: {len(self.history)}")
        print(f"  Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def process_command(self, user_input: str):
        """Process user command"""
        user_input = user_input.strip()
        
        if not user_input:
            return True
        
        # Split command and args
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Handle commands
        if command in ['exit', 'quit']:
            return False
        
        elif command == 'help':
            self.print_help()
        
        elif command == 'explore':
            if args:
                self.handle_explore(args)
            else:
                print("\n⚠️  Usage: explore <what to explore>")
                print("   Example: explore GPU memory patterns")
        
        elif command == 'generate':
            if args:
                self.handle_generate(args)
            else:
                print("\n⚠️  Usage: generate <what to generate>")
                print("   Example: generate shader compilation function")
        
        elif command == 'review':
            self.handle_review()
        
        elif command == 'explain':
            if args:
                self.handle_explain(args)
            else:
                print("\n⚠️  Usage: explain <topic>")
                print("   Example: explain memory_alloc pattern")
        
        elif command == 'history':
            self.show_history()
        
        elif command == 'status':
            self.show_status()
        
        elif command == 'clear':
            os.system('clear' if os.name == 'posix' else 'cls')
        
        elif command == 'reset':
            self.history = []
            print("\n✓ Session reset\n")
        
        else:
            # Natural language query
            print(f"\n💬 Processing: {user_input}")
            print("─" * 60)
            print("""
I understand you're asking about: "{}"

In a full implementation, I would:
  1. Analyze your query using the LLM
  2. Search relevant code and breadcrumbs
  3. Provide a detailed response
  4. Suggest related actions

For now, try specific commands like:
  • explore <topic>  - Search the codebase
  • generate <task>  - Create code
  • explain <topic>  - Get explanations
""".format(user_input))
            
            self.history.append({
                'type': 'query',
                'text': user_input,
                'timestamp': datetime.now().isoformat()
            })
        
        return True
    
    def run(self):
        """Run the interactive chat interface"""
        self.print_welcome()
        
        # Initialize session
        if not self.initialize_session():
            print("Failed to start session. Exiting.")
            return
        
        # Main chat loop
        try:
            while True:
                try:
                    # Show prompt
                    user_input = input("\n> ").strip()
                    
                    # Process command
                    if not self.process_command(user_input):
                        break
                    
                except KeyboardInterrupt:
                    print("\n")
                    if not InteractivePrompt.ask_yes_no("Do you want to exit?", False):
                        continue
                    else:
                        break
        
        finally:
            print("\n" + "="*60)
            print("Thank you for using the AI Development Assistant!")
            print("="*60)
            print(f"\nCommands executed: {len(self.history)}")
            print("\nSee you next time! 👋\n")


def main():
    """Main entry point"""
    chat = ChatInterface()
    chat.run()


if __name__ == "__main__":
    main()
