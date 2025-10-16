# AI Model Setup Guide

## Overview

The AROS-Cognito system uses two AI models for intelligent code generation and analysis:

1. **CodeGen** - For code generation (Salesforce/codegen-350M-mono, ~350MB)
2. **LLaMA-2** - For reasoning and exploration (meta-llama/Llama-2-7b-chat-hf, ~13GB)

## Important: Models Are Required

**The system will NOT work without AI models installed.** When models are missing, you'll see clear error messages with installation instructions.

### What Happens Without Models

When you try to run the system without models, you'll get a helpful error message like:

```
╔══════════════════════════════════════════════════════════════════╗
║  AI MODEL NOT FOUND                                              ║
╚══════════════════════════════════════════════════════════════════╝

Failed to load codegen model: ...

PROBLEM:
  The AI model files are not downloaded.

SOLUTION:
  Download the required models using:
  
  $ python3 scripts/download_models.py --codegen
```

**This is intentional.** The system tells you exactly what's wrong and how to fix it.

## Installation Options

### Option 1: Install CodeGen Only (Lightweight)

For basic code generation with a small model (~350MB):

```bash
python3 scripts/download_models.py --codegen
```

### Option 2: Install Full AI Stack (Recommended)

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
# Download all models
python3 scripts/download_models.py --all --token YOUR_HF_TOKEN
```

### Option 3: Testing Mode (Mock Models)

For testing the system without downloading models, you can use mock mode:

```bash
# Use mock models explicitly (template-based responses only)
python3 src/copilot_iteration.py --use-mock --project test

# Or in Python code:
loader = LocalModelLoader()
model = loader.load_model('codegen', use_mock=True)
```

**Note:** Mock mode only provides template-based responses. It's useful for:
- Testing system logic
- Developing new features
- Running in CI/CD pipelines

**It is NOT a replacement for real AI models.**

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
