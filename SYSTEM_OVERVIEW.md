# AROS-Cognito System Overview

## Executive Summary

AROS-Cognito is a self-evolving operating system development platform that uses AI to autonomously develop, compile, and learn from the AROS operating system codebase. The system implements a continuous feedback loop where AI generates code with structured metadata (breadcrumbs), compiles it, learns from errors, and iterates until completion.

## Core Innovation: AI Breadcrumb System

The breadcrumb system is the "cognitive contract" between the AI and the codebase. Every piece of AI-generated code is annotated with structured metadata that documents:

- **Intent**: Why this code exists (AI_STRATEGY, AI_DETAILS)
- **Context**: What environment it operates in (AI_CONTEXT JSON)
- **History**: Previous attempts and fixes (AI_HISTORY, AI_CHANGE)
- **Errors**: What went wrong and how it was fixed (COMPILER_ERR, FIX_REASON)
- **References**: Links to similar code in Linux/AmigaOS (LINUX_REF, AMIGAOS_REF)

This creates a self-documenting, machine-readable development history.

## System Components

### 1. Breadcrumb Parser (`src/breadcrumb_parser/`)

**Purpose**: Extract and validate AI metadata from source code

**Features**:
- Parses C/C++ source files for breadcrumb comments
- Supports 25+ different tag types
- Validates breadcrumb completeness and correctness
- Generates statistics on development progress

**Key Classes**:
- `BreadcrumbParser`: Extracts breadcrumbs from source files
- `Breadcrumb`: Data structure for breadcrumb metadata
- `BreadcrumbValidator`: Ensures breadcrumb quality

### 2. Compiler Loop (`src/compiler_loop/`)

**Purpose**: Implement the compile-test-learn feedback cycle

**Features**:
- Automated compilation with error capture
- Error pattern recognition
- Historical error tracking
- Success/failure metrics

**Key Classes**:
- `CompilerLoop`: Manages compilation and testing
- `ErrorTracker`: Tracks and analyzes errors across iterations

### 3. Web UI (`ui/`)

**Purpose**: Real-time monitoring and visualization

**Features**:
- Live dashboard with auto-refresh
- Breadcrumb statistics by phase and status
- Compilation success/failure tracking
- Error intelligence and patterns
- Training progress monitoring

**Technology**: Flask (Python) + Vanilla JavaScript

### 4. Automation Scripts (`scripts/`)

**Purpose**: Orchestrate the development pipeline

**Scripts**:
- `clone_aros.sh`: Clone AROS repository
- `train_model.sh`: Train AI model on AROS codebase
- `run_ai_agent.sh`: Execute the AI development loop
- `quickstart.sh`: One-command setup and start

## The Development Loop

```
╔═══════════════════════════════════════════════════════════════╗
║                  TRAIN → DEVELOP → COMPILE → LEARN            ║
╚═══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│ Phase 1: ANALYZE                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Parse existing breadcrumbs                            │ │
│ │ • Identify incomplete tasks (PARTIAL, NOT_STARTED)      │ │
│ │ • Prioritize by phase and dependencies                  │ │
│ │ • Load context from AI_HISTORY and AI_CONTEXT           │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: GENERATE                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Use fine-tuned model to generate code                 │ │
│ │ • Generate breadcrumb metadata automatically            │ │
│ │ • Reference LINUX_REF/AMIGAOS_REF for patterns          │ │
│ │ • Apply AI_PATTERN from similar implementations         │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: COMPILE                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Run GCC/Make on modified code                         │ │
│ │ • Capture stdout/stderr                                 │ │
│ │ • Parse compiler errors and warnings                    │ │
│ │ • Log compilation results with timestamps               │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: LEARN                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Hash and track each unique error                      │ │
│ │ • Analyze error patterns (type errors, linking, etc.)   │ │
│ │ • Update breadcrumbs with COMPILER_ERR and FIX_REASON   │ │
│ │ • Feed errors back into model context for next iteration│ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (Iterate until success)
```

## Data Flow

### Breadcrumb Creation
```
Source Code → Parser → Breadcrumb Objects → Validator → Statistics
                                    ↓
                            Database/UI Display
```

### Compilation Cycle
```
Code Generation → Compilation → Error Capture → Error Tracking
       ↑                                              ↓
       └──────────────── Learning ────────────────────┘
```

### Training Pipeline
```
AROS Git History → Dataset Preparation → Model Fine-tuning → Deployment
     (commits)      (breadcrumbs +         (PyTorch +      (Inference
                     code patterns)          ROCm)           Ready)
```

## Architecture Decisions

### 1. Why Python for Core Components?

- Ecosystem: Rich ML/AI libraries (PyTorch, Transformers)
- ROCm Support: Excellent AMD GPU integration
- Rapid Development: Perfect for iterative research
- Data Processing: Strong parsing and analysis capabilities

### 2. Why Flask for UI?

- Lightweight: No unnecessary overhead
- Python Integration: Seamless access to core modules
- Real-time Updates: Easy WebSocket/polling implementation
- Simplicity: Focus on functionality over framework complexity

### 3. Why Structured Comments (Breadcrumbs)?

- **Machine-Readable**: AI can parse and understand
- **Human-Readable**: Developers can review and modify
- **Version Control Friendly**: Text-based, diff-able
- **Non-Invasive**: Doesn't affect compilation or runtime
- **Flexible**: Can be extended without breaking existing code

### 4. Why AROS as Target?

- **Open Source**: Full access to codebase and history
- **Real-World Complexity**: True operating system challenges
- **Rich History**: Decades of development to learn from
- **AmigaOS Legacy**: Unique API patterns for AI to master
- **Active Community**: Real users and feedback

## Performance Characteristics

### Breadcrumb Parsing
- Speed: ~1000 files/second on average hardware
- Memory: O(n) where n = number of breadcrumbs
- Scalability: Parallel processing possible

### Compilation Loop
- Duration: 5-300 seconds per iteration (depends on target)
- Error Tracking: Constant time per error (hashed lookup)
- Storage: ~1MB per 100 iterations (compressed logs)

### Training
- Dataset: ~50GB AROS commit history
- Training Time: 2-48 hours (depends on GPU)
- Model Size: 7-13GB (fine-tuned CodeLlama)
- Inference: 1-5 tokens/second on MI25 GPUs

## Security Considerations

### Code Generation Safety
- Generated code runs in isolated environment
- Compilation happens before execution
- No arbitrary code execution without review

### Error Tracking
- Errors stored locally, no external transmission
- Hash-based deduplication (no sensitive data exposed)
- Configurable data retention policies

### Model Training
- Trained on open-source code only
- No proprietary code in training data
- Local deployment (no cloud dependency)

## Future Enhancements

### Near-Term (v1.x)
- [ ] Real model fine-tuning integration
- [ ] Advanced error pattern recognition
- [ ] Multi-target compilation support
- [ ] WebSocket-based real-time updates
- [ ] Git integration for automatic commits

### Mid-Term (v2.x)
- [ ] Distributed training across multiple GPUs
- [ ] Automated test generation
- [ ] Cross-system porting intelligence
- [ ] Performance regression detection
- [ ] Natural language task input

### Long-Term (v3.x)
- [ ] Multi-modal learning (code + documentation + issues)
- [ ] Collaborative AI-human development
- [ ] Self-optimizing compilation strategies
- [ ] Architectural evolution suggestions
- [ ] Full autonomous OS maintenance

## Metrics and Success Criteria

### Development Velocity
- Lines of code generated per day
- Successful compilation rate
- Error resolution time
- Task completion rate

### Code Quality
- Breadcrumb completeness
- Error recurrence rate
- Pattern reuse frequency
- Review acceptance rate

### Learning Efficiency
- Iterations to success per task
- Error type diversity reduction
- Pattern recognition accuracy
- Context retention across sessions

## Comparison to Traditional Development

| Aspect | Traditional | AROS-Cognito |
|--------|-------------|--------------|
| Planning | Manual design docs | AI_STRATEGY breadcrumbs |
| Coding | Human writes code | AI generates with context |
| Testing | Manual/scripted tests | Compiler-in-loop feedback |
| Debugging | Manual analysis | Automatic error tracking |
| Documentation | Often lacking/outdated | Self-documenting breadcrumbs |
| Learning | Tribal knowledge | Machine-readable history |
| Iteration Speed | Days/weeks | Minutes/hours |

## Technical Requirements

### Development Environment
- Ubuntu 20.04+ (or similar Linux)
- Python 3.8+
- GCC/Make toolchain
- Git
- 8GB+ RAM
- 50GB+ disk space

### Optional (for full training)
- AMD Instinct MI25/MI60 or newer
- ROCm 5.7+
- 16GB+ GPU memory
- PyTorch 2.3+ with ROCm

## References

- AROS Development: https://github.com/aros-development-team
- ROCm Platform: https://rocmdocs.amd.com/
- CodeLlama: https://github.com/facebookresearch/codellama
- AI Breadcrumb Spec: See README.md

## License

This system is designed for research and education. Check individual component licenses for production use.

---

**Status**: Active Development  
**Version**: 1.0  
**Last Updated**: 2025-10-09
