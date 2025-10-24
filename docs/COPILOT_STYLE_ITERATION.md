# Copilot-Style Iteration with Local Models

## Overview

The enhanced iteration system provides GitHub Copilot-style interactive development using **local AI models** instead of cloud services. This implementation uses:

- **Local Code Generation**: Salesforce Codegen or similar models for code generation
- **Local LLM**: Llama 2, Mistral, or other local LLMs for reasoning and exploration
- **Interactive Sessions**: Multi-turn conversations with context preservation
- **Exploration Phase**: Automatic codebase analysis before code generation
- **Self-Review**: Generated code is reviewed before compilation

## Key Features

### 1. Exploration Before Generation

Like GitHub Copilot, the system explores the codebase before generating code:

- Finds relevant files based on the task
- Analyzes existing breadcrumbs for patterns
- Gathers context from similar implementations
- Uses LLM to extract insights from the exploration

### 2. Reasoning Phase

The system reasons about the task before generating code:

- Analyzes the requirements
- Considers previous attempts
- Develops a step-by-step strategy
- Identifies potential challenges

### 3. Interactive Code Generation

Generates code with full context:

- Uses exploration insights
- Follows discovered patterns
- Includes AI breadcrumb metadata
- Maintains conversation history

### 4. Self-Review

Reviews generated code before compilation:

- Checks correctness against requirements
- Identifies potential issues
- Suggests improvements
- Validates breadcrumb metadata

### 5. Iterative Learning

Learns from compilation results:

- Tracks errors across iterations
- Identifies patterns in failures
- Improves success rate over time
- Maintains error database

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Manager                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Interactive Session                                  │  │
│  │  - Multi-turn conversations                           │  │
│  │  - Context preservation                               │  │
│  │  - History tracking                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Model Loader                             │
│  ┌──────────────────┐         ┌─────────────────────────┐  │
│  │  Codegen Model   │         │      Local LLM         │  │
│  │  - Code gen      │         │  - Reasoning           │  │
│  │  - Breadcrumbs   │         │  - Exploration         │  │
│  │  - Completion    │         │  - Review              │  │
│  └──────────────────┘         └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                Iteration Loop (6 Phases)                    │
│                                                             │
│  Phase 1: Exploration  → Gather context from codebase      │
│  Phase 2: Reasoning    → Analyze task and plan approach    │
│  Phase 3: Generation   → Generate code with breadcrumbs    │
│  Phase 4: Review       → Self-review generated code        │
│  Phase 5: Compilation  → Compile and test                  │
│  Phase 6: Learning     → Track errors and improve          │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### 1. Basic Installation (CPU)

```bash
pip install torch transformers
```

### 2. AMD ROCm Installation (GPU Acceleration)

For AMD GPUs (Radeon Pro V620, Radeon Pro V620, RX 6000/7000 series):

```bash
# Install PyTorch with ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.0

# Install Transformers
pip install transformers accelerate
```

### 3. Model Download

The models will be automatically downloaded on first use. To pre-download:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Download Codegen model (code generation)
AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")

# Download Llama 2 model (requires Hugging Face token)
# Get token from: https://huggingface.co/settings/tokens
AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf", use_auth_token="your_token")
```

## Configuration

Edit `config/models.json` to customize model settings:

```json
{
  "codegen": {
    "model_path": "Salesforce/codegen-350M-mono",
    "device": "cpu",
    "max_length": 512,
    "temperature": 0.7
  },
  "llm": {
    "model_path": "meta-llama/Llama-2-7b-chat-hf",
    "device": "cpu",
    "max_length": 2048,
    "temperature": 0.8
  },
  "exploration": {
    "enabled": true,
    "max_files_to_scan": 50
  }
}
```

### Model Options

#### Code Generation Models

- `Salesforce/codegen-350M-mono` (350M params) - Fast, lightweight
- `Salesforce/codegen-2B-mono` (2B params) - Better quality
- `Salesforce/codegen-6B-mono` (6B params) - Highest quality
- `bigcode/starcoderbase` (15B params) - State-of-the-art

#### LLM Models

- `meta-llama/Llama-2-7b-chat-hf` (7B params) - Recommended
- `mistralai/Mistral-7B-v0.1` (7B params) - Good alternative
- `codellama/CodeLlama-7b-hf` (7B params) - Code-focused
- `WizardLM/WizardCoder-15B-V1.0` (15B params) - Advanced

### Hardware Acceleration

To use AMD GPU:

```json
{
  "codegen": {
    "device": "cuda"
  },
  "llm": {
    "device": "cuda"
  },
  "hardware": {
    "use_gpu_if_available": true
  }
}
```

## Usage

### Basic Usage

```bash
./scripts/run_copilot_iteration.sh [PROJECT] [MAX_ITERATIONS]
```

Examples:

```bash
# Work on radeonsi project, 10 iterations
./scripts/run_copilot_iteration.sh radeonsi 10

# Work on graphics, 5 iterations
./scripts/run_copilot_iteration.sh graphics 5

# Work on kernel, 20 iterations
./scripts/run_copilot_iteration.sh kernel 20
```

### Advanced Usage

```bash
./scripts/run_copilot_iteration.sh [PROJECT] [MAX_ITERATIONS] [AROS_PATH] [LOG_PATH]
```

Example:

```bash
./scripts/run_copilot_iteration.sh radeonsi 15 /path/to/aros-src /path/to/logs
```

### Python API

```python
from src.copilot_iteration import CopilotStyleIteration

# Create iteration instance
iteration = CopilotStyleIteration(
    aros_path='aros-src',
    project_name='radeonsi',
    log_path='logs/copilot',
    max_iterations=10
)

# Run the iteration loop
summary = iteration.run()

print(f"Success rate: {summary['successful']/summary['total_iterations']*100:.1f}%")
```

### Interactive Session API

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

# Start session
session_id = session.start_session(
    task_description="Implement GPU memory management",
    context={'phase': 'MEMORY_MANAGER', 'project': 'radeonsi'}
)

# Explore codebase
exploration = session.explore("GPU memory management")
print(exploration['insights'])

# Reason about task
reasoning = session.reason()
print(reasoning['reasoning'])

# Generate code
generation = session.generate(use_exploration=True)
print(generation['code'])

# Review code
review = session.review()
print(review['review'])

# End session
session.end_session(status='completed')
```

## Output and Logs

The system creates detailed logs in three categories:

### 1. Session Logs (`logs/copilot_iteration/sessions/`)

Each session is saved as a JSON file containing:
- Task description and context
- All exploration results
- Reasoning traces
- Generated code history
- Review results
- Conversation history

### 2. Compilation Logs (`logs/copilot_iteration/compile/`)

Compilation results including:
- Success/failure status
- Compiler output (stdout/stderr)
- Parsed errors and warnings
- Duration and timestamp

### 3. Error Logs (`logs/copilot_iteration/errors/`)

Error tracking database:
- Unique error patterns
- Resolution history
- Statistics and trends

## Performance Tips

### 1. Model Selection

- **Small projects (<1000 LOC)**: Use 350M codegen + 7B LLM
- **Medium projects (1000-10000 LOC)**: Use 2B codegen + 7B LLM
- **Large projects (>10000 LOC)**: Use 6B codegen + 13B LLM

### 2. Hardware Optimization

**CPU Only:**
- Use smaller models (350M codegen, 7B LLM)
- Reduce `max_length` to 256-512
- Process one file at a time

**AMD GPU (8GB VRAM):**
- Can run 2B codegen + 7B LLM
- Use `torch.float16` for better performance
- Enable `low_cpu_mem_usage=True`

**AMD GPU (16GB+ VRAM):**
- Can run 6B codegen + 13B LLM
- Use full precision if needed
- Enable batch processing

### 3. Exploration Optimization

Reduce exploration scope for faster iterations:

```json
{
  "exploration": {
    "max_files_to_scan": 20,
    "enable_caching": true
  }
}
```

## Comparison with Original Iteration

| Feature | Original | Copilot-Style |
|---------|----------|---------------|
| Code Generation | Simulated | Local model |
| Exploration | None | Automatic |
| Reasoning | None | LLM-powered |
| Self-Review | None | Built-in |
| Context Awareness | Limited | Extensive |
| Session Management | None | Multi-turn |
| Learning | Error tracking | Enhanced tracking |
| Interactivity | Batch only | Interactive |

## Troubleshooting

### Issue: "Model not found"

**Solution**: The model needs to be downloaded. Ensure you have internet connection and run:

```python
from transformers import AutoModelForCausalLM
AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
```

### Issue: "Out of memory"

**Solutions**:
1. Use a smaller model
2. Reduce `max_length` in config
3. Enable `low_cpu_mem_usage=True`
4. Use CPU instead of GPU for very large models

### Issue: "CUDA/ROCm not found"

**Solution**: PyTorch is trying to use GPU but drivers aren't installed. Either:
1. Install ROCm: Follow AMD ROCm installation guide
2. Force CPU: Set `"device": "cpu"` in config

### Issue: "Slow generation"

**Solutions**:
1. Use GPU acceleration
2. Use smaller models
3. Reduce exploration scope
4. Enable caching

### Issue: "Token limit exceeded"

**Solution**: The context is too large. Reduce:
- `max_files_to_scan` in exploration config
- Conversation history length
- Input prompt size

## Future Enhancements

Planned features:

- [ ] Streaming output (real-time generation display)
- [ ] Multi-model ensemble for better quality
- [ ] Fine-tuning on AROS codebase
- [ ] Integration with UI for live monitoring
- [ ] Distributed iteration across multiple GPUs
- [ ] Automatic model selection based on hardware
- [ ] Embeddings-based code search
- [ ] Automatic test generation

## Contributing

To add new features:

1. **New Models**: Add to `src/local_models/`
2. **New Phases**: Extend `CopilotStyleIteration` class
3. **New Exploration**: Enhance `SessionManager.explore()`
4. **New Review**: Extend `LocalLLM.review_code()`

## References

- [Salesforce Codegen](https://github.com/salesforce/CodeGen)
- [Llama 2](https://ai.meta.com/llama/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [AMD ROCm](https://rocm.docs.amd.com/)
- [AI Breadcrumb System](../README.md#ai-breadcrumb-system)
