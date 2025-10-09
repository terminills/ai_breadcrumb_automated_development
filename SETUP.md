# AROS-Cognito Setup Guide

This guide will help you set up and run the AI Breadcrumb Automated Development system.

## Prerequisites

- Python 3.8 or higher
- Git
- 20GB+ free disk space (for AROS repository)
- Optional: AMD ROCm-capable GPU for training

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Clone AROS Repository

This will clone the AROS Development Team's repository for training:

```bash
./scripts/clone_aros.sh
```

The script will:
- Clone the AROS repository to `aros-src/`
- Display repository statistics
- Prepare for AI training

### 3. Start the Monitoring UI

Launch the web-based monitoring interface:

```bash
cd ui
python app.py
```

Then open your browser to: http://localhost:5000

The UI provides real-time monitoring of:
- AI breadcrumb statistics
- Compilation loop progress
- Error tracking and patterns
- Training status

### 4. Train the Model (Optional)

For full AI capabilities, train the model on AROS codebase:

```bash
./scripts/train_model.sh
```

This will:
- Analyze the AROS commit history
- Fine-tune the model on AROS patterns
- Generate breadcrumb-aware code generation model
- Save trained model to `models/`

**Note**: Full training requires AMD Instinct GPUs with ROCm. The current script demonstrates the training process.

### 5. Run the AI Agent

Start the autonomous development loop:

```bash
./scripts/run_ai_agent.sh ITERATE radeonsi 10
```

Arguments:
- `ITERATE`: Operation mode
- `radeonsi`: Target project
- `10`: Maximum iterations

The agent will:
1. **Analyze** breadcrumbs to find incomplete tasks
2. **Generate** code with breadcrumb metadata
3. **Compile** the code and capture errors
4. **Learn** from compilation errors
5. **Repeat** until task completion or iteration limit

## System Architecture

### Directory Structure

```
ai_breadcrumb_automated_development/
├── config/                    # Configuration files
│   └── config.json           # Main configuration
├── scripts/                   # Automation scripts
│   ├── clone_aros.sh         # Clone AROS repository
│   ├── train_model.sh        # Train AI model
│   └── run_ai_agent.sh       # Run development loop
├── ui/                        # Web monitoring interface
│   ├── app.py                # Flask application
│   └── templates/            # HTML templates
├── src/                       # Core Python modules
│   ├── breadcrumb_parser/    # Breadcrumb parsing and validation
│   └── compiler_loop/        # Compilation and error tracking
├── logs/                      # System logs
│   ├── training/             # Training logs
│   ├── compile/              # Compilation logs
│   └── errors/               # Error tracking database
├── models/                    # Trained AI models
└── aros-src/                 # AROS repository (created by scripts)
```

### The Development Loop

```
┌─────────────┐
│   Analyze   │  Read breadcrumbs, find incomplete tasks
│ Breadcrumbs │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generate   │  AI generates code with breadcrumb metadata
│    Code     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Compile &  │  Run GCC/Make, capture errors
│    Test     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Learn    │  Track errors, update patterns
│from Errors  │
└──────┬──────┘
       │
       └──────→ (Repeat)
```

## Configuration

Edit `config/config.json` to customize:

```json
{
  "aros_repo_url": "https://github.com/aros-development-team/AROS.git",
  "aros_local_path": "./aros-src",
  "training": {
    "batch_size": 4,
    "learning_rate": 0.0001,
    "epochs": 10
  },
  "compiler_loop": {
    "max_iterations": 100,
    "compile_timeout": 300
  },
  "ui": {
    "host": "0.0.0.0",
    "port": 5000,
    "refresh_interval": 5
  }
}
```

## Monitoring and Logs

### Web UI

The web interface provides:
- Real-time system status
- Breadcrumb statistics by phase
- Compilation success/failure rates
- Error intelligence and patterns
- Recent activity logs

### Log Files

All operations are logged to the `logs/` directory:

- `logs/training/` - Training progress and model metrics
- `logs/compile/` - Compilation results (JSON format)
- `logs/errors/` - Error database and patterns
- `logs/agent/` - AI agent iteration logs

## AI Breadcrumb System

The system uses structured metadata comments to track AI development. Breadcrumbs support both **line comments** (`//`) and **block comments** (`/* */`):

**Line Comment Style:**
```c
// AI_PHASE: GRAPHICS_PIPELINE
// AI_STATUS: PARTIAL
// AI_STRATEGY: Initialize LLVM for multi-target GCN code generation
// COMPILER_ERR: undefined reference to 'LLVMInitializeAMDGPUTarget'
// FIX_REASON: Missing LLVM library initialization
// LINUX_REF: drivers/gpu/drm/radeon/radeon_cs.c
// AI_CONTEXT: { "target_arch": "x86_64", "critical": true }
static void init_llvm_backend(void) {
    // Implementation...
}
```

**Block Comment Style:**
```c
/*
 * AI_PHASE: ISSUE_TRACKER_INTEGRATION
 * AI_STATUS: IMPLEMENTED
 * REF_GITHUB_ISSUE: #1
 * REF_TROUBLE_TICKET: TT-2025-001
 * HUMAN_OVERRIDE: Manual fix for edge case
 * AI_CONTEXT: { "issue_tracker": "github", "auto_sync": true }
 */
int init_issue_tracking(void) {
    // Implementation...
}
```

**Enhanced Issue Tracking Integration:**
The breadcrumb system now includes direct integration with issue trackers:
- `REF_GITHUB_ISSUE`: Link to GitHub issues
- `REF_TROUBLE_TICKET`: Internal ticket references
- `REF_USER_FEEDBACK`: User feedback tracking
- `REF_AUDIT_LOG`: Compliance audit logs
- `HUMAN_OVERRIDE`: Manual intervention tracking

See the main README.md for complete breadcrumb tag reference.

## Advanced Usage

### Custom Training

To train on specific AROS components:

```bash
./scripts/train_model.sh /path/to/aros custom-model-name gfx900
```

### Targeted Compilation

To focus on specific AROS projects:

```bash
./scripts/run_ai_agent.sh ITERATE kernel 20
./scripts/run_ai_agent.sh ITERATE graphics 15
```

### Error Analysis

The system automatically tracks and analyzes errors. View the error database:

```bash
cat logs/errors/error_database.json | jq
```

## Troubleshooting

### AROS Repository Not Found

```bash
Error: AROS repository not found
```

Solution: Run `./scripts/clone_aros.sh`

### Port Already in Use

```bash
Error: Port 5000 already in use
```

Solution: Change port in `config/config.json` or stop conflicting service

### Import Errors

```bash
ModuleNotFoundError: No module named 'flask'
```

Solution: Install dependencies: `pip install -r requirements.txt`

## Next Steps

1. **Monitor Progress**: Keep the UI running to watch development in real-time
2. **Review Breadcrumbs**: Check the breadcrumb statistics to understand current state
3. **Analyze Errors**: Use error patterns to improve AI training
4. **Iterate**: Run multiple agent loops to see autonomous improvement

## Contributing

This system is designed for experimentation and research. Contributions welcome:

- Enhance breadcrumb parsing
- Improve error pattern recognition
- Add new compilation targets
- Optimize training pipeline

## References

- AROS Development Team: https://github.com/aros-development-team
- AI Breadcrumb Specification: See README.md
- ROCm Documentation: https://rocmdocs.amd.com/
