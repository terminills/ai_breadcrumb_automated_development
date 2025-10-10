# AMD ROCm Setup Guide

This document describes the new `--amd` flag feature for automatic ROCm-compatible PyTorch installation.

## Problem

The previous setup installed generic PyTorch which is not compatible with AMD Instinct GPUs (MI25, MI60, etc.). Users with ROCm-enabled AMD GPUs needed to manually install the correct PyTorch version from the AMD repository.

## Solution

The setup scripts now include an `--amd` flag that:
- Automatically detects your ROCm version
- Installs the correct PyTorch version from the AMD ROCm repository
- Ensures compatibility with AMD Instinct GPUs

## Usage

### Quick Setup (Recommended)

For AMD GPU users:
```bash
./scripts/quickstart.sh --amd
```

For generic systems (CPU/CUDA):
```bash
./scripts/quickstart.sh
```

### Manual Setup

Install just the dependencies:
```bash
# For AMD ROCm systems:
./scripts/setup.sh --amd

# For generic systems:
./scripts/setup.sh
```

## ROCm Detection

The setup script automatically detects ROCm version using multiple methods:

1. **rocminfo command** - Queries the ROCm runtime
2. **Version files** - Checks `/opt/rocm/.info/version`
3. **Package managers** - Queries dpkg/rpm for ROCm packages

Example detection output:
```
AMD ROCm mode enabled

Detecting ROCm version...
✓ Detected ROCm version: 5.7

✓ ROCm 5.7 is supported by PyTorch

Installing PyTorch 2.3.1 with ROCm 5.7 support...
```

## Supported ROCm Versions

The script supports the following ROCm versions:
- ROCm 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
- ROCm 6.0, 6.1

For other versions, the script will attempt installation but may require manual intervention.

## Supported Hardware

This feature is designed for AMD Instinct GPUs including:
- AMD Instinct MI25 (gfx900)
- AMD Instinct MI60 (gfx906)
- Other ROCm-compatible AMD GPUs

## Troubleshooting

### ROCm Not Detected

If ROCm is not detected, ensure:
1. ROCm is installed: `rocminfo` should work
2. ROCm is in your PATH: `which rocminfo`
3. Version files exist: `cat /opt/rocm/.info/version`

### Manual Installation

If automatic detection fails, you can install manually:
```bash
# Determine your ROCm version
rocminfo | grep "Runtime Version"

# Install PyTorch manually (example for ROCm 5.7)
pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### Verify Installation

After installation, verify PyTorch detects ROCm:
```bash
python3 -c "import torch; print('ROCm available:', hasattr(torch.version, 'hip'))"
```

## Testing

Run the test suite to verify the setup:
```bash
./scripts/test_setup.sh
```

This validates:
- Script syntax and permissions
- ROCm version parsing logic
- Documentation completeness
- Supported version list

## Examples

### Example 1: Fresh Installation on ROCm System

```bash
git clone <repository_url>
cd ai_breadcrumb_automated_development
./scripts/quickstart.sh --amd
```

The script will:
1. Detect Python and Git
2. Detect ROCm version (e.g., 5.7.1)
3. Install dependencies
4. Install PyTorch 2.3.1 with ROCm 5.7 support
5. Offer to start the monitoring UI

### Example 2: Manual Dependency Installation

```bash
# Install only dependencies (no UI startup)
./scripts/setup.sh --amd

# Then proceed with other steps
./scripts/clone_aros.sh
cd ui && python app.py
```

## Migration from Old Setup

If you previously installed with `pip install -r requirements.txt`, you can upgrade:

```bash
# Uninstall existing PyTorch
pip uninstall torch torchvision torchaudio

# Reinstall with ROCm support
./scripts/setup.sh --amd
```

## References

- [PyTorch ROCm Installation](https://pytorch.org/get-started/locally/)
- [AMD ROCm Documentation](https://rocmdocs.amd.com/)
- [AMD Instinct GPUs](https://www.amd.com/en/products/server-accelerators/instinct-mi25.html)
