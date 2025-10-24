# Bootstrap Troubleshooting Guide

## Common Issues and Solutions

### GitHub Token Issues

#### Problem: "Authentication failed"
**Symptoms:**
```
Error: Authentication failed
Failed to clone repository
```

**Solutions:**
1. Check token permissions:
   - Visit https://github.com/settings/tokens
   - Verify token has 'repo' scope
   - Token should not be expired

2. Reset token:
   ```bash
   rm ~/.aros_github_token
   export GITHUB_TOKEN="your_new_token"
   ./scripts/bootstrap_ubuntu.sh
   ```

3. Manual token entry:
   ```bash
   unset GITHUB_TOKEN
   ./scripts/bootstrap_ubuntu.sh
   # Enter token when prompted
   ```

### ROCm Issues

#### Problem: "ROCm not detected"
**Symptoms:**
```
⚠ ROCm not detected or not properly installed
```

**Solutions:**
1. **Use automatic installation (Ubuntu 22.04.3 only)**:
   - The bootstrap script will offer to install ROCm 7.0.2 automatically
   - Answer 'y' when prompted: "Install ROCm 7.0.2? (y/n)"
   - Installation handles DKMS compatibility issues automatically

2. Verify ROCm installation:
   ```bash
   rocminfo
   /opt/rocm/bin/rocminfo
   ```

3. Check ROCm version:
   ```bash
   cat /opt/rocm/.info/version
   ```

4. Manual ROCm 7.0.2 installation:
   - Visit: https://rocmdocs.amd.com/
   - Follow Ubuntu 22.04.3 instructions

5. Special handling for ROCm 7.0:
   - PyTorch 2.9.0+rocm7.0 will be installed from official PyTorch repository
   - torchvision and torchaudio will be installed with ROCm 7.0 support
   - Compatible with Python 3.8+

6. Continue without ROCm:
   - Script will use CPU-only PyTorch
   - Full functionality available
   - Training will be slower

#### Problem: "DKMS module installation failed" or "rocminfo shows version 1.1"
**Symptoms:**
```
DKMS module installation failed
amdgpu module version shows 1.1 instead of 5.7.1
```

**Explanation:**
Ubuntu 22.04.3 has compatibility issues with DKMS modules from newer ROCm packages. The bootstrap script addresses this by:
- Installing ROCm 7.0.2 without DKMS drivers
- Using the kernel's built-in amdgpu driver
- The kernel module may show version 1.1, but this is expected and correct
- ROCm 7.0.2 userspace tools and libraries are fully functional

**Solutions:**
1. **Automatic fix (recommended)**:
   - Run the bootstrap script: `./scripts/bootstrap_ubuntu.sh`
   - When prompted, choose to install ROCm 7.0.2
   - Script installs ROCm without DKMS automatically

2. Verify ROCm is working despite version mismatch:
   ```bash
   rocminfo | grep "Runtime Version"  # Should show 5.7.x
   cat /opt/rocm/.info/version        # Should show 5.7.1
   rocm-smi                           # Should detect GPU
   ```

3. Manual installation without DKMS:
   ```bash
   # Add ROCm repository
   wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
   echo "deb [arch=amd64] https://repo.radeon.com/rocm/apt/5.7.1 ubuntu main" | sudo tee /etc/apt/sources.list.d/rocm.list
   sudo apt update
   
   # Install ROCm without DKMS
   sudo apt install -y rocm-dev rocm-libs rocm-utils rocminfo rocm-smi hip-runtime-amd hip-dev
   
   # Add user to groups
   sudo usermod -a -G video,render $USER
   ```

4. After installation:
   - Log out and back in for group changes
   - Verify with: `rocminfo` and `rocm-smi`
   - The kernel module version (1.1) is expected and does not affect functionality

#### Problem: "No compatible AMD GPU detected"
**Symptoms:**
```
⚠ No compatible AMD GPU detected
```

**Solutions:**
1. Check GPU detection:
   ```bash
   rocminfo | grep gfx
   lspci | grep VGA
   ```

2. Verify GPU support:
   - Radeon Pro V620 (gfx1030) ✓
   - Radeon Pro V620 (gfx1030) ✓
   - Other gfx9xx ✓

3. Check GPU permissions:
   ```bash
   ls -l /dev/kfd
   groups  # Should include 'render' or 'video'
   ```

### PyTorch Installation Issues

#### Problem: "Cannot uninstall distutils-installed-package"
**Symptoms:**
```
error: uninstall-distutils-installed-package
× Cannot uninstall blinker 1.4
╰─> It is a distutils installed project...
```

**Solutions:**
1. The bootstrap script now handles this automatically with `--ignore-installed` flag
2. If running setup.sh manually with AMD flag:
   ```bash
   ./scripts/setup.sh --amd
   ```

3. Manual workaround if needed:
   ```bash
   pip install --ignore-installed [package-name]
   ```

#### Problem: "PyTorch ROCm version mismatch"
**Symptoms:**
```
⚠ Warning: Python 3.x detected, but AMD ROCm 7.0 wheels are built for Python 3.10
```

**Solutions:**
1. Install Python 3.10 for ROCm 7.0.2:
   ```bash
   sudo apt-get install python3.10 python3.10-venv python3.10-dev
   ```

2. Create virtual environment with Python 3.10:
   ```bash
   python3.10 -m venv venv_torch_rocm
   source venv_torch_rocm/bin/activate
   ./scripts/bootstrap_ubuntu.sh
   ```

3. Script will fallback to standard PyTorch installation if Python version doesn't match

#### Problem: "PyTorch installation fails"
**Symptoms:**
```
❌ Failed to install PyTorch with ROCm support
```

**Solutions:**
1. Check internet connectivity:
   ```bash
   ping -c 3 repo.radeon.com
   curl -I https://repo.radeon.com/rocm/manylinux/rocm-rel-5.7/
   ```

2. Manual installation for ROCm 7.0:
   ```bash
   pip install torch==2.9.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.0
   ```

3. Alternative - try without specifying version:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.0
   ```

### Database Issues

#### Problem: "Database migration failed"
**Symptoms:**
```
❌ Database migration failed
```

**Solutions:**
1. Check disk space:
   ```bash
   df -h .
   ```

2. Check permissions:
   ```bash
   ls -ld logs/
   chmod 755 logs/
   ```

3. Manual migration:
   ```bash
   ./scripts/migrate_database.sh
   ```

4. Clean restart:
   ```bash
   rm -rf logs/
   ./scripts/migrate_database.sh
   ```

#### Problem: "Invalid JSON in database"
**Symptoms:**
```
⚠ Error database: Invalid JSON, reinitializing...
```

**Solutions:**
1. Let script repair:
   - Script will automatically recreate
   - Backups are in `logs/backups/`

2. Manual validation:
   ```bash
   python3 -m json.tool logs/errors/error_database.json
   ```

3. Restore from backup:
   ```bash
   cp logs/backups/LATEST/error_database.json logs/errors/
   ```

### Network Access Issues

#### Problem: "UI not accessible from network"
**Symptoms:**
- Can access http://localhost:5000
- Cannot access http://192.168.x.x:5000

**Solutions:**
1. Check UI configuration:
   ```bash
   grep '"host"' config/config.json
   # Should show: "host": "0.0.0.0"
   ```

2. Check firewall:
   ```bash
   sudo ufw status
   sudo ufw allow 5000/tcp
   ```

3. Check network binding:
   ```bash
   netstat -tlnp | grep 5000
   # Should show: 0.0.0.0:5000
   ```

4. Restart UI:
   ```bash
   pkill -f "python.*app.py"
   ./start_ui.sh
   ```

#### Problem: "Port 5000 already in use"
**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Solutions:**
1. Find conflicting process:
   ```bash
   lsof -i :5000
   ```

2. Kill conflicting process:
   ```bash
   pkill -f "python.*5000"
   ```

3. Change port in config:
   ```json
   {
     "ui": {
       "port": 5001
     }
   }
   ```

### Repository Issues

#### Problem: "Repository already exists"
**Symptoms:**
```
fatal: destination path 'aros-src' already exists
```

**Solutions:**
1. Use existing repo:
   - Bootstrap will skip cloning
   - Repo will be used as-is

2. Start fresh:
   ```bash
   rm -rf aros-src/
   ./scripts/bootstrap_ubuntu.sh
   ```

3. Update existing:
   ```bash
   cd aros-src
   git fetch --all
   git pull origin master
   ```

#### Problem: "Upstream not configured"
**Symptoms:**
```
fatal: 'upstream' does not appear to be a git repository
```

**Solutions:**
1. Add upstream manually:
   ```bash
   cd aros-src
   git remote add upstream https://github.com/aros-development-team/AROS.git
   git fetch upstream
   ```

2. Verify remotes:
   ```bash
   cd aros-src
   git remote -v
   # Should show both 'origin' and 'upstream'
   ```

### Installation Issues

#### Problem: "Python dependencies failed to install"
**Symptoms:**
```
ERROR: Could not install packages
```

**Solutions:**
1. Update pip:
   ```bash
   python3 -m pip install --upgrade pip
   ```

2. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev build-essential
   ```

3. Manual install:
   ```bash
   pip install -r requirements.txt
   ```

4. Use virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Problem: "PyTorch installation failed"
**Symptoms:**
```
❌ Failed to install PyTorch with ROCm support
```

**Solutions:**
1. Check ROCm version:
   ```bash
   rocminfo | grep Version
   ```

2. Manual PyTorch install:
   ```bash
   # For ROCm 7.0
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.0
   ```

3. CPU-only fallback:
   ```bash
   pip install torch torchvision torchaudio
   ```

### Permission Issues

#### Problem: "Permission denied"
**Symptoms:**
```
bash: ./scripts/bootstrap_ubuntu.sh: Permission denied
```

**Solutions:**
1. Make executable:
   ```bash
   chmod +x scripts/*.sh
   ```

2. Run with bash:
   ```bash
   bash scripts/bootstrap_ubuntu.sh
   ```

## Testing Issues

#### Problem: "Test suite fails"
**Symptoms:**
```
✗ Some tests failed
```

**Solutions:**
1. Check specific failures:
   ```bash
   ./scripts/test_bootstrap.sh
   # Review which tests failed
   ```

2. Fix individual issues:
   - Follow error messages
   - Apply solutions from above

3. Re-run after fixes:
   ```bash
   ./scripts/test_bootstrap.sh
   ```

## Advanced Troubleshooting

### Enable Debug Mode

1. Bootstrap script:
   ```bash
   bash -x scripts/bootstrap_ubuntu.sh 2>&1 | tee bootstrap_debug.log
   ```

2. Migration script:
   ```bash
   bash -x scripts/migrate_database.sh 2>&1 | tee migration_debug.log
   ```

3. UI app:
   ```python
   # In ui/app.py, change:
   app.run(host=host, port=port, debug=True)
   ```

### Check System Requirements

```bash
# OS version
cat /etc/os-release

# Python version
python3 --version  # Should be 3.8+

# Disk space
df -h .  # Should have 20GB+

# Memory
free -h

# ROCm
rocminfo | head -20

# GPU
lspci | grep -i vga
```

### Collect Diagnostic Information

```bash
# Create diagnostic report
cat > diagnostic_report.txt << EOF
OS: $(cat /etc/os-release | grep PRETTY_NAME)
Python: $(python3 --version)
Disk: $(df -h . | tail -1)
ROCm: $(rocminfo 2>/dev/null | grep Version | head -1 || echo "Not installed")
GPU: $(lspci | grep -i vga)
EOF

cat diagnostic_report.txt
```

## Getting Help

### Before Reporting Issues

1. Run test suite:
   ```bash
   ./scripts/test_bootstrap.sh
   ```

2. Check logs:
   ```bash
   ls -lh logs/
   cat logs/errors/error_database.json
   ```

3. Verify configuration:
   ```bash
   cat config/config.json
   python3 -m json.tool config/config.json
   ```

### When Reporting Issues

Include:
1. OS version: `cat /etc/os-release`
2. Test results: `./scripts/test_bootstrap.sh`
3. Error messages: Copy exact error text
4. ROCm version: `rocminfo | head`
5. Python version: `python3 --version`
6. Disk space: `df -h .`

## Quick Reset

Complete system reset (⚠️ Destroys all data):

```bash
# Backup first!
tar czf backup.tar.gz logs/ models/ aros-src/

# Clean everything
rm -rf logs/ models/ aros-src/
rm ~/.aros_github_token

# Re-bootstrap
./scripts/bootstrap_ubuntu.sh
```

## Still Having Issues?

1. Check documentation:
   - `SETUP.md` - Setup guide
   - `BOOTSTRAP_QUICKREF.md` - Quick reference
   - `BOOTSTRAP_IMPLEMENTATION.md` - Implementation details

2. Review scripts:
   - `scripts/bootstrap_ubuntu.sh` - Main script
   - `scripts/migrate_database.sh` - Migration script

3. Check test results:
   ```bash
   ./scripts/test_bootstrap.sh
   ```

4. Enable debug mode and collect logs
