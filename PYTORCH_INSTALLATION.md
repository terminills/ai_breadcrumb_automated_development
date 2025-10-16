# PyTorch 2.3.1 Installation Guide

## Overview

This project requires PyTorch 2.3.1 for AI model-based iteration and code generation. However, the UI and session management can be tested in **demo mode** without PyTorch installed.

## Demo Mode (No PyTorch Required)

For testing the UI and session flow without installing PyTorch:

1. Start the UI:
   ```bash
   cd ui && python app.py
   ```

2. Create a session with **Demo Mode** enabled:
   - Go to http://localhost:5000/sessions
   - Fill in task description
   - Check "Demo Mode" checkbox
   - Click "Create Session"

3. Watch the simulated progress at:
   - Sessions page: http://localhost:5000/sessions
   - Main dashboard: http://localhost:5000/

Demo mode simulates iteration progress through exploration, reasoning, generation, review, and compilation phases without requiring actual AI models.

## Installing PyTorch 2.3.1

### For CPU-only systems:

```bash
pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### For NVIDIA CUDA systems:

```bash
# CUDA 11.8
pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### For AMD ROCm systems (MI25, MI60, etc.):

This project is tested with ROCm 5.7.x (specifically 5.7.1). PyTorch 2.3.1 with ROCm support:

```bash
# ROCm 5.7.x (including 5.7.1)
pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

**Note:** AMD GPU support requires ROCm to be installed separately. See [ROCm Installation Guide](https://rocmdocs.amd.com/en/latest/Installation_Guide/Installation-Guide.html)

### Using the Bootstrap Script (Recommended for AMD):

The project includes an automated bootstrap script that handles PyTorch installation:

```bash
./scripts/bootstrap_ubuntu.sh
```

This script:
- Detects your ROCm version automatically
- Installs PyTorch 2.3.1+ with appropriate ROCm support
- Sets up virtual environment in `~/cognito-envs/ai_breadcrumb/`
- Configures all dependencies

## Verification

After installation, verify PyTorch is working:

```bash
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}'); print(f'ROCm: {torch.version.hip if hasattr(torch.version, \"hip\") else \"N/A\"}')"
```

Expected output:
```
PyTorch: 2.3.1+cu118  # or rocm5.7, cpu, etc.
CUDA: True  # or False for CPU/ROCm
ROCm: 5.7.1  # or N/A for non-ROCm
```

## Using Real Models

Once PyTorch is installed, disable demo mode when creating sessions:

1. Go to http://localhost:5000/sessions
2. Fill in task description
3. **Uncheck** "Demo Mode" checkbox
4. Click "Create Session"

The system will use the actual AI models for:
- Code exploration
- Reasoning and planning
- Code generation
- Self-review
- Compilation and testing

## Model Configuration

Models are configured in `config/models.json`. The default setup uses:

- **Codegen Model**: Salesforce CodeGen (350M-6B params)
- **LLM**: Llama 2, Mistral, or CodeLlama (7B-13B params)

To use specific models, edit `config/models.json` or run training:

```bash
./scripts/train_model.sh --data aros-src --output models/aros-v1.3
```

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'torch'

**Solution:** Install PyTorch following the instructions above.

### Issue: CUDA/ROCm not detected

**Solution:** 
1. Verify GPU drivers are installed
2. For NVIDIA: Install CUDA toolkit
3. For AMD: Install ROCm following AMD's guide
4. Reinstall PyTorch with appropriate index URL

### Issue: Out of memory during model loading

**Solution:**
1. Use smaller models (e.g., 350M instead of 6B params)
2. Reduce batch size in `config/config.json`
3. Use CPU if GPU memory is insufficient (slower but works)

### Issue: Session fails to start (non-demo mode)

**Solution:**
1. Ensure AROS repository is cloned
2. Check `scripts/run_copilot_iteration.sh` exists
3. Verify PyTorch is installed correctly
4. Check logs in `logs/` directory for errors
5. Try demo mode first to verify UI is working

## Additional Resources

- [PyTorch Official Documentation](https://pytorch.org/docs/stable/index.html)
- [ROCm Documentation](https://rocmdocs.amd.com/)
- [Project README](README.md)
- [Setup Guide](SETUP.md)
