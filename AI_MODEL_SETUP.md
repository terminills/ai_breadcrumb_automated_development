# AI Model Setup Guide

## Overview

The AROS-Cognito system uses two AI models for intelligent code generation and analysis:

1. **CodeGen** - For code generation (Salesforce/codegen-350M-mono, ~350MB)
2. **LLaMA-2** - For reasoning and exploration (meta-llama/Llama-2-7b-chat-hf, ~13GB)

## Mock Model Fallback

**Important:** The system includes a mock model fallback feature. This means:

- ✅ The system works even without downloading AI models
- ✅ All iteration loops and sessions will run successfully
- ✅ Mock AI provides template-based responses for testing
- ⚠️ For actual intelligent AI responses, you need to download real models

## Installation Options

### Option 1: Use Mock Models (Default)

The system automatically uses mock models if real models aren't available. No action needed!

```bash
# Just run the system - it will use mocks automatically
./scripts/run_copilot_iteration.sh
```

### Option 2: Install CodeGen Only (Lightweight)

For basic code generation with a small model (~350MB):

```bash
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM

print("Downloading CodeGen model (~350MB)...")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
print("✓ CodeGen model downloaded successfully!")
EOF
```

### Option 3: Install Full AI Stack (Recommended)

For complete AI capabilities including intelligent reasoning:

#### Step 1: Get HuggingFace Token

1. Visit https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
2. Click "Access repository"
3. Fill out the form and wait for approval (usually instant)
4. Go to https://huggingface.co/settings/tokens
5. Create a new token with "Read" access
6. Copy the token

#### Step 2: Download Models

```bash
# Set your HuggingFace token
export HF_TOKEN='your_token_here'

# Download CodeGen (small model, ~350MB)
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM

print("Downloading CodeGen model (~350MB)...")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
print("✓ CodeGen downloaded!")
EOF

# Download LLaMA-2 (large model, ~13GB - requires token)
python3 << 'EOF'
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

token = os.environ.get('HF_TOKEN')
if not token:
    print("Error: HF_TOKEN not set")
    exit(1)

print("Downloading LLaMA-2 model (~13GB - this may take a while)...")
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    use_auth_token=token
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    use_auth_token=token
)
print("✓ LLaMA-2 downloaded!")
EOF
```

## GPU Acceleration (Optional)

### With AMD ROCm

If you have an AMD GPU with ROCm 5.7.1 installed:

```bash
# Models will automatically use GPU if available
# Check GPU is detected:
python3 -c "import torch; print('GPU available:', torch.cuda.is_available())"
```

The system will automatically use your GPU for faster inference.

### CPU-Only Mode

Models work fine on CPU, but inference will be slower. This is automatically handled.

## Verifying Installation

```bash
# Test that models load correctly
python3 tests/test_mock_models.py

# You should see either:
# - "Mock model" messages (if using fallback)
# - "Model loaded successfully" (if real models are installed)
```

## Model Storage

Models are cached by transformers in:
- Linux: `~/.cache/huggingface/hub/`
- The total size is approximately 13.5GB for both models

You can change the cache directory:
```bash
export TRANSFORMERS_CACHE=/path/to/cache
```

## Troubleshooting

### "No module named 'torch'"

Install PyTorch:
```bash
pip install torch transformers
# Or use the setup script:
./scripts/setup.sh
```

### "Failed to load model"

The system will automatically fall back to mock models. To use real models:

1. Ensure torch and transformers are installed
2. For LLaMA-2, ensure you have a valid HuggingFace token
3. Check you have enough disk space (~13.5GB)
4. Check internet connection for first-time download

### Out of Memory

For large models on limited RAM:

1. Use CodeGen only (smaller model)
2. Add swap space
3. Use a machine with more RAM (16GB+ recommended for LLaMA-2)

## Performance

Expected inference times (CPU):

- **CodeGen**: 5-30 seconds per generation
- **LLaMA-2**: 30-120 seconds per generation

With GPU (AMD RX 6800XT):

- **CodeGen**: 1-5 seconds per generation
- **LLaMA-2**: 5-20 seconds per generation

## Configuration

Edit `config/models.json` to customize:

```json
{
  "codegen": {
    "model_path": "Salesforce/codegen-350M-mono",
    "device": "cpu",  // or "cuda" for GPU
    "max_length": 512,
    "temperature": 0.7
  },
  "llm": {
    "model_path": "meta-llama/Llama-2-7b-chat-hf",
    "device": "cpu",
    "max_length": 2048,
    "temperature": 0.8
  }
}
```

## Alternative Models

You can use other compatible models by changing the `model_path` in config:

### Smaller LLM Alternatives

- `microsoft/phi-2` (2.7B parameters, ~5GB)
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (1.1B parameters, ~2GB)

### Larger CodeGen Alternatives

- `Salesforce/codegen-2B-mono` (2B parameters, ~8GB)
- `Salesforce/codegen-6B-mono` (6B parameters, ~24GB)

Just update `config/models.json` with the new model path.
