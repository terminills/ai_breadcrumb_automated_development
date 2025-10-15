# Interactive Development - Quick Reference

## 🚀 Quick Start

```bash
# Fastest way to start
./scripts/quickstart_interactive.sh

# Or choose specific mode
./scripts/interactive_mode.sh
```

## 📋 Available Tools

| Tool | Command | Use Case |
|------|---------|----------|
| **Interactive Demo** | `python3 scripts/interactive_demo.py` | See full workflow (2 min) |
| **Chat Mode** | `python3 scripts/interactive_chat.py` | Ask questions, generate code |
| **Copilot Iteration** | `./scripts/run_copilot_iteration.sh <project> <n>` | Real AI development |
| **Web UI** | `./start_ui.sh` | Browser monitoring |
| **Menu Launcher** | `./scripts/interactive_mode.sh` | Choose from menu |

## 💬 Chat Commands

```bash
explore <query>     # Search codebase for patterns
generate <task>     # Create code for task
review              # Review code (paste when prompted)
explain <topic>     # Get explanations
history             # Show conversation history
status              # Session info
help                # All commands
exit/quit           # End session
```

## 🎯 Common Tasks

### Understand Existing Code
```bash
python3 scripts/interactive_chat.py
> explore GPU memory allocation
> explain MEMORY_ALLOC_V2 pattern
```

### Generate New Code
```bash
python3 scripts/interactive_chat.py
> explore shader compilation patterns
> generate shader compiler function
> review
[paste code]
###
```

### See Full Workflow
```bash
python3 scripts/interactive_demo.py
# Select task when prompted
# Watch 6 phases execute
```

### Real Development
```bash
./scripts/run_copilot_iteration.sh radeonsi 10
```

### Monitor Progress
```bash
./start_ui.sh
# Open http://localhost:5000
```

## 🔄 6-Phase Development Cycle

```
1. Exploration  → Scan codebase for context
2. Reasoning    → Analyze task, plan approach
3. Generation   → Create code with breadcrumbs
4. Review       → Self-check quality
5. Compilation  → Test and compile
6. Learning     → Track results, improve
```

## 🎨 Output Elements

| Symbol | Meaning |
|--------|---------|
| ✓ | Success |
| ✗ | Error |
| ⚠ | Warning |
| 📂 | Exploring |
| 🧠 | Reasoning |
| ⚡ | Generating |
| 🔍 | Reviewing |
| 🔨 | Compiling |
| 📚 | Learning |
| 🎉 | Complete |
| 💡 | Tip |

## 📁 Key Directories

```
scripts/
  ├── interactive_demo.py        # Demo tool
  ├── interactive_chat.py        # Chat interface
  ├── interactive_mode.sh        # Menu launcher
  ├── quickstart_interactive.sh  # Quick start
  └── run_copilot_iteration.sh   # Real iteration

docs/
  ├── INTERACTIVE_GUIDE.md       # Full guide
  ├── INTERACTIVE_WORKFLOWS.md   # Example workflows
  └── COPILOT_STYLE_ITERATION.md # Technical docs

logs/
  ├── sessions/   # Saved chat sessions
  ├── errors/     # Error tracking
  └── reasoning/  # AI reasoning logs

config/
  └── models.json # Model configuration
```

## 🎓 Learning Path

1. **First Time?** → `./scripts/quickstart_interactive.sh`
2. **See Demo?** → `python3 scripts/interactive_demo.py`
3. **Try Chat?** → `python3 scripts/interactive_chat.py`
4. **Read Docs?** → `docs/INTERACTIVE_GUIDE.md`
5. **Real Use?** → `./scripts/run_copilot_iteration.sh`

## 💡 Pro Tips

### 1. Always Explore First
```
> explore [topic]
```
Context improves generation quality.

### 2. Use Specific Queries
❌ `explore memory`
✓ `explore GPU memory allocation patterns in radeonsi`

### 3. Iterate on Results
```
> generate v1
> review
> generate v2 with improvements
```

### 4. Check History
```
> history
> status
```

### 5. Combine Tools
- Demo → Learn the workflow
- Chat → Quick exploration
- Copilot → Full development
- Web UI → Monitor progress

## 🔧 Model Configuration

### CPU (Default)
```json
{
  "codegen": {
    "model_path": "Salesforce/codegen-350M-mono",
    "device": "cpu"
  }
}
```

### AMD GPU
```json
{
  "codegen": {
    "model_path": "Salesforce/codegen-2B-mono",
    "device": "cuda"
  }
}
```

Edit: `config/models.json`

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Models not loading | Demo/chat don't need models |
| Session won't start | `mkdir -p logs/sessions` |
| Chat stuck | Press Ctrl+C, type `reset` |
| Import errors | `pip install -r requirements.txt` |

## 📚 More Information

- **Full Guide**: `docs/INTERACTIVE_GUIDE.md`
- **Workflows**: `docs/INTERACTIVE_WORKFLOWS.md`
- **Technical**: `docs/COPILOT_STYLE_ITERATION.md`
- **Quick Start**: `docs/QUICKSTART_COPILOT.md`
- **System**: `SYSTEM_OVERVIEW.md`

## 🎬 Example Session

```bash
$ python3 scripts/interactive_chat.py

╔════════════════════════════════════════════════════════════╗
║          AI Development Assistant - Chat Mode             ║
╚════════════════════════════════════════════════════════════╝

> explore GPU memory allocation

📂 Exploring: GPU memory allocation
  • Found 8 relevant C files
  • Identified 3 breadcrumbs with pattern MEMORY_ALLOC_V2
  • Located reference implementation
✓ Exploration complete

> generate memory allocation function

⚡ Generating code for: memory allocation function
```c
// AI_PHASE: GPU_MEMORY
// AI_STATUS: IMPLEMENTED
static BOOL allocate_memory(ctx, size, ptr) {
  ...
}
```
✓ Code generated

> review
[paste code]
###

🔍 Code Review
  ✓ Structure looks good
  ⚠ Add NULL checks
✓ Review complete

> exit

Thanks for using the AI Development Assistant!
```

## 🚀 Getting Started Now

Choose one:

**New User**
```bash
./scripts/quickstart_interactive.sh
```

**See Demo**
```bash
python3 scripts/interactive_demo.py
```

**Try Chat**
```bash
python3 scripts/interactive_chat.py
```

**Read First**
```bash
less docs/INTERACTIVE_GUIDE.md
```

---

**Need Help?** Type `help` in any interactive tool or see the full documentation in `docs/`.
