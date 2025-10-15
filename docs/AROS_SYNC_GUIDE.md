# AROS Repository Synchronization Guide

This guide explains how to keep your private AROS-OLD repository synchronized with the upstream aros-development-team repository.

## Overview

The AROS-Cognito project works with two repositories:

1. **Private Repository** (terminills/AROS-OLD): Your working repository where you make changes
2. **Upstream Repository** (aros-development-team/AROS): The main AROS development repository

This guide shows you how to:
- Clone the private repository with authentication
- Sync updates from the upstream repository
- Verify that your code still builds after updates
- Fix any issues that arise from upstream changes

## Prerequisites

- Git installed on your system
- GitHub Personal Access Token (for private repository access)
- Python 3.8+ (for configuration parsing)
- Basic build tools (gcc, make) for verification

## Setup

### 1. Create GitHub Personal Access Token

To access the private AROS-OLD repository, you need a GitHub token:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "AROS Development")
4. Select scopes:
   - ✅ **repo** (Full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### 2. Set Environment Variable

Export the token in your shell:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

To make it permanent, add to your `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Clone Private Repository

```bash
cd /path/to/ai_breadcrumb_automated_development
./scripts/clone_aros.sh
```

This will:
- Clone terminills/AROS-OLD to `./aros-src/`
- Automatically add upstream remote (aros-development-team/AROS)
- Configure authentication using your GitHub token

## Syncing with Upstream

### Quick Sync (Recommended)

Use the all-in-one script that syncs and verifies:

```bash
./scripts/update_and_verify.sh
```

This will:
1. Fetch latest changes from upstream
2. Merge them into your repository
3. Run build verification
4. Report any issues

### Manual Sync

If you prefer step-by-step control:

```bash
# Step 1: Sync only
./scripts/sync_aros_upstream.sh

# Step 2: Verify build
./scripts/verify_aros_build.sh
```

### Sync with Auto-Accept

To skip the confirmation prompt (useful for automation):

```bash
./scripts/sync_aros_upstream.sh --yes
# or
./scripts/sync_aros_upstream.sh -y
```

## Understanding the Sync Process

### What Happens During Sync

1. **Fetch**: Downloads latest commits from aros-development-team/AROS
2. **Analysis**: Shows you what changes will be merged
3. **Confirmation**: Asks if you want to proceed (unless --yes)
4. **Merge**: Integrates upstream changes into your branch
5. **Report**: Shows summary of changes

### Example Output

```
================================================
AROS Upstream Sync Script
================================================
Syncing from: https://github.com/aros-development-team/AROS.git
Local path: /home/user/project/aros-src

Current branch: master
Upstream remote already exists
Upstream branch: master

Changes to be merged:
a1b2c3d Fix memory leak in graphics driver
e4f5g6h Update documentation
h8i9j0k Improve USB device detection
...

Total commits to merge: 47

Do you want to merge these changes? (y/N) y

Merging upstream changes...
✓ Successfully merged upstream changes

================================================
Sync Summary
================================================
Branch: master
Commits merged: 47
Repository is now up to date with upstream
```

## Build Verification

### What Gets Verified

The verification script checks:

1. **Prerequisites**: gcc, make, python3
2. **Configuration**: Whether AROS is configured for building
3. **Syntax**: Compiles recently modified C/H files
4. **Summary**: Reports any errors found

### Example Output

```
================================================
AROS Build Verification Script
================================================

Checking build prerequisites...
✓ gcc found
✓ make found
✓ python3 found

✓ AROS appears to be configured

Performing syntax checks on C files...
  Checking arch/all-linux/kernel/core.c... ✓
  Checking compiler/arossupport/newlist.c... ✓
  Checking rom/exec/allocmem.c... ✓

================================================
Build Verification Summary
================================================
Files checked: 3
Syntax errors: 0

✓ No syntax errors detected in checked files
```

## Handling Issues

### Merge Conflicts

If the sync detects conflicts:

```
✗ Merge conflicts detected!

Conflicting files:
  arch/all-linux/kernel/platform_init.c
  rom/exec/memory.c

To resolve conflicts:
  1. Edit the conflicting files
  2. Run: git add <file>
  3. Run: git commit
```

**Resolution Steps:**

1. Open each conflicting file in your editor
2. Look for conflict markers:
   ```c
   <<<<<<< HEAD
   // Your changes
   =======
   // Upstream changes
   >>>>>>> upstream/master
   ```
3. Edit to resolve the conflict
4. Remove the conflict markers
5. Stage the resolved file: `git add <file>`
6. Complete the merge: `git commit`
7. Verify: `./scripts/verify_aros_build.sh`

### Build Failures

If verification finds syntax errors:

```
✗ Syntax errors detected. Check build log for details:
  cat logs/build/build_verification_20251015_143000.log
```

**Resolution Steps:**

1. Check the build log for specific errors
2. Fix the syntax errors in your code
3. Re-run verification: `./scripts/verify_aros_build.sh`
4. If errors are in upstream code, you may need to:
   - Report the issue to aros-development-team
   - Apply a temporary fix
   - Document the fix for future syncs

### Authentication Issues

If you get authentication errors:

```
fatal: Authentication failed
```

**Resolution:**

1. Verify your token is set: `echo $GITHUB_TOKEN`
2. Check token permissions at https://github.com/settings/tokens
3. Regenerate token if necessary
4. Update the environment variable
5. Re-run: `./scripts/clone_aros.sh`

## Best Practices

### Regular Syncing

- Sync at least weekly to avoid large merges
- Sync before starting major new features
- Sync after upstream announces important updates

### Pre-Sync Checklist

Before syncing:
- ✅ Commit all local changes
- ✅ Push your changes to GitHub (backup)
- ✅ Note your current working state
- ✅ Have time to handle any merge conflicts

### Post-Sync Checklist

After syncing:
- ✅ Run full build verification
- ✅ Test your custom features
- ✅ Update any documentation affected by changes
- ✅ Commit the merge if not auto-committed

## Automation

### Cron Job for Daily Sync

To automatically sync daily:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * cd /path/to/project && ./scripts/update_and_verify.sh --yes >> logs/sync.log 2>&1
```

### Git Hooks

Set up a pre-push hook to verify build before pushing:

```bash
# Create hook file
cat > aros-src/.git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "Running build verification..."
cd .. && ./scripts/verify_aros_build.sh
EOF

chmod +x aros-src/.git/hooks/pre-push
```

## Configuration

### Repository URLs

The sync system uses these configurations (in `config/config.json`):

```json
{
  "aros_repo_url": "https://github.com/terminills/AROS-OLD.git",
  "aros_upstream_url": "https://github.com/aros-development-team/AROS.git",
  "aros_local_path": "./aros-src",
  "github_token_env": "GITHUB_TOKEN"
}
```

### Customization

To use different repositories or paths:

1. Edit `config/config.json`
2. Update the relevant URLs
3. Re-run `./scripts/clone_aros.sh`

## Troubleshooting

### "upstream remote already exists"

This is normal and not an error. The script detects and uses the existing upstream remote.

### "Not a git repository"

Make sure you're in the correct directory and have cloned the repository first.

### Large Number of Conflicts

If you have many conflicts:

1. Consider creating a new branch for the merge
2. Resolve conflicts incrementally
3. Test after each resolution
4. Merge back to your main branch when done

### Sync Takes Too Long

For large updates:
- Be patient, it may take several minutes
- Check your internet connection
- Verify disk space is available

## Advanced Usage

### Sync Specific Branch

```bash
cd aros-src
git fetch upstream
git merge upstream/development
```

### Cherry-Pick Specific Commits

```bash
cd aros-src
git fetch upstream
git cherry-pick abc123def456
```

### Reset to Upstream

If you want to completely reset to upstream:

```bash
cd aros-src
git fetch upstream
git reset --hard upstream/master
```

**Warning**: This discards all local changes!

## Getting Help

If you encounter issues:

1. Check the build log in `logs/build/`
2. Review the sync output carefully
3. Search AROS development team issues
4. Ask in the AROS developer community

## Related Documentation

- [SETUP.md](../SETUP.md) - Initial setup guide
- [README.md](../README.md) - Project overview
- [SYSTEM_OVERVIEW.md](../SYSTEM_OVERVIEW.md) - System architecture

## Summary

The AROS synchronization workflow:

```
┌─────────────────────┐
│  Clone Private Repo │
│   (one-time setup)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Sync from Upstream │ ← Run regularly
│   (fetch + merge)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Verify Build       │
│  (syntax check)     │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
   Success   Failure
      │         │
      │         └──→ Fix Issues
      │                  │
      └──────────────────┘
```

Keep your repository synchronized, verify builds regularly, and maintain compatibility with upstream changes!
