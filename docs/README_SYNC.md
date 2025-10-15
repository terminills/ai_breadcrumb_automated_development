# AROS Repository Synchronization Documentation

This directory contains comprehensive documentation for the AROS repository synchronization system.

## Overview

The synchronization system enables you to:
- Work with the private AROS-OLD repository (terminills/AROS-OLD)
- Sync updates from the public upstream repository (aros-development-team/AROS)
- Verify builds after syncing
- Handle merge conflicts
- Maintain compatibility with upstream changes

## Documentation Files

### 📘 [AROS_SYNC_GUIDE.md](AROS_SYNC_GUIDE.md)
**The complete guide for AROS synchronization**

400+ lines covering:
- GitHub token setup and authentication
- Step-by-step sync procedures
- Conflict resolution strategies
- Build verification process
- Troubleshooting common issues
- Best practices and automation
- Advanced usage scenarios

**Start here if**: You're setting up for the first time or need detailed explanations.

### 📊 [SYNC_WORKFLOW_DIAGRAM.md](SYNC_WORKFLOW_DIAGRAM.md)
**Visual workflow diagrams and flowcharts**

Includes:
- Repository structure diagrams
- Data flow visualizations
- Script relationship hierarchies
- State machine diagrams
- Timeline views
- Error handling flows
- Quick reference visuals

**Start here if**: You prefer visual learning or need a quick overview.

### 📋 [../QUICKREF_SYNC.md](../QUICKREF_SYNC.md)
**Quick command reference**

Concise reference for:
- Common commands
- Quick troubleshooting
- Configuration details
- Workflow examples
- Manual operations

**Start here if**: You know what you're doing and just need command syntax.

### 🔧 [../IMPLEMENTATION_NOTES.md](../IMPLEMENTATION_NOTES.md)
**Technical implementation details**

Developer-focused documentation:
- Design decisions
- Implementation rationale
- File changes summary
- Testing approach
- Future enhancements

**Start here if**: You're contributing to the project or need technical details.

## Quick Start

### First Time Setup

1. **Get a GitHub Token**
   ```bash
   # Visit: https://github.com/settings/tokens
   # Create token with 'repo' scope
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

2. **Clone the Repository**
   ```bash
   ./scripts/clone_aros.sh
   ```

3. **You're ready!**

### Regular Workflow

**Option 1: All-in-one** (Recommended)
```bash
./scripts/update_and_verify.sh
```

**Option 2: Step-by-step**
```bash
./scripts/sync_aros_upstream.sh     # Sync
./scripts/verify_aros_build.sh      # Verify
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│        aros-development-team/AROS               │
│        (Public Upstream)                        │
└────────────────┬────────────────────────────────┘
                 │
                 │ fetch/merge
                 ▼
┌─────────────────────────────────────────────────┐
│        terminills/AROS-OLD                      │
│        (Private Fork)                           │
└────────────────┬────────────────────────────────┘
                 │
                 │ clone/push
                 ▼
┌─────────────────────────────────────────────────┐
│        ./aros-src/                              │
│        (Local Working Copy)                     │
└─────────────────────────────────────────────────┘
```

## Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `clone_aros.sh` | Initial clone with authentication | First time setup |
| `sync_aros_upstream.sh` | Fetch and merge upstream changes | Regular updates |
| `verify_aros_build.sh` | Check build after changes | After sync or modifications |
| `update_and_verify.sh` | Combined sync + verify | Regular workflow |

## Configuration

Key settings in `config/config.json`:

```json
{
  "aros_repo_url": "https://github.com/terminills/AROS-OLD.git",
  "aros_upstream_url": "https://github.com/aros-development-team/AROS.git",
  "github_token_env": "GITHUB_TOKEN"
}
```

## Common Tasks

### Check Sync Status
```bash
cd aros-src
git fetch upstream
git log HEAD..upstream/master
```

### Force Sync (Skip Confirmation)
```bash
./scripts/sync_aros_upstream.sh --yes
```

### Resolve Merge Conflicts
```bash
# After conflict detection:
# 1. Edit conflicting files
# 2. Stage resolved files
git add <file>
# 3. Complete merge
git commit
# 4. Verify
./scripts/verify_aros_build.sh
```

### Check Build Logs
```bash
ls -ltr logs/build/
cat logs/build/build_verification_*.log
```

## Troubleshooting

### Authentication Failed
- Check token: `echo $GITHUB_TOKEN`
- Verify token has 'repo' scope
- Regenerate if expired

### Merge Conflicts
- Follow script instructions
- Edit conflicting files
- Test after resolution

### Build Failures
- Check build log in `logs/build/`
- Fix syntax errors
- Re-run verification

## Best Practices

✅ **Do:**
- Sync regularly (weekly)
- Commit local changes before syncing
- Read change preview before accepting
- Run verification after sync
- Keep GitHub token secure

❌ **Don't:**
- Skip verification after sync
- Ignore merge conflicts
- Commit directly to upstream
- Share your GitHub token
- Force-push without backup

## Support

### Getting Help

1. Check this documentation
2. Review script output carefully
3. Check build logs
4. Search AROS development team issues
5. Ask in AROS developer community

### Reporting Issues

When reporting problems, include:
- Command you ran
- Complete error message
- Build log (if applicable)
- Git status output
- Your configuration

## Related Documentation

- [Main README](../README.md) - Project overview
- [Setup Guide](../SETUP.md) - Initial setup
- [System Overview](../SYSTEM_OVERVIEW.md) - Architecture

## Change Log

### Version 1.0 (2025-10-15)
- Initial implementation
- GitHub token authentication
- Upstream sync support
- Build verification
- Comprehensive documentation

## Statistics

- **Total Documentation**: 1,600+ lines
- **Code Added**: 400+ lines (scripts)
- **Files Created**: 7
- **Files Modified**: 4

## Contributing

Improvements welcome! Areas for contribution:
- Enhanced build verification
- Additional automation
- Better conflict resolution
- More comprehensive testing
- Improved error messages

## License

Same as parent project. See main LICENSE file.

---

**Last Updated**: 2025-10-15  
**Version**: 1.0  
**Status**: Production Ready ✓
