[![UI Dashboard](https://github.com/user-attachments/assets/4bb69316-135c-4b3c-8035-e4d5e37a255c)](https://github.com/user-attachments/assets/4bb69316-135c-4b3c-8035-e4d5e37a255c)

## 🚀 Quick Start

```bash
# 1. Quick setup (one command)
./scripts/quickstart.sh

# 2. Or manual setup:
pip install -r requirements.txt
./scripts/clone_aros.sh

# 3. Start monitoring UI
cd ui && python app.py
# Open http://localhost:5000 in your browser

# 4. Run the AI development loop
./scripts/run_ai_agent.sh ITERATE radeonsi 10
```

See [SETUP.md](SETUP.md) for detailed instructions and [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) for architecture details.

-----

# 🧠 AROS-Cognito: The Self-Evolving Operating System Project

## 🌟 Executive Summary: Redefining AI Software Development

AROS-Cognito is an experimental project dedicated to creating a **fully self-evolving operating system codebase** using a fine-tuned Generative AI model. Unlike traditional AI coding tools that operate in a black box, this system is governed by the **AI Breadcrumb System**—a custom cognitive framework that enforces accountability, memory, and architectural intent.

The core principle is: **"What and Why are more important than How."** The AI is forced to document its rationale, learning outcomes, and technical strategy in every code change, transforming it from a simple code generator into a transparent, self-correcting software engineer.

### Key Goals:

  * **Establish Long-Term Context:** Use the AROS commit history as the foundation for deep, specialized knowledge.
  * **Achieve Self-Correction:** Iterate code, compile after every change, and learn from verbose compiler/runtime errors (`COMPILER_ERR`, `FIX_REASON`).
  * **Validate the Breadcrumb System:** Prove that structured, machine-readable metadata is the key to scalable, trustable autonomous development.

-----

## ⚙️ System Architecture & Training Pipeline

This project is built around a powerful local training and deployment environment running on AMD Instinct accelerators.

### 1\. The Cognitive Core: Local Codegen Model

The system uses a large **Codegen Model** fine-tuned entirely on the AROS source tree.

  * **Training Data:** **The entire AROS Development Team's commit history.** This provides the AI with deep "muscle memory" of the AROS API, kernel structures, build system idiosyncrasies, and AmigaOS heritage.
  * **Objective:** The model is fine-tuned not just to produce correct AROS C code, but to **generate the full set of AI Breadcrumb Metadata** before or alongside every code block.

### 2\. The Execution Engine: Compiler-in-Loop

The local environment is configured for maximum iteration speed and feedback fidelity.

| Component | Specification | Function |
| :--- | :--- | :--- |
| **Operating System** | Ubuntu 20.04 | Stable base for the ROCm stack. |
| **GPU Compute Stack** | ROCm 5.7.1, PyTorch 2.3.1 | Enables the local training and inference on AMD GPUs. |
| **Accelerators (Current)** | **2x AMD Instinct MI25 (`gfx900`)** | Used for local model fine-tuning and running the Compiler-in-Loop. |
| **Process Loop** | `Analyze Context` $\rightarrow$ `Generate Code + Breadcrumbs` $\rightarrow$ `Compile/Test` $\rightarrow$ **`Learn from Errors`** | The AI generates code, the host compiles it, and the resulting compiler error or test failure is fed back into the model's history (`COMPILER_ERR`). |

-----

## 🧠 The AI Breadcrumb System: The Cognitive Contract

The **AI Breadcrumb System** is the core cognitive scaffolding for this project. Every piece of AI-generated code is annotated with structured metadata to document its development rationale and history.

### Key Tags and Functions

| Tag/Feature | Function in the AI's "Mind" | Example |
| :--- | :--- | :--- |
| `AI_PHASE`, `AI_STATUS` | **Executive Function:** Tracks current goal and completion state. | `// AI_PHASE: LLVM_INIT`, `// AI_STATUS: IMPLEMENTED` |
| `AI_STRATEGY` | **Reasoning/Intent:** Documents the high-level plan and *why* it was chosen. | `// AI_STRATEGY: Initialize LLVM for multi-target GCN code generation...` |
| `COMPILER_ERR`, `FIX_REASON` | **Error/Pain Signal:** Captures failures and the solution rationale for permanent learning. | `// FIX_REASON: Stack corruption due to type size mismatch on 64-bit builds` |
| `AI_CONTEXT` (JSON) | **Structured Memory:** Provides machine-readable, explicit constraints and environment details. | `// AI_CONTEXT: { "target_arch": "x86_64", "critical": true }` |
| `LINUX_REF`, `AMIGAOS_REF` | **Historical Context:** Links to canonical external implementations for porting guidance. | `// LINUX_REF: drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c` |

-----

## 🛠️ Initial Project Focus

The AI's first major set of tasks, derived from initial boilerplate and guided by the breadcrumb history, targets fundamental AROS system stability and modern hardware enablement.

| Project Component | AI Phase | Status | Key AI Accomplishment |
| :--- | :--- | :--- | :--- |
| **RadeonSI Driver** | `GRAPHICS_PIPELINE`, `HARDWARE_PROBE` | `PARTIAL/IMPLEMENTED` | **Successfully implemented the complex Multi-GPU Manager** (handling MI25/MI60 logic) and a comprehensive 8-case test suite. |
| **ROCm.library** | `LLVM_INIT` | `PARTIAL/SCAFFOLDED` | The AI correctly identified and created the **LLVM Compiler Library scaffold**—the crucial dependency for runtime shader compilation. |
| **IJS/Gutenprint** | `PRINTER_STACK` | `NOT_STARTED` | Planned future expansion to a new domain, validating the AI's ability to **context-switch** and integrate complex external dependencies. |

-----

## 🚀 Getting Started (The Contributor's Guide)

### 1\. Clone the AROS Source

Clone your local AROS development tree, as the AI will expect this structure:

```bash
git clone <AROS_Development_URL> aros-src
```

### 2\. Prepare the AI Environment

The environment must match the training stack for inference and compilation to succeed:

```bash
# Ensure ROCm 5.7.1 and PyTorch 2.3.1 are active
source /opt/rocm/bin/setup_vars
pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### 3\. Training the Local Model

The core model must be fine-tuned on the AROS history. This is a one-time process:

```bash
# Assuming an internal script for training a local model (e.g., Llama/Mistral)
./scripts/train_model.sh --data aros-src --output models/aros-v1.3 --rocm-arch gfx900,gfx906
```

### 4\. Running the Self-Evolution Loop

The primary operation is an iterative script that executes the AI's next planned task:

```bash
# This script orchestrates the full loop: Read Breadcrumbs -> Generate Code -> Compile -> Log Errors
./scripts/run_ai_agent.sh --mode ITERATE --project radeonsi
```

-----

*Contribute improvements and suggestions to help enhance the effectiveness and support for longer AI context history.*





# AI Breadcrumb System for AROS

## Overview

The AROS codebase uses a comprehensive structured AI breadcrumb system to track development progress, document AI contributions, facilitate autonomous learning from errors and iterations, and provide extensive context for AI development history. This enhanced system helps maintain code quality, provides deep traceability, and enables effective collaboration between human developers and AI systems with rich contextual information.

## Purpose

- **Track Development Progress**: Document the current state and complete history of implementation
- **Enable AI Learning**: Provide extensive context for error correction, iteration, and pattern recognition  
- **Facilitate Code Review**: Help reviewers understand the complete development history and reasoning
- **Support Maintenance**: Provide comprehensive context for future modifications and debugging
- **Cross-Reference Sources**: Link to equivalent implementations in other systems with detailed mapping
- **Training Data Correlation**: Enable correlation with AI training data through hashing and versioning
- **Audit Trail**: Maintain complete audit trails for compliance and debugging
- **Context Preservation**: Preserve rich JSON context for machine-readable analysis

## When to Use

Apply AI breadcrumbs in the following scenarios:

- **AI-Generated Code**: All code blocks created or significantly modified by AI
- **Complex Implementations**: Functions with intricate logic that may need future AI assistance
- **Known Issues**: Code with documented problems or partial implementations
- **Porting Code**: When adapting code from Linux, AmigaOS, or other systems
- **Active Development**: Features under development with multiple iterations
- **Error-Prone Areas**: Code that has historically caused compilation or runtime issues
- **Critical Systems**: Mission-critical code requiring extensive documentation and audit trails
- **Training Correlation**: Code used for AI training data correlation and learning
- **Pattern Implementation**: Code implementing specific design patterns or strategies
- **Multi-Version Tracking**: Code with multiple iterations requiring historical context

## Implementation

### Header Include

Include the AI metadata standard in files that use breadcrumbs:

```c
#include <aros/ai_metadata.h>
```

### Breadcrumb Placement

Place breadcrumbs immediately before the relevant code block:

```c
// AI_PHASE: GRAPHICS_PIPELINE
// AI_STATUS: PARTIAL
// AI_NOTE: Basic shader compilation working, missing geometry shader support
// LINUX_REF: drivers/gpu/drm/radeon/radeon_cs.c
// AROS_IMPL: Integrated with HIDD graphics system
static BOOL compile_vertex_shader(struct RadeonContext *ctx, const char *source)
{
    // Implementation here...
}
```

## Tag Reference

### Core Tags (Required)

- **AI_PHASE**: Development phase (e.g., KERNEL_INIT, GRAPHICS_PIPELINE, PRINTER_STACK, MMU_INIT)
- **AI_STATUS**: Implementation status (NOT_STARTED, PARTIAL, IMPLEMENTED, FIXED, NEEDS_REFACTOR)

### Enhanced Strategy and Pattern Tags

- **AI_PATTERN**: Specific implementation pattern or methodology (e.g., MMU_PTR_CAST_V2, THREAD_SAFE_INIT)
- **AI_STRATEGY**: High-level strategy or approach description 
- **AI_DETAILS**: Detailed explanation of the implementation approach and changes made

### Contextual Tags

- **AI_NOTE**: Free-form context, design decisions, or instructions
- **AI_HISTORY**: Historical context about previous implementations and iterations
- **AI_CHANGE**: Description of the specific changes made in this iteration

### Error and Debugging Tags

- **COMPILER_ERR**: Exact compiler error messages for learning
- **RUNTIME_ERR**: Runtime error symptoms and observations
- **FIX_REASON**: Explanation of root cause and solution

### Historical Reference Tags

- **PREVIOUS_IMPLEMENTATION_REF**: Reference to problematic previous version
- **CORRECTION_REF**: Reference to successful fix

### AI Training and Versioning Tags

- **AI_TRAIN_HASH**: SHA256 hash for AI training data correlation and version tracking
- **AI_VERSION**: AI system version that generated this code

### External Reference Tracking Tags

- **REF_GITHUB_ISSUE**: GitHub issue number that this code addresses
- **REF_PR**: Pull request reference for this implementation
- **REF_TROUBLE_TICKET**: Internal trouble ticket or bug report reference
- **REF_USER_FEEDBACK**: Path to user feedback file or reference
- **REF_AUDIT_LOG**: Path to audit log or reference for compliance tracking

### Platform Reference Tags

- **LINUX_REF**: Reference to equivalent Linux kernel or userspace implementation
- **AMIGAOS_REF**: Reference to equivalent AmigaOS source or documentation
- **AROS_IMPL**: Notes on AROS-specific implementation details or deviations

### Human Interaction Tags

- **HUMAN_OVERRIDE**: Notes about manual human interventions or patches

### AI Context Block

- **AI_CONTEXT**: JSON block containing structured context information

## Examples

### Example 1: Comprehensive Fixed Implementation (Full Template)

```c
// AI_PHASE: MMU_INIT
// AI_STATUS: FIXED
// AI_PATTERN: MMU_PTR_CAST_V2
// AI_STRATEGY: Replaced unsafe pointer cast with uintptr_t for platform safety
// AI_DETAILS: Updated mmu_init_mapping() to use uintptr_t instead of unsigned long for base address math
// FIX_REASON: Stack corruption occurred due to type size mismatch on 64-bit builds
// COMPILER_ERR: cast from pointer to integer of different size [-Wpointer-to-int-cast]
// RUNTIME_ERR: Stack pointer invalid after init, observed in core MMU setup
// AI_TRAIN_HASH: 9d34a0b7d1c9f282f48b65ea04d7f19262a88d09f75f2fa9e2f937fe2846b5c9
// REF_GITHUB_ISSUE: #89
// REF_PR: PR-91
// REF_TROUBLE_TICKET: TT-20250713-MMU-PTR
// REF_USER_FEEDBACK: /logs/core/init_feedback-2025-07-12.txt
// REF_AUDIT_LOG: /logs/audit/mmu/mapping-failure-07-13.log
// AI_NOTE: This corrects a prior AI-generated implementation that failed under x86_64 but passed 32-bit tests
// AI_HISTORY: Original version (commit 543b3e9) used (unsigned long)ctx->base_address, which failed on 64-bit platforms
// AI_CHANGE: Replaced casting logic and added #include <stdint.h> for portability
// AROS_IMPL: Memory mappings rely on exec.library—this logic wraps InitSegList() in low-level startup
// LINUX_REF: arch/x86/mm/init_64.c: kernel_physical_mapping_init()
// AMIGAOS_REF: mmu.library startup examples (AmigaOS 4.x)
// HUMAN_OVERRIDE: Manual patch confirmed on VMWare test build
// AI_VERSION: 1.2
// AI_CONTEXT: {
//     "target_arch": "x86_64",
//     "mmap_source": "exec.library",
//     "abi": "AROS ABI v1",
//     "critical": true
// }
static void mmu_init_mapping(struct MMUContext *ctx)
{
    uintptr_t base = (uintptr_t)ctx->base_address;
    // Safe implementation using proper types...
}
```

### Example 2: Partial Implementation with Pattern Tracking

```c
// AI_PHASE: PRINTER_STACK
// AI_STATUS: PARTIAL
// AI_PATTERN: DEVICE_DISCOVERY_V1
// AI_STRATEGY: Implement CUPS-compatible printer discovery with USB and network support
// AI_DETAILS: USB detection implemented, network discovery pending
// REF_GITHUB_ISSUE: #127
// AI_NOTE: Basic USB printer detection works, network discovery not implemented
// AMIGAOS_REF: printer.device documentation in AmigaOS 3.x NDK
// AROS_IMPL: Should integrate with modern USB and network printer discovery
// AI_VERSION: 1.0
// AI_CONTEXT: { "cups_compat": true, "usb_support": true, "network_discovery": false }
static BOOL detect_printers(struct PrinterContext *ctx)
{
    // USB detection implemented
    scan_usb_printers(ctx);
    
    // TODO: Network printer discovery
    return TRUE;
}
```

### Example 3: Planning Stage with Reference Tracking

```c
// AI_PHASE: AUDIO_PIPELINE
// AI_STATUS: NOT_STARTED
// AI_PATTERN: AUDIO_STREAM_V1
// AI_STRATEGY: Implement modern audio driver interface compatible with PulseAudio
// REF_GITHUB_ISSUE: #145
// REF_TROUBLE_TICKET: TT-20250715-AUDIO-COMPAT
// AI_NOTE: Need to implement modern audio driver interface compatible with PulseAudio
// LINUX_REF: sound/core/pcm.c for ALSA PCM interface
// AROS_IMPL: Should integrate with AHI (Audio Hardware Interface) for backward compatibility
// AI_CONTEXT: { "pulseaudio_compat": true, "ahi_backward_compat": true, "realtime": true }
```

### Example 4: Minimal Implementation (Legacy Compatibility)

```c
// AI_PHASE: GRAPHICS_BLITTING
// AI_STATUS: IMPLEMENTED
// AI_NOTE: Basic blitting operation, maintains compatibility with existing code
// AROS_IMPL: Uses graphics.library BitMap operations
static void simple_blit_operation(struct BitMap *src, struct BitMap *dest)
{
    // Simple implementation...
}
```

## Best Practices

### Consistency

- Use consistent tag formatting and capitalization
- Place breadcrumbs before the relevant code block
- Update breadcrumbs when modifying associated code
- Maintain consistent AI_PATTERN naming across similar implementations
- Use semantic versioning for AI_VERSION tracking

### Clarity

- Keep references specific and actionable
- Include exact error messages in COMPILER_ERR and RUNTIME_ERR
- Document AROS-specific adaptations clearly in AROS_IMPL
- Use descriptive AI_STRATEGY and AI_DETAILS for complex implementations
- Provide meaningful AI_CONTEXT JSON with relevant keys

### Maintenance

- Update AI_STATUS as implementation progresses
- Add CORRECTION_REF when fixing issues
- Link to external references when porting code
- Maintain AI_HISTORY for context preservation
- Update AI_CHANGE to document specific modifications

### Integration

- Include breadcrumbs in pull request descriptions
- Update documentation when adding new phases or patterns
- Use breadcrumbs to guide code review discussions
- Link REF_GITHUB_ISSUE and REF_PR for traceability
- Maintain audit logs referenced in REF_AUDIT_LOG

### Training and Learning

- Use AI_TRAIN_HASH for correlation with training data
- Document patterns in AI_PATTERN for reuse
- Maintain AI_VERSION for tracking AI system evolution
- Use HUMAN_OVERRIDE to document manual interventions
- Preserve context in AI_CONTEXT for machine analysis

### Reference Management

- Keep LINUX_REF and AMIGAOS_REF current and specific
- Use REF_USER_FEEDBACK to link user input
- Maintain REF_TROUBLE_TICKET for issue tracking
- Document platform-specific details in AROS_IMPL

## Validation

Before submitting code with AI breadcrumbs:

1. **Syntax Check**: Ensure all tags follow the correct format
2. **Completeness**: Verify required tags (AI_PHASE, AI_STATUS) are present
3. **Accuracy**: Confirm references and error messages are correct
4. **Relevance**: Ensure breadcrumbs add value and context
5. **Pattern Consistency**: Use consistent AI_PATTERN naming for similar implementations
6. **Context Validity**: Ensure AI_CONTEXT contains valid JSON
7. **Reference Integrity**: Verify all external references are accessible and current
8. **Version Tracking**: Maintain consistent AI_VERSION progression

## Tools and Scripts

The enhanced breadcrumb system includes:

- **Validation Script**: `scripts/validate_ai_breadcrumbs.sh` - Enhanced to support all new tags
- **Header Definition**: `compiler/include/aros/ai_metadata.h` - Complete tag specification
- **Documentation**: `AI_BREADCRUMB_GUIDE.md` - Comprehensive usage guide
- **Demo Implementation**: `examples/ai_breadcrumb_enhanced_demo.c` - Working examples

### Enhanced Script Features

- Support for all new comprehensive tags
- JSON context validation capability
- Pattern consistency checking
- Reference integrity validation
- Training hash correlation support
- Audit trail verification

Future enhancements may include:

- JSON schema validation for AI_CONTEXT blocks
- Pattern analysis and recommendation tools
- Training hash verification against known datasets
- Automated reference link checking
- Integration with external issue tracking systems
- AI_CONTEXT extraction for machine learning analysis

## Support

For questions about the enhanced AI breadcrumb system:

- See the complete specification in `compiler/include/aros/ai_metadata.h`
- Review comprehensive examples in `examples/ai_breadcrumb_enhanced_demo.c`
- Check existing usage throughout the AROS codebase
- Use `scripts/validate_ai_breadcrumbs.sh` for validation
- Consult the AROS development team for guidance on complex implementations

This enhanced system evolves with the codebase and AI development practices - contribute improvements and suggestions to help enhance its effectiveness and support for longer AI context history.
