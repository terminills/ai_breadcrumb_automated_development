# Bootstrap Ubuntu Script Update - Virtual Environment Support

## Summary

Updated the bootstrap Ubuntu script and related files to use a Python virtual environment instead of system-wide package installation, and to run as a regular user instead of requiring root access.

## Changes Made

### 1. bootstrap_ubuntu.sh
- **No longer requires root**: Script now runs as a regular user
- **Uses sudo explicitly**: System package installations use `sudo` command directly (prompts for password)
- **Virtual environment**: Creates and uses a Python venv in `venv/` directory
- **Python packages in venv**: All Python package installations happen within the venv
- **PyTorch 2.3.1+**: Uses PyTorch 2.3.1 from requirements.txt (except ROCm 5.7.1 systems)

Key changes:
- Added `VENV_DIR` variable pointing to `$PROJECT_ROOT/venv`
- Removed root/EUID checks that prevented running as regular user
- Updated `install_system_dependencies()` to use `sudo` directly
- Updated `install_rocm_5_7_1()` to use `sudo` directly
- Modified `setup_python_env()` to create and activate venv
- Updated all Python package installations to use venv's pip
- Modified verification to use venv's python

### 2. start_ui.sh
- **Automatic venv activation**: Detects and activates venv if it exists
- **Graceful fallback**: Falls back to system Python if venv doesn't exist
- **User guidance**: Provides helpful messages about venv status

Key changes:
- Added `VENV_DIR` variable
- Added venv detection and activation logic at startup
- Uses `python` when in venv, `python3` otherwise
- Shows clear status messages about venv activation

### 3. setup.sh
- **Venv compatibility**: Works correctly whether run in venv or system context
- **PyTorch version**: Updated comments to clarify version usage (2.3.1+ generic, 2.0.1 for ROCm 5.7.1)

Key changes:
- Updated Python command detection to work with venv
- Fixed `install_pytorch_generic()` comment about PyTorch version
- Updated verification to use correct Python command

### 4. .gitignore
- Added `ai_env/` to ignored directories (in addition to existing `venv/`)

### 5. Documentation Updates

#### README.md
- Updated bootstrap section to mention running as regular user
- Added note about sudo password prompt
- Clarified PyTorch version usage
- Updated start_ui.sh documentation

#### SETUP.md
- Added virtual environment to setup steps
- Clarified sudo usage
- Updated manual activation instructions
- Fixed typo: "migrated" → "migrates"

#### BOOTSTRAP_QUICKREF.md
- Added virtual environment section
- Reorganized steps to include venv setup
- Added manual activation instructions
- Updated all Python package references

## Benefits

1. **Better isolation**: Dependencies are isolated from system Python
2. **Compatible with AI tools**: Works with AI downloader scripts that expect isolated environments
3. **Safer**: No system-wide package modifications (except system packages via sudo)
4. **Cleaner**: Easier to remove/recreate environment by deleting venv directory
5. **User-friendly**: Runs as regular user, prompts for sudo only when needed
6. **Up-to-date PyTorch**: Uses PyTorch 2.3.1+ with better support and features

## Usage

### Bootstrap (first time setup)
```bash
# Run as regular user
./scripts/bootstrap_ubuntu.sh
```

You'll be prompted for:
1. Sudo password (for system package installation)
2. GitHub token (for private repo access)
3. ROCm installation (if not present)

### Starting the UI
```bash
# Automatically activates venv
./start_ui.sh
```

### Manual venv activation
```bash
# Activate venv manually
source venv/bin/activate

# Now you can run any Python scripts
python ui/app.py
```

## Testing

All existing tests pass:
- Bootstrap script syntax validation ✓
- Database migration tests ✓
- Configuration validation ✓
- Script executable checks ✓

New functionality tested:
- Virtual environment creation ✓
- Venv activation in start_ui.sh ✓
- Python command detection ✓

## Compatibility Notes

- **ROCm 5.7.1**: Still uses PyTorch 2.0.1 for compatibility with ROCm 5.7.1 wheels
- **Other systems**: Use PyTorch 2.3.1+ from requirements.txt
- **Backward compatible**: Script detects if venv doesn't exist and provides helpful messages

## Migration Path

For existing installations:
1. The scripts detect if venv exists
2. If not, they fall back gracefully or prompt to run bootstrap
3. Old system-wide installations continue to work
4. Run `./scripts/bootstrap_ubuntu.sh` to create venv-based setup

## Files Modified

- scripts/bootstrap_ubuntu.sh
- scripts/setup.sh
- start_ui.sh
- .gitignore
- README.md
- SETUP.md
- BOOTSTRAP_QUICKREF.md
