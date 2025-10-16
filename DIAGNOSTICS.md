# System Diagnostics

The system now includes comprehensive diagnostics to help identify issues with PyTorch, CUDA, ROCm, and AI models.

## Features

### 1. Command-Line Diagnostics

Run comprehensive system diagnostics from the command line:

```bash
python3 scripts/check_system_diagnostics.py
```

This will check:
- Python version and environment
- PyTorch installation and CUDA/ROCm availability
- Transformers library
- GPU drivers (NVIDIA/AMD)
- Disk space
- AI model installation status
- Required Python packages

**Export to JSON:**
```bash
python3 scripts/check_system_diagnostics.py --json diagnostics.json
```

**Quiet mode (JSON only):**
```bash
python3 scripts/check_system_diagnostics.py --json diagnostics.json --quiet
```

### 2. Enhanced Model Download Script

The `download_models.py` script now shows detailed diagnostics:

```bash
python3 scripts/download_models.py --check
```

When PyTorch is installed, it shows:
- PyTorch version
- CUDA availability and version
- GPU count and details
- ROCm availability and version
- Transformers version

### 3. Web UI Diagnostics

The web UI now includes a "System Diagnostics" button in the System Status card.

**To access:**
1. Start the web UI: `./start_ui.sh`
2. Open http://localhost:5000
3. Click "🔍 System Diagnostics" button in the System Status card

The diagnostics modal shows:
- Python environment
- PyTorch status (version, CUDA, ROCm, GPUs)
- AI models installation status
- Disk space
- Required packages status

**Export feature:**
- Click "Export JSON" to download diagnostics as a JSON file

### 4. API Endpoint

Programmatic access to diagnostics:

```bash
curl http://localhost:5000/api/diagnostics
```

Returns JSON with complete diagnostic information.

## Common Issues and Solutions

### PyTorch Not Installed

**Symptoms:**
```
❌ PyTorch is not installed
Error: No module named 'torch'
```

**Solution:**
```bash
pip install torch transformers
```

### PyTorch Installed but No GPU

**Symptoms:**
```
✓ PyTorch: v2.3.1
CUDA Available: No (CPU only)
```

**Possible Causes:**
1. No GPU in the system
2. CUDA drivers not installed
3. PyTorch CPU-only version installed

**Solutions:**
- Install NVIDIA drivers and CUDA toolkit
- For AMD GPUs, install ROCm
- Reinstall PyTorch with GPU support

### Models Not Downloaded

**Symptoms:**
```
✗ CodeGen: Not installed
✗ LLaMA-2: Not installed
```

**Solution:**
```bash
python3 scripts/download_models.py --codegen
```

### Low Disk Space

**Symptoms:**
```
⚠️ Low disk space (< 15GB free)
```

**Requirements:**
- CodeGen: ~350MB
- LLaMA-2: ~13GB
- Recommended: At least 15GB free space

**Solutions:**
1. Free up disk space
2. Use external storage
3. Use mock models for testing: `--use-mock` flag

### Missing Packages

**Symptoms:**
```
⚠️ 5 required packages missing
Missing packages:
  - flask
  - GitPython
  - psutil
```

**Solution:**
```bash
pip install flask GitPython psutil pyyaml tqdm
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Diagnostic Information in Error Messages

When model loading fails, you'll now see detailed diagnostic information:

```
╔══════════════════════════════════════════════════════════════════╗
║  AI MODEL DEPENDENCY ERROR                                       ║
╚══════════════════════════════════════════════════════════════════╝

Failed to load codegen model: No module named 'torch'

DIAGNOSTIC INFORMATION:
  PyTorch: Not installed ✗
  Transformers: Not installed ✗
  Disk Space: 42.3GB free
  CodeGen Model: Not downloaded ✗
  LLaMA-2 Model: Not downloaded ✗

PROBLEM:
  Required Python packages are not installed or have compatibility issues.

SOLUTION:
  1. Run system diagnostics:
     $ python3 scripts/check_system_diagnostics.py
  
  2. Install the required dependencies:
     $ pip install torch transformers
  
  3. Or use the setup script:
     $ ./scripts/setup.sh
```

## Integration Points

The diagnostics are integrated into:

1. **Model Loader** (`src/local_models/model_loader.py`)
   - Shows diagnostics in error messages
   - Provides actionable solutions

2. **Download Script** (`scripts/download_models.py`)
   - Enhanced dependency checking
   - Shows PyTorch and GPU information

3. **Web UI** (`ui/app.py` and `ui/templates/index.html`)
   - `/api/diagnostics` endpoint
   - Interactive diagnostics modal
   - Export functionality

4. **Standalone Script** (`scripts/check_system_diagnostics.py`)
   - Comprehensive system check
   - JSON export
   - Exit codes for automation

## Exit Codes

The diagnostics script returns:
- `0`: Success (PyTorch installed)
- `1`: Critical issue (PyTorch not installed)

Use in scripts:
```bash
if python3 scripts/check_system_diagnostics.py --quiet; then
    echo "System ready"
else
    echo "System has issues"
fi
```

## Troubleshooting Guide

For detailed troubleshooting, see:
- `AI_MODEL_SETUP.md` - AI model setup guide
- `PYTORCH_INSTALLATION.md` - PyTorch installation guide
- `BOOTSTRAP_TROUBLESHOOTING.md` - Bootstrap issues

## Future Enhancements

Potential improvements:
- Real-time monitoring of GPU usage
- Automatic dependency installation
- Compatibility checks for different PyTorch versions
- Performance benchmarks
- Network connectivity tests
- Model download progress tracking
