# Ubuntu 22.04.3 Bootstrap Quick Reference

## One-Command Setup

```bash
./scripts/bootstrap_ubuntu.sh
```

## What Gets Set Up

### 1. System Dependencies ✓
- Build tools (gcc, make, etc.)
- Python 3 and pip
- Git
- Required libraries

### 2. ROCm Validation ✓
- Detects ROCm 5.7.1
- Validates AMD GPU (MI25, MI60, etc.)
- Falls back to CPU mode if not available

### 3. GitHub Integration ✓
- Prompts for GitHub token (first run only)
- Saves token securely to `~/.aros_github_token`
- Clones `terminills/AROS-OLD` (private)
- Configures `aros-development-team/AROS` as upstream

### 4. Database Schema ✓
- Initializes JSON databases
- Creates schema version tracking
- Sets up automatic backups
- Validates on every run

### 5. Python Environment ✓
- Installs PyTorch with ROCm support
- Installs all dependencies
- Validates installation

### 6. Network UI ✓
- Configures UI to bind on `0.0.0.0:5000`
- Accessible from local network
- Creates convenience startup script

## After Bootstrap

### Start the UI
```bash
./start_ui.sh
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
