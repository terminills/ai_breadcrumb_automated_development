# Integrating Thought Process Logging into AI Agent

## Quick Start Integration

This guide shows how to integrate the thought process logging system into your AI autonomous development agent.

## Basic Integration

### 1. Initialize Components

```python
from src.compiler_loop import CompilerLoop, ErrorTracker, ReasoningTracker
from src.breadcrumb_parser import BreadcrumbParser

# Initialize all components
compiler = CompilerLoop("aros-src", "logs/compile")
error_tracker = ErrorTracker("logs/errors")
reasoning_tracker = ReasoningTracker("logs/reasoning")
parser = BreadcrumbParser()
```

### 2. Add to Agent Loop

```python
def ai_agent_iteration(task):
    """Single iteration of the AI agent with reasoning logging"""
    
    # Parse breadcrumbs for context
    breadcrumbs = parser.get_breadcrumbs_by_phase(task.phase)
    breadcrumb_patterns = [bc.pattern for bc in breadcrumbs if bc.pattern]
    
    # START: Capture reasoning
    reasoning_id = reasoning_tracker.start_reasoning(
        task_id=task.id,
        phase="analyzing",
        breadcrumbs_consulted=breadcrumb_patterns,
        error_context=task.error_message if hasattr(task, 'error_message') else None,
        files_considered=task.files
    )
    
    # AI analyzes the problem
    reasoning_tracker.add_reasoning_step("Analyzing error context...")
    reasoning_tracker.add_reasoning_step("Consulting breadcrumbs...")
    
    # Identify applicable patterns
    for bc in breadcrumbs:
        if bc.pattern:
            reasoning_tracker.add_pattern(bc.pattern)
            reasoning_tracker.add_reasoning_step(f"Pattern {bc.pattern} identified")
    
    # Make decision
    decision = make_ai_decision(task, breadcrumbs)
    
    reasoning_tracker.set_decision(
        decision_type=decision['type'],
        approach=decision['approach'],
        confidence=decision['confidence'],
        complexity=decision['complexity'],
        raw_thought=decision['explanation']
    )
    
    # Generate and test code
    success, iterations = generate_and_compile(task, decision)
    
    # COMPLETE: Record outcome
    reasoning_tracker.complete_reasoning(
        reasoning_id,
        success=success,
        iterations=iterations
    )
    
    return success
```

### 3. Prompt Enhancement for AI Model

Add this to your AI model prompt:

```
Before implementing a fix, provide your reasoning in JSON format:

{
  "breadcrumbs_consulted": ["AI_PATTERN: SHADER_V2", "AI_NOTE: ..."],
  "error_analysis": "what the error means",
  "reasoning_steps": [
    "step 1: analyze error",
    "step 2: identify pattern",
    "step 3: choose approach"
  ],
  "patterns_to_apply": ["SHADER_V2"],
  "chosen_approach": "description of approach",
  "confidence": 0.85,
  "complexity": "MEDIUM"
}

Then implement the fix based on this reasoning.
```

### 4. Parse AI Response

```python
def parse_ai_reasoning(ai_response):
    """Extract reasoning from AI response"""
    # Extract JSON from AI response
    reasoning_json = extract_json(ai_response)
    
    # Log to reasoning tracker
    for step in reasoning_json.get('reasoning_steps', []):
        reasoning_tracker.add_reasoning_step(step)
    
    for pattern in reasoning_json.get('patterns_to_apply', []):
        reasoning_tracker.add_pattern(pattern)
    
    reasoning_tracker.set_decision(
        decision_type=reasoning_json.get('decision_type', 'unknown'),
        approach=reasoning_json.get('chosen_approach', ''),
        confidence=reasoning_json.get('confidence', 0.5),
        complexity=reasoning_json.get('complexity', 'MEDIUM'),
        raw_thought=reasoning_json.get('error_analysis', '')
    )
    
    return reasoning_json
```

## Advanced Usage

### Monitoring Reasoning Quality

```python
def monitor_reasoning_quality():
    """Monitor and report on reasoning quality"""
    stats = reasoning_tracker.get_statistics()
    
    print(f"Success Rate: {stats['success_rate']:.1%}")
    
    # Alert on low confidence failures
    failed = reasoning_tracker.get_failed_reasoning_patterns()
    low_confidence_failures = [
        f for f in failed 
        if f.get('confidence', 1.0) < 0.6
    ]
    
    if low_confidence_failures:
        print("⚠️  Low confidence failures detected:")
        for failure in low_confidence_failures:
            print(f"  - {failure['task_id']}: {failure['confidence']:.0%} confidence")
            print(f"    Missing: {identify_missing_breadcrumbs(failure)}")
```

### Adaptive Learning

```python
def improve_from_reasoning():
    """Use reasoning data to improve breadcrumbs"""
    
    # Find patterns with low success rates
    pattern_stats = reasoning_tracker.get_pattern_statistics()
    
    for pattern, stats in pattern_stats.items():
        if stats['success_rate'] < 0.5 and stats['uses'] >= 3:
            print(f"⚠️  Pattern {pattern} has low success rate: {stats['success_rate']:.1%}")
            
            # Get failed reasoning using this pattern
            failed = reasoning_tracker.query_by_pattern(pattern)
            failed = [f for f in failed if not f.get('success', True)]
            
            # Analyze what was missing
            for failure in failed:
                print(f"  Failure: {failure['task_id']}")
                print(f"  Breadcrumbs: {failure['breadcrumbs_consulted']}")
                print(f"  → Suggestion: Add more context to {pattern} breadcrumbs")
```

### Real-time Dashboard Integration

The reasoning data automatically appears in the web dashboard at `http://localhost:5000`.

Monitor these sections:
- **AI Currently Thinking**: See live reasoning
- **Recent Decisions**: View historical outcomes
- **Pattern Usage**: Identify effective patterns

### Querying Reasoning Data

```python
# Find reasoning by phase
analyzing_phase = reasoning_tracker.query_by_phase("analyzing")

# Find successful vs failed reasoning
all_reasoning = reasoning_tracker.get_recent_reasoning(limit=100)
successful = [r for r in all_reasoning if r.get('success')]
failed = [r for r in all_reasoning if r.get('success') is False]

# Analyze patterns
for pattern in ['SHADER_V2', 'MEMORY_V3', 'DMA_SAFE']:
    pattern_reasoning = reasoning_tracker.query_by_pattern(pattern)
    success_rate = sum(1 for r in pattern_reasoning if r.get('success')) / len(pattern_reasoning)
    print(f"{pattern}: {success_rate:.1%} success rate")
```

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

## Benefits

1. **Debugging**: Understand why AI made certain decisions
2. **Research**: Quantify breadcrumb effectiveness
3. **Improvement**: Identify missing information
4. **Transparency**: Full audit trail of AI decisions

## Example Output

Each reasoning event produces a detailed JSON log:

```json
{
  "timestamp": "2025-10-15T14:32:18Z",
  "task_id": "shader_compilation",
  "phase": "analyzing",
  "breadcrumbs_consulted": ["AI_PATTERN: SHADER_V2"],
  "reasoning_steps": [
    "Error indicates missing NIR function",
    "Need NIR parser before LLVM"
  ],
  "patterns_identified": ["SHADER_V2"],
  "decision_type": "add_nir_parser",
  "approach_chosen": "follow_linux_pattern",
  "confidence": 0.85,
  "success": true,
  "iterations_taken": 3
}
```

## See Also

- [THOUGHT_PROCESS_LOGGING.md](THOUGHT_PROCESS_LOGGING.md) - Complete documentation
- [README.md](../README.md) - Main project documentation
- [demo_reasoning.py](../scripts/demo_reasoning.py) - Working example
