# AI Thought Process Logging

## Overview

The AI Thought Process Logging system captures and analyzes the AI's reasoning during autonomous development. This provides critical insights into how the AI makes decisions, applies patterns, and solves problems.

## Why This Matters

**Without thought process logging:**
- You see: Error → Fix → Success
- You don't see: WHY the AI chose that fix

**With thought process logging:**
- You see: Error → AI reasoning → Decision → Fix → Success
- You understand: The AI's problem-solving process

## What It Captures

### AI Internal Reasoning

The system captures:

1. **Context**: What information the AI is working with
   - Breadcrumbs consulted
   - Error messages analyzed
   - Files considered

2. **Reasoning Chain**: How the AI thinks through the problem
   - Step-by-step logical progression
   - Patterns identified
   - Linux/AROS references used

3. **Decision**: What the AI chose to do
   - Type of action (e.g., "add_nir_parser")
   - Approach taken
   - Confidence level (0.0 - 1.0)
   - Estimated complexity

4. **Outcome**: Results of the decision
   - Success/failure
   - Number of iterations required
   - Completion timestamp

## Usage

### In Python Code

```python
from src.compiler_loop import ReasoningTracker

# Initialize tracker
tracker = ReasoningTracker("logs/reasoning")

# Start capturing reasoning
reasoning_id = tracker.start_reasoning(
    task_id="shader_compilation",
    phase="analyzing",
    breadcrumbs_consulted=[
        "AI_PATTERN: SHADER_V2",
        "AI_NOTE: NIR not implemented",
        "Linux ref: si_shader.c:245"
    ],
    error_context="undefined reference to 'nir_shader_get_entrypoint'",
    files_considered=["si_shader.c", "si_shader.h"]
)

# Add reasoning steps
tracker.add_reasoning_step("Error indicates missing NIR function")
tracker.add_reasoning_step("Breadcrumb says NIR parsing not implemented")
tracker.add_reasoning_step("Linux reference shows pattern to follow")
tracker.add_reasoning_step("Need NIR parser before LLVM")

# Add patterns identified
tracker.add_pattern("SHADER_V2")
tracker.add_pattern("NIR_INTEGRATION")

# Record decision
tracker.set_decision(
    decision_type="add_nir_parser",
    approach="follow_linux_pattern",
    confidence=0.85,
    complexity="MEDIUM",
    raw_thought="Following Linux pattern in si_shader.c lines 245-267"
)

# Complete reasoning with outcome
tracker.complete_reasoning(
    reasoning_id,
    success=True,
    iterations=3
)
```

### Viewing Current Reasoning

```python
# Get what AI is currently thinking about
current = tracker.get_current_reasoning()

if current:
    print(f"Task: {current['task_id']}")
    print(f"Phase: {current['phase']}")
    print(f"Decision: {current['decision_type']}")
    print(f"Confidence: {current['confidence']:.1%}")
```

### Analyzing Patterns

```python
# Get pattern usage statistics
pattern_stats = tracker.get_pattern_statistics()

for pattern, stats in pattern_stats.items():
    print(f"{pattern}:")
    print(f"  Uses: {stats['uses']}")
    print(f"  Success Rate: {stats['success_rate']:.1%}")
```

### Breadcrumb Effectiveness

```python
# Analyze which breadcrumbs are most effective
breadcrumb_effectiveness = tracker.get_breadcrumb_effectiveness()

for breadcrumb, stats in breadcrumb_effectiveness.items():
    print(f"{breadcrumb}:")
    print(f"  Uses: {stats['uses']}")
    print(f"  Success Rate: {stats['success_rate']:.1%}")
```

## API Endpoints

The web UI provides REST API endpoints for accessing reasoning data:

### GET `/api/reasoning/current`
Returns the current AI reasoning in progress.

**Response:**
```json
{
  "timestamp": "2025-10-15T14:32:18Z",
  "task_id": "shader_compilation",
  "phase": "analyzing",
  "breadcrumbs_consulted": ["AI_PATTERN: SHADER_V2"],
  "error_context": "undefined reference...",
  "reasoning_steps": [
    "Error indicates missing function",
    "Need to implement X before Y"
  ],
  "decision_type": "add_nir_parser",
  "confidence": 0.85
}
```

### GET `/api/reasoning/history?limit=10`
Returns recent reasoning entries.

### GET `/api/reasoning/stats`
Returns comprehensive statistics including:
- Total reasoning events
- Success/failure counts
- Pattern usage statistics
- Breadcrumb effectiveness

### GET `/api/reasoning/patterns`
Returns pattern usage statistics.

### GET `/api/reasoning/breadcrumbs`
Returns breadcrumb effectiveness analysis.

### GET `/api/reasoning/failed`
Returns failed reasoning patterns for debugging.

### GET `/api/reasoning/by_phase/<phase>`
Query reasoning entries by phase (analyzing, deciding, implementing, evaluating).

### GET `/api/reasoning/by_pattern/<pattern>`
Query reasoning entries that used a specific pattern.

## Dashboard Integration

### Real-Time Panels

The dashboard includes several new panels:

#### 1. AI Reasoning Card
Shows high-level statistics:
- Total reasoning events
- Success rate
- Number of patterns used

#### 2. AI Currently Thinking About
Real-time display of active reasoning:
- Current task and phase
- Breadcrumbs being consulted
- Reasoning steps as they happen
- Decision and confidence level
- Patterns identified

#### 3. Recent Decisions & Reasoning
Historical view of recent reasoning:
- Task and outcome (✓ success, ⚠ failure, ⏳ in progress)
- Decision type and approach
- Confidence levels
- Patterns used

#### 4. Pattern Usage Statistics
Shows pattern effectiveness:
- Most used patterns
- Success rates per pattern
- Usage frequency

## Data Storage

Reasoning data is stored in two formats:

1. **Individual JSON files**: `logs/reasoning/reasoning_<id>.json`
   - Each reasoning event stored separately
   - Easy to search and analyze
   - Queryable by filesystem

2. **Metadata database**: `logs/reasoning/reasoning_database.json`
   - Aggregate statistics
   - Quick access to totals
   - Performance metrics

## Use Cases

### For Debugging
When the AI gets stuck in a loop:
1. Check reasoning history
2. Identify where logic breaks down
3. Find missing breadcrumb information
4. Update breadcrumbs, not code

### For Research
Understanding AI behavior:
- How does it use breadcrumbs?
- What patterns does it follow?
- When does it succeed vs. fail?
- What makes autonomous development work?

### For Improvement
Iterating the breadcrumb specification:
- Which breadcrumb fields are most useful?
- What information is the AI missing?
- What patterns emerge repeatedly?
- How to enhance the system?

### For Analysis
Query the data:

```python
# Find all reasoning using a specific pattern
shader_reasoning = tracker.query_by_pattern("SHADER_V2")

# Find failed reasoning for debugging
failed = tracker.get_failed_reasoning_patterns()

# Analyze by development phase
analyzing_phase = tracker.query_by_phase("analyzing")
```

## Metrics and Analysis

### Pattern Recognition
Query logs to find:
- "Show all times AI used SHADER_V2 pattern"
- "What breadcrumbs led to successful fixes?"
- "Which reasoning chains resulted in loops?"

### Breadcrumb Effectiveness
Measure impact:
- Features with detailed breadcrumbs vs. sparse
- Success rate by breadcrumb type
- Time to completion with different patterns

### Model Comparison
If testing different models:
- Compare reasoning quality
- See which model uses breadcrumbs better
- Identify capability differences

## Configuration

In `config/config.json`:

```json
{
  "compiler_loop": {
    "reasoning_log_path": "logs/reasoning",
    "capture_thought_process": true
  }
}
```

## Example Output

### Reasoning Log File
```json
{
  "timestamp": "2025-10-15T14:32:18Z",
  "task_id": "shader_compilation",
  "phase": "analyzing",
  "breadcrumbs_consulted": [
    "AI_PATTERN: SHADER_V2",
    "AI_NOTE: NIR not implemented",
    "Linux ref: si_shader.c:245"
  ],
  "error_context": "undefined reference to 'nir_shader_get_entrypoint'",
  "files_considered": ["si_shader.c", "si_shader.h"],
  "reasoning_steps": [
    "Error indicates missing NIR function",
    "Breadcrumb says NIR parsing not implemented",
    "Linux reference shows pattern to follow",
    "Need NIR parser before LLVM"
  ],
  "patterns_identified": ["SHADER_V2", "NIR_INTEGRATION"],
  "decision_type": "add_nir_parser",
  "approach_chosen": "follow_linux_pattern",
  "confidence": 0.85,
  "estimated_complexity": "MEDIUM",
  "success": true,
  "iterations_taken": 3,
  "completion_time": "2025-10-15T14:35:42Z"
}
```

## Benefits

### Quantitative Proof
With thought process logging, you can demonstrate:
- "87% of successful fixes referenced AI_PATTERN breadcrumbs"
- "Breadcrumbs reduced reasoning steps from 8.3 to 3.1"
- "Pattern-based decisions had 91% success rate"

### Complete Audit Trail
- Every decision is logged
- Full reasoning chain captured
- Pattern application documented
- Outcome tracked

### Foundation for Distributed AI
When scaling to multiple agents:
- Understand decision conflicts
- See why agents made different choices
- Debug coordination issues
- Improve orchestration

## Future Enhancements

1. **Reasoning Quality Metrics**: Score reasoning chains
2. **Reasoning Templates**: Common patterns for different scenarios
3. **Learning from Failures**: Auto-improve based on failed reasoning
4. **Collective Intelligence**: Share successful patterns across agents
5. **Real-time Reasoning Visualization**: Watch AI think in real-time
6. **Reasoning Replay**: Step through historical decisions

## Integration Example

Complete example in an AI agent loop:

```python
from src.compiler_loop import CompilerLoop, ErrorTracker, ReasoningTracker
from src.breadcrumb_parser import BreadcrumbParser

# Initialize components
compiler = CompilerLoop("aros-src", "logs/compile")
error_tracker = ErrorTracker("logs/errors")
reasoning_tracker = ReasoningTracker("logs/reasoning")
parser = BreadcrumbParser()

# Agent iteration
def ai_iteration(task):
    # Parse breadcrumbs
    breadcrumbs = parser.get_breadcrumbs_by_phase(task.phase)
    
    # Start reasoning
    reasoning_id = reasoning_tracker.start_reasoning(
        task_id=task.id,
        phase="analyzing",
        breadcrumbs_consulted=[bc.pattern for bc in breadcrumbs],
        error_context=task.error,
        files_considered=task.files
    )
    
    # AI thinks through the problem
    reasoning_tracker.add_reasoning_step("Analyzing error context...")
    reasoning_tracker.add_reasoning_step("Identified relevant pattern...")
    
    # Identify patterns
    for bc in breadcrumbs:
        if bc.pattern:
            reasoning_tracker.add_pattern(bc.pattern)
    
    # Make decision
    reasoning_tracker.set_decision(
        decision_type="implement_feature",
        approach="follow_breadcrumb_pattern",
        confidence=0.75
    )
    
    # Generate and compile code
    success = generate_and_compile(task)
    
    # Complete reasoning
    reasoning_tracker.complete_reasoning(
        reasoning_id,
        success=success,
        iterations=1
    )
    
    return success
```

## See Also

- [README.md](README.md) - Main project documentation
- [SETUP.md](SETUP.md) - Setup and configuration
- [Breadcrumb Parser](src/breadcrumb_parser/parser.py) - Breadcrumb parsing
- [Compiler Loop](src/compiler_loop/compiler.py) - Compilation system
- [Error Tracker](src/compiler_loop/error_tracker.py) - Error tracking
