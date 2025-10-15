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
1. Verify ROCm installation:
   ```bash
   rocminfo
   /opt/rocm/bin/rocminfo
   ```

2. Check ROCm version:
   ```bash
   cat /opt/rocm/.info/version
   ```

3. Install ROCm 5.7.1:
   - Visit: https://rocmdocs.amd.com/
   - Follow Ubuntu 22.04.3 instructions

4. Continue without ROCm:
   - Script will use CPU-only PyTorch
   - Full functionality available
   - Training will be slower

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
   - MI25 (gfx900) ✓
   - MI60 (gfx906) ✓
   - Other gfx9xx ✓

3. Check GPU permissions:
   ```bash
   ls -l /dev/kfd
   groups  # Should include 'render' or 'video'
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
   # For ROCm 5.7
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
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
