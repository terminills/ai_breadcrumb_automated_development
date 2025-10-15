# Quick Start Guide - Copilot-Style Iteration

This guide will get you up and running with the new Copilot-style iteration system in under 5 minutes.

## Prerequisites

- Python 3.8 or higher
- At least 8GB RAM (16GB recommended for larger models)
- Optional: AMD GPU with ROCm for acceleration

## Step 1: Install Dependencies

### Option A: CPU Only (Fastest Setup)

```bash
pip install torch transformers
```

### Option B: AMD GPU Acceleration (Recommended for production)

```bash
# Install PyTorch with ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7

# Install Transformers
pip install transformers
```

## Step 2: Configure Models

The system will use default lightweight models if you don't configure anything. To customize:

Edit `config/models.json`:

```json
{
  "codegen": {
    "model_path": "Salesforce/codegen-350M-mono",
    "device": "cpu"
  },
  "llm": {
    "model_path": "meta-llama/Llama-2-7b-chat-hf",
    "device": "cpu"
  }
}
```

For GPU acceleration, change `"device": "cpu"` to `"device": "cuda"`.

## Step 3: Run Your First Iteration

```bash
# Basic usage (will auto-download models on first run)
./scripts/run_copilot_iteration.sh radeonsi 5

# Or for a different project
./scripts/run_copilot_iteration.sh graphics 3
```

**First run note**: The system will download models from Hugging Face (~1-2GB). This only happens once.

## Step 4: Monitor Progress

The system will show real-time progress:

```
============================================================
  Copilot-Style AI Iteration with Local Models
============================================================

Configuration:
  Project: radeonsi
  Max Iterations: 5

Starting Copilot-Style Iteration...

============================================================
Iteration 1/5
Task: RADEONSI_DEVELOPMENT
============================================================

--- Phase 1: Exploration ---
Exploring codebase for: RADEONSI_DEVELOPMENT
Explored 10 files
Found 3 relevant breadcrumbs

--- Phase 2: Reasoning ---
Reasoning completed
Strategy preview: Implement radeonsi functionality using established patterns...

--- Phase 3: Code Generation ---
Generated code (iteration 1)
Code length: 1234 characters

--- Phase 4: Code Review ---
Code review completed

--- Phase 5: Compilation & Testing ---
✓ Compilation successful

--- Phase 6: Learning ---
✓ Iteration successful - no errors to learn from
```

## Step 5: Review Results

Check the logs:

```bash
# View session logs
ls logs/copilot_iteration/sessions/

# View a specific session
cat logs/copilot_iteration/sessions/session_*.json
```

## What Just Happened?

The system performed a complete Copilot-style development cycle:

1. **Explored** your codebase for relevant patterns
2. **Reasoned** about the task using the local LLM
3. **Generated** code with AI breadcrumbs using the codegen model
4. **Reviewed** the generated code for quality
5. **Compiled** and tested (simulated for demo)
6. **Learned** from any errors

All of this happened **locally** using your own hardware!

## Next Steps

### Try Interactive Mode (Python API)

```python
from src.local_models import LocalModelLoader
from src.interactive_session import SessionManager

# Initialize
loader = LocalModelLoader()
session = SessionManager(
    model_loader=loader,
    aros_path='aros-src',
    log_path='logs/sessions'
)

# Start a session
session_id = session.start_session(
    task_description="Implement GPU memory management",
    context={'phase': 'MEMORY_MANAGER', 'project': 'radeonsi'}
)

# Explore
exploration = session.explore("GPU memory management")
print(exploration['insights'])

# Generate
generation = session.generate()
print(generation['code'])

# End session
session.end_session(status='completed')
```

### Customize for Your Project

1. **Change the project**: Replace `radeonsi` with your project name
2. **Adjust iterations**: Change the number based on complexity
3. **Use better models**: Edit `config/models.json` to use larger models
4. **Enable GPU**: Set device to "cuda" in config

### Advanced Usage

See the full documentation:

- [COPILOT_STYLE_ITERATION.md](COPILOT_STYLE_ITERATION.md) - Complete guide
- [API Reference](#) - Detailed API documentation
- [Model Selection Guide](#) - Choosing the right models

## Troubleshooting

### "Model not found"

The model needs to be downloaded. Ensure internet connection and it will download automatically on first use.

### "Out of memory"

Use a smaller model:

```json
{
  "codegen": {
    "model_path": "Salesforce/codegen-350M-mono"
  }
}
```

### "Slow generation"

Consider:
- Using GPU acceleration
- Using smaller models for faster iteration
- Reducing `max_files_to_scan` in exploration config

### "CUDA not available"

Either:
- Install ROCm for AMD GPUs
- Use CPU by setting `"device": "cpu"` in config

## Performance Tips

- **First run**: Will be slow due to model download
- **Subsequent runs**: Much faster as models are cached
- **GPU acceleration**: 5-10x faster than CPU
- **Model size**: Smaller = faster, but lower quality
- **Balance**: 350M codegen + 7B LLM is a good starting point

## What's Different from Standard Iteration?

| Feature | Standard | Copilot-Style |
|---------|----------|---------------|
| Exploration | ❌ | ✅ Automatic |
| Reasoning | ❌ | ✅ LLM-powered |
| Context Awareness | Basic | Extensive |
| Self-Review | ❌ | ✅ Built-in |
| Sessions | ❌ | ✅ Multi-turn |
| Streaming | ❌ | ✅ Real-time |
| Local Models | ❌ | ✅ Fully local |

## Getting Help

- Check the [full documentation](COPILOT_STYLE_ITERATION.md)
- Review [test examples](../tests/test_copilot_iteration.py)
- Check [configuration guide](../config/models.json)

Happy coding with local AI! 🚀
