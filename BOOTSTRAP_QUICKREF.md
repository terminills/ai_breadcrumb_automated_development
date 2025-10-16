# Ubuntu 22.04.3 Bootstrap Quick Reference

## One-Command Setup

```bash
# Run as regular user (not root)
./scripts/bootstrap_ubuntu.sh
```

**Interactive Setup**: The script will ask once if you want to install system packages.

## What Gets Set Up

### 1. Permission Check ✓
- Asks once about system package installation
- Choose Yes for sudo operations or No to skip

### 2. System Dependencies ✓
- Build tools (gcc, make, etc.) - installed via sudo (if requested)
- Python 3 and pip
- Python venv support
- Git
- Required libraries

### 3. Python Virtual Environment ✓
- Creates venv in `~/cognito-envs/ai_breadcrumb/`
- Isolates dependencies from system Python
- Automatically activated during setup
- Configurable via `VENV_BASE` environment variable

### 4. ROCm Validation ✓
- Detects ROCm 5.7.1
- Validates AMD GPU (MI25, MI60, etc.)
- Falls back to CPU mode if not available
- ROCm installed via sudo if needed (and if user chose system packages)

### 5. GitHub Integration ✓
- Prompts for GitHub token (first run only)
- Saves token securely to `~/.aros_github_token`
- Clones `terminills/AROS-OLD` (private)
- Configures `aros-development-team/AROS` as upstream

### 6. Database Schema ✓
- Initializes JSON databases
- Creates schema version tracking
- Sets up automatic backups
- Validates on every run

### 7. Python Dependencies ✓
- Installs PyTorch 2.3.1+ (or 2.0.1 for ROCm 5.7.1)
- Installs all dependencies in venv
- Validates installation

### 8. Network UI ✓
- Configures UI to bind on `0.0.0.0:5000`
- Accessible from local network
- Works with venv setup

## After Bootstrap

### Start the UI
```bash
./start_ui.sh  # Automatically activates venv
```

### Manual Activation
```bash
source ~/cognito-envs/ai_breadcrumb/bin/activate
cd ui && python app.py
```

### Environment Variables
```bash
# Use custom venv location
VENV_BASE=/custom/path ./scripts/bootstrap_ubuntu.sh
VENV_BASE=/custom/path ./start_ui.sh
```

Access at:
- Local: http://localhost:5000
- Network: http://YOUR_IP:5000

### Sync Upstream
```bash
./scripts/update_and_verify.sh
```

### Train Model (requires GPU)
```bash
./scripts/train_model.sh
```

### Run AI Agent
```bash
./scripts/run_ai_agent.sh ITERATE radeonsi 10
```

## Database Management

### Manual Migration
```bash
./scripts/migrate_database.sh
```

### Database Locations
- `logs/errors/error_database.json` - Error tracking
- `logs/reasoning/reasoning_database.json` - AI reasoning
- `logs/training/training_state.json` - Training progress
- `logs/compile/compile_state.json` - Compilation stats

### Backups
Automatic backups in: `logs/backups/YYYYMMDD_HHMMSS/`

## Troubleshooting

### Token Issues
```bash
# Reset token
rm ~/.aros_github_token
./scripts/bootstrap_ubuntu.sh
```

### Database Issues
```bash
# Force migration
./scripts/migrate_database.sh
```

### UI Not Accessible on Network
Check firewall:
```bash
sudo ufw allow 5000/tcp
```

Check binding:
```bash
grep '"host"' config/config.json
# Should show: "host": "0.0.0.0"
```

## Testing

Run test suite:
```bash
./scripts/test_bootstrap.sh
```

## Requirements

- Ubuntu 22.04.3 (recommended)
- Python 3.8+
- 20GB+ disk space
- Optional: ROCm 5.7.1 + AMD GPU

## Key Features

✓ **Idempotent**: Safe to run multiple times
✓ **Automatic**: Minimal user interaction
✓ **Network-Ready**: UI accessible on LAN
✓ **Schema-Safe**: Always migrates databases
✓ **Token-Secure**: Encrypted token storage
✓ **Validated**: Comprehensive test suite
