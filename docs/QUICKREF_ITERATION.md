# Quick Reference: Enhanced Copilot Iteration

## Key Features

### 1. Checkpoint/Resume
```python
# Save checkpoint
checkpoint_path = session.save_checkpoint("feature_v1")

# Load checkpoint
session.load_checkpoint(checkpoint_path)

# List checkpoints
checkpoints = session.list_checkpoints()
```

### 2. Adaptive Retries
```python
iteration = CopilotStyleIteration(..., max_retries=3, adaptive_retries=True)
result = iteration.run_interactive_iteration(task, retry_on_failure=True)
print(f"Adaptive retries used: {result['retry_count']}")
```

### 3. Iteration History
```python
# View history
for entry in iteration.iteration_history:
    print(f"Iteration {entry['iteration']}: {entry['success']}")

# Save/Load state
iteration.save_iteration_state()
iteration.load_iteration_state()
```

### 4. Pattern Learning
```python
# Get learned patterns
patterns = iteration.get_learned_patterns()
print(f"Overall success rate: {patterns['overall_success_rate']:.1%}")
```

## Previously Available Features

### 1. Retry Logic
```python
iteration = CopilotStyleIteration(..., max_retries=3)
result = iteration.run_interactive_iteration(task, retry_on_failure=True)
print(f"Retries: {result['retry_count']}")
```

### 2. Reasoning Tracking
```python
stats = iteration.reasoning_tracker.get_statistics()
print(f"Success rate: {stats['success_rate']:.1%}")
recent = iteration.reasoning_tracker.get_recent_reasoning(limit=5)
```

### 3. Error Similarity
```python
similar = error_tracker.find_similar_errors("undefined reference...")
suggestions = error_tracker.get_resolution_suggestions("error message")
```

### 4. Iteration Metrics
```python
metrics = session.get_iteration_metrics()
print(f"Total attempts: {metrics['total_attempts']}")
print(f"Success rate: {metrics['success_rate']:.1%}")
```

### 5. Performance Monitoring
```python
result = iteration.run_interactive_iteration(task)
print(f"Total time: {result['total_time']:.2f}s")
for phase, timing in result['timings'].items():
    print(f"{phase}: {timing:.2f}s")
```

### 6. Streaming Generation
```python
generation = session.generate(use_exploration=True, stream=True)
print(f"Streamed: {generation['streamed']}")
```

## Common Tasks

### Check Success Rate
```python
stats = iteration.reasoning_tracker.get_statistics()
if stats['success_rate'] < 0.5:
    print("Warning: Low success rate")
```

### Get Error Suggestions
```python
for error in compile_result['errors']:
    suggestions = iteration.error_tracker.get_resolution_suggestions(error)
    for s in suggestions[:3]:
        print(f"- {s}")
```

### Mark Error Resolved
```python
error_hash = tracker.track_error(error_message, context)
tracker.mark_resolved(error_hash, "Solution description")
```

### Analyze Patterns
```python
patterns = iteration.reasoning_tracker.get_pattern_statistics()
for pattern, stats in patterns.items():
    print(f"{pattern}: {stats['success_rate']:.1%} ({stats['uses']} uses)")
```

### Get Recent Reasoning
```python
recent = iteration.reasoning_tracker.get_recent_reasoning(limit=10)
for r in recent:
    print(f"Task: {r['task_id']}, Success: {r['success']}")
```

## Configuration

### Basic Setup
```python
from src.copilot_iteration import CopilotStyleIteration

iteration = CopilotStyleIteration(
    aros_path='aros-src',
    project_name='radeonsi',
    log_path='logs/copilot',
    max_iterations=10,
    max_retries=3
)
```

### Run With Retries
```python
result = iteration.run_interactive_iteration(
    task={'phase': 'DEVELOPMENT', 'strategy': 'Implement feature'},
    enable_exploration=True,
    retry_on_failure=True
)
```

### Interactive Session
```python
from src.interactive_session import SessionManager
from src.local_models import LocalModelLoader

loader = LocalModelLoader()
session = SessionManager(loader, 'aros-src', 'logs')

session.start_session("Task", {'phase': 'DEVELOPMENT'})
exploration = session.explore("search query")
generation = session.generate(stream=True)
metrics = session.get_iteration_metrics()
session.end_session(status='completed')
```

## Testing

Run all tests:
```bash
python3 tests/test_copilot_iteration.py
```

Run specific component tests:
```python
# In Python
from tests.test_copilot_iteration import *

test_reasoning_tracker()
test_error_similarity()
test_iteration_context()
test_performance_tracking()
```

## Debugging

### View Reasoning Chain
```python
current = iteration.reasoning_tracker.get_current_reasoning()
if current:
    print("Steps:", current['reasoning_steps'])
    print("Patterns:", current['patterns_identified'])
    print("Decision:", current['approach_chosen'])
```

### Check Error Database
```python
stats = iteration.error_tracker.get_statistics()
print(f"Total errors: {stats['total_unique_errors']}")
print(f"Resolved: {stats['resolved_errors']}")
print(f"Patterns: {stats['patterns']}")
```

### Session Summary
```python
summary = session.get_session_summary()
print(f"ID: {summary['id']}")
print(f"Turns: {summary['turns']}")
print(f"Generations: {summary['generations']}")
print(f"Context: {summary['iteration_context']}")
```

## Performance Tips

1. **Use retries for complex tasks**: `max_retries=3` or higher
2. **Enable streaming for interactivity**: `stream=True`
3. **Monitor success rate regularly**: Check reasoning stats
4. **Mark resolved errors**: Help future iterations
5. **Keep context clean**: Review iteration metrics periodically

## Troubleshooting

### Low Success Rate
```python
stats = iteration.reasoning_tracker.get_statistics()
if stats['success_rate'] < 0.5:
    # Check failed reasoning patterns
    failed = iteration.reasoning_tracker.get_failed_reasoning_patterns()
    for f in failed:
        print(f"Failed: {f['task_id']}, Reason: {f['reasoning_steps']}")
```

### Slow Iterations
```python
# Check phase timings
result = iteration.run_interactive_iteration(task)
slow_phases = {k: v for k, v in result['timings'].items() if v > 10}
print(f"Slow phases: {slow_phases}")
```

### Repeated Errors
```python
# Find recurring errors
stats = tracker.get_statistics()
patterns = stats['patterns']
for pattern, count in patterns.items():
    if count > 5:
        print(f"Recurring: {pattern} ({count} times)")
```

## API Reference

### CopilotStyleIteration
- `__init__(aros_path, project_name, log_path, max_iterations, max_retries)`
- `run()` - Run complete iteration loop
- `run_interactive_iteration(task, enable_exploration, retry_on_failure)` - Single iteration

### SessionManager
- `start_session(task_description, context)`
- `explore(query, max_files)`
- `reason(specific_question)`
- `generate(prompt, use_exploration, stream)`
- `review(code, errors)`
- `iterate(feedback, errors)`
- `get_session_summary()`
- `get_iteration_metrics()`
- `end_session(status, summary)`

### ErrorTracker
- `track_error(error_message, context)`
- `mark_resolved(error_hash, resolution, fix_commit)`
- `find_similar_errors(error_message, limit)`
- `get_resolution_suggestions(error_message)`
- `get_statistics()`

### ReasoningTracker
- `start_reasoning(task_id, phase, breadcrumbs_consulted, error_context, files_considered)`
- `add_reasoning_step(step)`
- `add_pattern(pattern)`
- `set_decision(decision_type, approach, confidence, complexity, raw_thought)`
- `complete_reasoning(reasoning_id, success, iterations)`
- `get_statistics()`
- `get_pattern_statistics()`
- `get_recent_reasoning(limit)`

## Logging

All components log to the configured log path:
- `logs/copilot/sessions/*.json` - Session data
- `logs/copilot/errors/*.json` - Error database
- `logs/copilot/reasoning/*.json` - Reasoning chains
- `logs/copilot/compile/*.log` - Compilation logs

View logs:
```bash
# Recent sessions
ls -lt logs/copilot/sessions/ | head -5

# Error database
cat logs/copilot/errors/error_database.json | jq

# Recent reasoning
ls -lt logs/copilot/reasoning/ | head -5
```
