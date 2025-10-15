# Interactive Development Guide

This guide introduces the interactive features of the AI Breadcrumb Development System, designed to provide a GitHub Copilot-style experience with local models.

## Quick Start

### 1. Launch Interactive Mode

The easiest way to get started is with the interactive mode launcher:

```bash
./scripts/interactive_mode.sh
```

This menu-driven interface lets you choose from:
- Interactive Demo - See the full workflow
- Chat Mode - Conversational assistant
- Copilot Iteration - Real model integration
- Web UI - Browser-based monitoring

### 2. Interactive Demo

Try the demo to see all phases of development in action:

```bash
python3 scripts/interactive_demo.py
```

**What you'll see:**
- Phase 1: Code exploration
- Phase 2: Task reasoning
- Phase 3: Code generation with breadcrumbs
- Phase 4: Self-review
- Phase 5: Compilation
- Phase 6: Learning from results

The demo runs without models, showing you what the full experience looks like.

### 3. Chat Mode

Start a conversational session with the AI assistant:

```bash
python3 scripts/interactive_chat.py
```

**Available commands:**
```
explore <query>     - Search the codebase
generate <task>     - Create code for a task
review              - Review code (paste when prompted)
explain <topic>     - Get explanations
history             - Show conversation history
status              - Session information
help                - Show all commands
```

**Example session:**
```
> explore GPU memory allocation patterns

📂 Exploring: GPU memory allocation patterns
  • Found 8 relevant C files in radeonsi driver
  • Identified 3 breadcrumbs with pattern MEMORY_ALLOC_V2
  • Located reference implementation in amdgpu_object.c
✓ Exploration complete

> generate shader compilation function

⚡ Generating code for: shader compilation function
[Generated code with breadcrumbs displayed]
✓ Code generated

> explain breadcrumb

💡 Explaining: breadcrumb
[Detailed explanation provided]
```

## Features

### Real-Time Progress

All interactive tools show real-time progress with:
- Animated spinners during processing
- Progress bars for long operations
- Status indicators (✓ success, ✗ error, ⚠ warning)
- Clear phase separation

### Context Preservation

The system maintains context across:
- Multi-turn conversations
- Multiple iterations
- Session history
- Error tracking

### Streaming Output

Experience Copilot-style output:
- Token-by-token code generation
- Real-time compilation feedback
- Progressive exploration results
- Live learning updates

## Integration with Web UI

Launch the web UI for visual monitoring:

```bash
./start_ui.sh
```

Access at: http://localhost:5000

**Features:**
- Real-time dashboard
- Breadcrumb statistics
- Compilation results
- Error tracking
- Project management
- Git integration

## Advanced Usage

### Custom Interactive Scripts

Create your own interactive workflows using the Python API:

```python
from src.streaming_output import OutputFormatter, ProgressIndicator
from src.interactive_session import SessionManager
from src.local_models import LocalModelLoader

# Initialize
formatter = OutputFormatter()
loader = LocalModelLoader()
session = SessionManager(loader, 'aros-src', 'logs')

# Start session
session_id = session.start_session(
    task_description="Implement feature X",
    context={'phase': 'DEVELOPMENT'}
)

# Explore
print("Exploring...")
exploration = session.explore("feature X patterns")
print(formatter.format_list(exploration.get('insights', [])))

# Generate
print("\nGenerating code...")
generation = session.generate(use_exploration=True)
print(formatter.format_code_block(generation['code']))

# Review
review = session.review()
print(f"\nReview: {review['review']}")

# End
session.end_session(status='completed')
```

### Keyboard Shortcuts

In chat mode:
- `Ctrl+C` - Interrupt (asks for confirmation)
- `Ctrl+D` - End input (in review mode)
- Arrow keys - Navigate command history (in shells that support it)

### Session Management

Sessions are automatically saved to `logs/sessions/`:
- Each session gets a unique ID
- All turns are recorded
- Exploration results preserved
- Generation history maintained

View past sessions:
```bash
ls logs/sessions/
cat logs/sessions/session_*.json
```

## Tips for Best Results

### 1. Be Specific in Queries

❌ Bad: "help with memory"
✓ Good: "explore GPU memory allocation patterns in radeonsi"

### 2. Use Commands Effectively

Start with `explore` before `generate`:
```
> explore texture upload implementation
> generate texture upload function based on exploration
```

### 3. Iterate on Feedback

If generated code isn't perfect:
```
> review
[paste code]
> generate improved version with better error handling
```

### 4. Build on Context

The system remembers your session:
- Previous explorations inform generation
- Error patterns are tracked
- Successful patterns are reused

### 5. Use the Right Tool

- **Demo** - Learn the workflow
- **Chat** - Quick queries and exploration
- **Copilot** - Full development iterations
- **Web UI** - Monitoring and project management

## Troubleshooting

### "Models not loading"

For the demo and chat mode, no models are required - they simulate the experience. For real model integration, see:
- `docs/COPILOT_STYLE_ITERATION.md` - Full model setup
- `docs/QUICKSTART_COPILOT.md` - Quick model installation

### "Session won't start"

Check that necessary directories exist:
```bash
mkdir -p logs/sessions logs/errors logs/reasoning
```

### "Chat mode stuck"

Press `Ctrl+C` to interrupt. Type `reset` to start fresh.

### "Interactive demo exits immediately"

Make sure you answer 'y' when prompted to continue:
```bash
echo "y" | python3 scripts/interactive_demo.py
```

Or run interactively:
```bash
python3 scripts/interactive_demo.py
```

## Next Steps

### Learn More

- **Copilot System**: `docs/COPILOT_STYLE_ITERATION.md`
- **API Examples**: `examples/copilot_api_example.py`
- **Quick Start**: `docs/QUICKSTART_COPILOT.md`
- **System Overview**: `SYSTEM_OVERVIEW.md`

### Try Real Models

Install models for real code generation:
```bash
pip install torch transformers
# See docs/QUICKSTART_COPILOT.md for configuration
```

### Customize

Edit configurations:
- `config/models.json` - Model settings
- `config/config.json` - System settings

### Contribute

Found issues or have ideas?
- Open an issue on GitHub
- Submit a pull request
- Share your workflows

## Examples

### Example 1: Quick Code Generation

```bash
python3 scripts/interactive_chat.py
> generate GPU memory allocation function
[Code generated with breadcrumbs]
> exit
```

### Example 2: Explore Then Generate

```bash
python3 scripts/interactive_chat.py
> explore shader compilation patterns
> explain SHADER_COMPILE_V1 pattern
> generate shader compilation function using that pattern
> review
[paste generated code]
> exit
```

### Example 3: Full Demo Walkthrough

```bash
python3 scripts/interactive_demo.py
# Answer 'y' to start
# Choose a task (1-4)
# Watch all 6 phases execute
# See results and summary
```

## Integration Examples

### With Version Control

```bash
# Explore before coding
python3 scripts/interactive_chat.py
> explore feature requirements
> generate implementation

# Take generated code, refine, commit
git add src/feature.c
git commit -m "AI_PHASE: FEATURE_IMPL - Added feature"
```

### With CI/CD

Include interactive tools in your workflow:
```yaml
# .github/workflows/ai-assist.yml
- name: Generate missing implementations
  run: |
    ./scripts/run_copilot_iteration.sh project 5
```

### With IDEs

Use as external tool in VS Code, Vim, or Emacs:
```bash
# In VS Code tasks.json
{
  "label": "AI Assistant",
  "type": "shell",
  "command": "python3 scripts/interactive_chat.py"
}
```

---

**Ready to start?** Run:
```bash
./scripts/interactive_mode.sh
```

**Need help?** See:
- Full documentation: `docs/`
- Examples: `examples/`
- Scripts: `scripts/`
