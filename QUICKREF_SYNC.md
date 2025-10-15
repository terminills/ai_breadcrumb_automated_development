# AROS Sync Quick Reference

Quick command reference for AROS repository synchronization.

## Initial Setup

```bash
# Set GitHub token (required for private repo)
export GITHUB_TOKEN="ghp_your_token_here"

# Clone the private AROS-OLD repository
./scripts/clone_aros.sh
```

## Regular Sync Operations

```bash
# Sync and verify (recommended - all in one)
./scripts/update_and_verify.sh

# Sync only (fetch + merge from upstream)
./scripts/sync_aros_upstream.sh

# Verify build only (check syntax, no sync)
./scripts/verify_aros_build.sh

# Sync without confirmation prompt (for automation)
./scripts/sync_aros_upstream.sh --yes
```

## Manual Operations

```bash
# Check repository status
cd aros-src
git status
git remote -v

# Fetch upstream changes (no merge)
git fetch upstream

# See what would be merged
git log HEAD..upstream/master

# Merge manually
git merge upstream/master
```

## Handling Issues

```bash
# If merge conflicts occur
git status                    # See conflicting files
# Edit files to resolve conflicts
git add <resolved-file>
git commit

# If build fails
cat logs/build/build_*.log    # Check build logs
./scripts/verify_aros_build.sh # Re-verify after fixes

# Reset to last known good state (WARNING: loses changes)
cd aros-src
git reset --hard HEAD~1
```

## Configuration

Location: `config/config.json`

Key settings:
- `aros_repo_url`: Private repository (terminills/AROS-OLD)
- `aros_upstream_url`: Public upstream (aros-development-team/AROS)
- `github_token_env`: Environment variable name for token (default: GITHUB_TOKEN)

## Logs

Build verification logs: `logs/build/build_verification_*.log`

## Getting Help

- Full guide: [docs/AROS_SYNC_GUIDE.md](docs/AROS_SYNC_GUIDE.md)
- Setup guide: [SETUP.md](SETUP.md)
- Main README: [README.md](README.md)

## Common Workflows

### Weekly Sync
```bash
export GITHUB_TOKEN="your_token"
./scripts/update_and_verify.sh
```

### Before Starting New Work
```bash
cd aros-src
git pull                              # Get your latest changes
cd ..
./scripts/update_and_verify.sh       # Sync with upstream
```

### After Upstream Announces Update
```bash
./scripts/update_and_verify.sh       # Get latest changes
# Test your features
# Fix any issues
git add .
git commit -m "Merge upstream changes and fix compatibility"
git push
```

## Repository Structure

```
Private Repo (terminills/AROS-OLD)
  ↓ origin (push/pull your changes)
  ↓
Local Clone (./aros-src/)
  ↑ upstream (fetch/merge updates)
  ↑
Public Repo (aros-development-team/AROS)
```

## Tips

- Always commit local changes before syncing
- Review changes before accepting merge
- Run verification after every sync
- Keep your GitHub token secure
- Sync regularly to avoid large merges
