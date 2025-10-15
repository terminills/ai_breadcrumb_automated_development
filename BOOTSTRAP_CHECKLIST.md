# Ubuntu 22.04.3 Bootstrap Checklist

Use this checklist to verify your bootstrap installation.

## Pre-Bootstrap Checklist

- [ ] Ubuntu 22.04.3 installed
- [ ] ROCm 5.7.1 installed (optional, for GPU support)
- [ ] AMD GPU validated (MI25, MI60, etc.) (optional)
- [ ] Internet connection active
- [ ] 20GB+ free disk space
- [ ] Python 3.8+ installed
- [ ] Git installed

## Bootstrap Process Checklist

- [ ] Run bootstrap script: `./scripts/bootstrap_ubuntu.sh`
- [ ] Provided GitHub token when prompted
- [ ] Token saved to `~/.aros_github_token`
- [ ] System dependencies installed
- [ ] ROCm detected (if applicable)
- [ ] GPU validated (if applicable)
- [ ] AROS-OLD repository cloned
- [ ] Upstream remote configured
- [ ] Database schema initialized
- [ ] PyTorch installed (with ROCm or CPU)
- [ ] UI configured for network access
- [ ] Installation verified
- [ ] Startup script created

## Post-Bootstrap Verification

### File Verification
- [ ] `scripts/bootstrap_ubuntu.sh` exists
- [ ] `scripts/migrate_database.sh` exists
- [ ] `scripts/test_bootstrap.sh` exists
- [ ] `start_ui.sh` exists
- [ ] `aros-src/` directory exists
- [ ] `logs/` directory exists with subdirectories
- [ ] `models/` directory exists

### Database Verification
- [ ] `logs/errors/error_database.json` exists
- [ ] `logs/reasoning/reasoning_database.json` exists
- [ ] `logs/training/training_state.json` exists
- [ ] `logs/compile/compile_state.json` exists
- [ ] `logs/.schema_version` contains "1"

### Configuration Verification
- [ ] `config/config.json` exists
- [ ] UI host set to "0.0.0.0"
- [ ] UI port set to 5000 (or custom)

### Repository Verification
- [ ] `aros-src/.git` exists
- [ ] Remote "origin" configured
- [ ] Remote "upstream" configured
- [ ] Can fetch from both remotes

### Test Suite Verification
- [ ] Run: `./scripts/test_bootstrap.sh`
- [ ] All 14 tests pass
- [ ] No errors reported

## UI Startup Verification

- [ ] Run: `./start_ui.sh`
- [ ] Database migration runs automatically
- [ ] UI starts without errors
- [ ] Local URL displayed: http://localhost:5000
- [ ] Network URL displayed: http://YOUR_IP:5000
- [ ] Can access UI locally
- [ ] Can access UI from another device on network

## Functional Verification

### Basic Functionality
- [ ] UI dashboard loads
- [ ] API status endpoint works: `/api/status`
- [ ] Database files are accessible
- [ ] No error messages in console

### Advanced Functionality
- [ ] Can sync with upstream: `./scripts/update_and_verify.sh`
- [ ] Can run migration manually: `./scripts/migrate_database.sh`
- [ ] Can access all UI pages
- [ ] All API endpoints respond

## Troubleshooting Checklist

If any checks fail, refer to `BOOTSTRAP_TROUBLESHOOTING.md`:

- [ ] Checked GitHub token validity
- [ ] Verified ROCm installation
- [ ] Checked disk space
- [ ] Verified permissions
- [ ] Checked firewall settings
- [ ] Reviewed error logs
- [ ] Ran test suite for diagnostics

## Documentation Review

- [ ] Read `BOOTSTRAP_QUICKREF.md`
- [ ] Read `BOOTSTRAP_IMPLEMENTATION.md`
- [ ] Read `BOOTSTRAP_TROUBLESHOOTING.md`
- [ ] Read `SETUP.md`
- [ ] Familiar with `README.md`

## Production Readiness

- [ ] All tests pass
- [ ] UI accessible on network
- [ ] Database schema up to date
- [ ] Repositories cloned and configured
- [ ] Token securely stored
- [ ] Documentation reviewed
- [ ] Troubleshooting guide available
- [ ] Ready to run AI development loop

## Next Steps

After completing this checklist:

1. [ ] Start UI: `./start_ui.sh`
2. [ ] Sync upstream: `./scripts/update_and_verify.sh`
3. [ ] Train model: `./scripts/train_model.sh`
4. [ ] Run AI agent: `./scripts/run_ai_agent.sh ITERATE radeonsi 10`

## Sign-Off

- Date: _________________
- System: Ubuntu 22.04.3
- ROCm Version: _________________
- GPU Model: _________________
- All Checks Passed: [ ] Yes [ ] No
- Ready for Production: [ ] Yes [ ] No

---

## Emergency Contacts

- Documentation: `BOOTSTRAP_TROUBLESHOOTING.md`
- Test Suite: `./scripts/test_bootstrap.sh`
- Issues: https://github.com/terminills/ai_breadcrumb_automated_development/issues

## Quick Commands

```bash
# Bootstrap
./scripts/bootstrap_ubuntu.sh

# Test
./scripts/test_bootstrap.sh

# Start UI
./start_ui.sh

# Migrate DB
./scripts/migrate_database.sh

# Sync upstream
./scripts/update_and_verify.sh
```

## Success Criteria

✓ All checklist items completed
✓ All tests pass (14/14)
✓ UI accessible on network
✓ Database schema version 1
✓ Repositories configured
✓ Ready for AI development

---

**Note**: This checklist should be completed after every fresh installation or major update.
