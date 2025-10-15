# AROS Repository Sync Workflow Diagram

## Repository Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                   GitHub Repositories                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  aros-development-team/AROS (Public)                   │    │
│  │  https://github.com/aros-development-team/AROS         │    │
│  │                                                         │    │
│  │  • Main AROS development                               │    │
│  │  • Always up-to-date                                   │    │
│  │  • Multiple contributors                               │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                             │
│                   │ fetch/merge (upstream)                      │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  terminills/AROS-OLD (Private)                         │    │
│  │  https://github.com/terminills/AROS-OLD               │    │
│  │                                                         │    │
│  │  • Our working fork                                    │    │
│  │  • May be out of date                                  │    │
│  │  • Custom modifications                                │    │
│  │  • Requires GitHub token                               │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                             │
└───────────────────┼─────────────────────────────────────────────┘
                    │
                    │ clone/pull (origin)
                    │ (with GITHUB_TOKEN)
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Local Development Machine                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ./aros-src/                                                     │
│  │                                                               │
│  ├── .git/                                                       │
│  │   ├── remotes/                                               │
│  │   │   ├── origin    → terminills/AROS-OLD                    │
│  │   │   └── upstream  → aros-development-team/AROS             │
│  │                                                               │
│  ├── arch/           (AROS architecture code)                   │
│  ├── compiler/       (AROS compiler)                            │
│  ├── rom/            (AROS ROM modules)                         │
│  └── workbench/      (AROS workbench)                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Sync Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Initial Setup (One-time)                                │
└─────────────────────────────────────────────────────────────────┘

   User Action                    Script                Result
   ───────────                    ──────                ──────

   1. Create GitHub Token
      │
      └─→ export GITHUB_TOKEN="..."
              │
              └─→ ./scripts/clone_aros.sh
                      │
                      ├─→ Clone terminills/AROS-OLD
                      ├─→ Add origin remote (with auth)
                      └─→ Add upstream remote
                              │
                              ▼
                          ✓ Local repo ready


┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Regular Sync (Weekly/Before Work)                       │
└─────────────────────────────────────────────────────────────────┘

   User Action                    Script                Result
   ───────────                    ──────                ──────

   ./scripts/update_and_verify.sh
       │
       ├─→ sync_aros_upstream.sh
       │       │
       │       ├─→ git fetch upstream
       │       │       │
       │       │       └─→ Downloads latest commits
       │       │
       │       ├─→ Show changes preview
       │       │       │
       │       │       └─→ List of commits to merge
       │       │
       │       ├─→ Ask confirmation
       │       │       │
       │       │       └─→ User: y/N?
       │       │
       │       └─→ git merge upstream/master
       │               │
       │               ├─→ ✓ Success → Continue
       │               └─→ ✗ Conflicts → User fixes
       │
       └─→ verify_aros_build.sh
               │
               ├─→ Check build tools
               ├─→ Check AROS config
               ├─→ Syntax check modified files
               └─→ Generate build log
                       │
                       ├─→ ✓ All pass → Success!
                       └─→ ✗ Errors → User fixes


┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Handle Conflicts (If Needed)                            │
└─────────────────────────────────────────────────────────────────┘

   Conflict Detected              Action                Result
   ─────────────────              ──────                ──────

   git merge fails
       │
       ├─→ Script shows conflicting files
       │       │
       │       └─→ file1.c, file2.c, ...
       │
       └─→ User edits files
               │
               ├─→ Resolve <<<<<<< ======= >>>>>>>
               ├─→ git add <file>
               ├─→ git commit
               │       │
               │       └─→ Merge complete
               │
               └─→ ./scripts/verify_aros_build.sh
                       │
                       └─→ Verify fixes work


┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Push to Origin (Backup)                                 │
└─────────────────────────────────────────────────────────────────┘

   Local Changes                  Action                Result
   ─────────────                  ──────                ──────

   Sync complete + verified
       │
       └─→ git push origin master
               │
               └─→ Updates terminills/AROS-OLD
                       │
                       └─→ ✓ Changes backed up on GitHub
```

## Data Flow

```
Upstream Changes Flow:
──────────────────────

aros-development-team/AROS  (commit: abc123)
            │
            │ git fetch upstream
            ▼
    Local upstream/master   (commit: abc123)
            │
            │ git merge upstream/master
            ▼
    Local master            (commit: abc123 + your changes)
            │
            │ git push origin
            ▼
terminills/AROS-OLD         (commit: abc123 + your changes)


Your Changes Flow:
─────────────────

Local working directory
            │
            │ git add & commit
            ▼
    Local master
            │
            │ git push origin
            ▼
terminills/AROS-OLD
            │
            │ (AI trains on this)
            ▼
    AI Model learns from changes
```

## Script Relationships

```
Scripts Hierarchy:
─────────────────

update_and_verify.sh (Master workflow)
    │
    ├─→ sync_aros_upstream.sh
    │       │
    │       ├─→ git fetch upstream
    │       ├─→ git merge upstream/master
    │       └─→ git log (summary)
    │
    └─→ verify_aros_build.sh
            │
            ├─→ Check prerequisites
            ├─→ gcc -fsyntax-only (modified files)
            └─→ Generate logs/build/*.log


Clone Workflow:
──────────────

clone_aros.sh
    │
    ├─→ Read config.json
    │       ├─→ aros_repo_url (terminills/AROS-OLD)
    │       └─→ aros_upstream_url (aros-development-team/AROS)
    │
    ├─→ Check GITHUB_TOKEN
    │       ├─→ Found: Use authenticated URL
    │       └─→ Missing: Use regular URL (will prompt)
    │
    ├─→ git clone (with auth)
    └─→ git remote add upstream
```

## Timeline View

```
Project Timeline:
────────────────

Time  │ Upstream (aros-dev-team)    │ Your Fork (AROS-OLD)
──────┼─────────────────────────────┼───────────────────────────
      │                             │
Day 0 │ Commit A                    │ Clone at A
      │                             │ git clone ...
      │                             │
Day 1 │ Commit B                    │ Working...
Day 2 │ Commit C                    │ Add feature X
Day 3 │                             │ Commit X
      │                             │
Day 4 │ Commit D                    │ 🔴 Out of sync!
Day 5 │ Commit E                    │
Day 6 │ Commit F                    │
      │                             │
Day 7 │                             │ ✓ SYNC
      │                             │ ./update_and_verify.sh
      │                             │   ├─ Fetch B,C,D,E,F
      │                             │   └─ Merge into local
      │                             │
      │                             │ Now: A + X + B,C,D,E,F
      │                             │ git push origin
      │                             │
Day 8 │ Commit G                    │ In sync + feature X
      │                             │
```

## States and Transitions

```
Repository State Machine:
────────────────────────

     ┌─────────────┐
     │   Initial   │
     │   (empty)   │
     └──────┬──────┘
            │
            │ clone_aros.sh
            ▼
     ┌─────────────┐
     │   Cloned    │
     │ + upstream  │
     └──────┬──────┘
            │
     ┌──────┴──────┐
     │             │
     │ Regular     │ Out of date
     │ work        │
     │             │
     ▼             ▼
┌─────────┐   ┌─────────────┐
│Modified │   │   Behind    │
│ Locally │   │  Upstream   │
└────┬────┘   └──────┬──────┘
     │               │
     │ commit        │ sync_aros_upstream.sh
     ▼               ▼
┌─────────┐   ┌─────────────┐
│Committed│   │   Synced    │
└────┬────┘   └──────┬──────┘
     │               │
     │ push          │ verify_aros_build.sh
     ▼               ▼
┌─────────┐   ┌─────────────┐
│ Backed  │◄──┤  Verified   │
│   Up    │   │    ✓        │
└─────────┘   └─────────────┘
```

## Error Handling Flow

```
Error Scenarios:
───────────────

┌──────────────────┐
│ Start Sync       │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
No Repo    Repo Exists
    │         │
    │         ├──→ Uncommitted changes?
    │         │        ├─→ Yes: Error + instructions
    │         │        └─→ No: Continue
    │         │
    │         ├──→ Fetch upstream
    │         │        ├─→ Success: Continue
    │         │        └─→ Fail: Network error
    │         │
    │         ├──→ Merge
    │         │        ├─→ Success: Continue
    │         │        └─→ Conflicts: Help resolve
    │         │
    │         └──→ Verify
    │                  ├─→ Success: Done ✓
    │                  └─→ Fail: Show errors
    │
    └──→ Error: Run clone_aros.sh first
```

## Quick Reference Visual

```
╔══════════════════════════════════════════════════════════════╗
║                  AROS Sync Quick Commands                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  🔧 Setup (once):                                            ║
║     export GITHUB_TOKEN="..."                                ║
║     ./scripts/clone_aros.sh                                  ║
║                                                               ║
║  🔄 Regular sync (weekly):                                   ║
║     ./scripts/update_and_verify.sh                           ║
║                                                               ║
║  ⚡ Quick checks:                                            ║
║     ./scripts/sync_aros_upstream.sh    # Sync only          ║
║     ./scripts/verify_aros_build.sh     # Verify only        ║
║                                                               ║
║  📝 After conflicts:                                         ║
║     # Edit conflicting files                                 ║
║     git add <file>                                           ║
║     git commit                                               ║
║     ./scripts/verify_aros_build.sh                           ║
║                                                               ║
║  📊 Check status:                                            ║
║     cd aros-src && git status                                ║
║     git log HEAD..upstream/master      # See pending         ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

## See Also

- [AROS_SYNC_GUIDE.md](AROS_SYNC_GUIDE.md) - Comprehensive guide
- [../QUICKREF_SYNC.md](../QUICKREF_SYNC.md) - Command reference
- [../SETUP.md](../SETUP.md) - Setup instructions
