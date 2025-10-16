# Advanced Copilot Iteration Features

## Overview

This document describes the advanced features added to the Copilot Iteration Loop system in the latest enhancement iteration. These features build upon the existing checkpoint/resume, adaptive retries, and pattern learning capabilities to provide an even more intelligent and robust development assistant.

## New Features

### 1. Pattern Recommendations 🎯

Intelligently suggest optimal approaches based on learned patterns from previous iterations.

#### What It Does

The pattern recommendation system analyzes your iteration history and learned patterns to provide:
- **Success Probability**: Estimated likelihood of success for a given task
- **Suggested Retry Count**: Optimized retry count based on historical data and task complexity
- **Estimated Completion Time**: Predicted time to complete the task
- **Similar Tasks**: List of similar previously completed tasks
- **Best Practices**: Actionable recommendations based on patterns

#### Usage

```python
from src.copilot_iteration import CopilotStyleIteration

iteration = CopilotStyleIteration(
    aros_path='aros-src',
    project_name='radeonsi',
    log_path='logs/copilot',
    max_iterations=10
)

# Get recommendation for a specific phase
recommendation = iteration.get_pattern_recommendation(
    phase='SHADER_COMPILATION',
    complexity='MEDIUM'  # LOW, MEDIUM, HIGH, or CRITICAL
)

print(f"Success Probability: {recommendation['success_probability']*100:.0f}%")
print(f"Suggested Retries: {recommendation['suggested_retries']}")
print(f"Estimated Time: {recommendation['estimated_time']:.0f}s")

for practice in recommendation['best_practices']:
    print(f"• {practice}")
```

#### Complexity Levels

The system adjusts recommendations based on task complexity:

| Complexity | Retry Multiplier | Time Multiplier | When to Use |
|------------|------------------|-----------------|-------------|
| LOW | 0.7x | 0.8x | Simple, well-understood tasks |
| MEDIUM | 1.0x | 1.0x | Standard tasks |
| HIGH | 1.3x | 1.4x | Complex tasks with dependencies |
| CRITICAL | 1.5x | 2.0x | Mission-critical, high-risk tasks |

#### Benefits

- **Informed Decisions**: Know what to expect before starting
- **Resource Planning**: Better estimate time and effort required
- **Risk Assessment**: Understand success probability upfront
- **Learning from History**: Leverage accumulated knowledge

---

### 2. Checkpoint Diff 📊

Compare two checkpoints to see exactly what changed between development sessions.

#### What It Does

The checkpoint diff functionality provides:
- **Added Keys**: New data added in the second checkpoint
- **Removed Keys**: Data removed from the first checkpoint
- **Changed Values**: Values that changed between checkpoints
- **Iteration Context Changes**: Detailed diff of iteration context
- **Human-Readable Summary**: Clear explanation of changes

#### Usage

```python
from src.interactive_session import SessionManager
from src.local_models import LocalModelLoader

loader = LocalModelLoader()
session = SessionManager(loader, 'aros-src', 'logs')

# Create first checkpoint
session.start_session("Implement feature", {'phase': 'DEVELOPMENT'})
session.iteration_context['step'] = 1
cp1 = session.save_checkpoint("before_refactor")

# Make changes...
session.iteration_context['step'] = 2
session.iteration_context['refactored'] = True
cp2 = session.save_checkpoint("after_refactor")

# Compare
diff = session.compare_checkpoints(cp1, cp2)

print("\n".join(diff['summary']))

for key, change in diff['iteration_context_diff'].items():
    print(f"{key}: {change['old']} → {change['new']}")
```

#### Use Cases

- **Code Review**: Understand what changed during a session
- **Debugging**: Track down when issues were introduced
- **Documentation**: Document progress and changes
- **Experimentation**: Compare different approaches

#### Example Output

```
Comparing before_refactor → after_refactor
Changed 3 values
  - context: {'phase': 'DEVELOPMENT'} → {'phase': 'DEVELOPMENT', 'refactored': True}
Iteration context changes: 2 items
```

---

### 3. Pattern Export/Import 📦

Share learned patterns between projects and team members.

#### What It Does

Export and import learned patterns to:
- **Share Knowledge**: Transfer successful patterns to other projects
- **Collaborative Learning**: Build shared pattern libraries across teams
- **Bootstrap New Projects**: Start new projects with proven patterns
- **Backup Patterns**: Save and restore pattern databases

#### Export Patterns

```python
iteration = CopilotStyleIteration(
    aros_path='aros-src',
    project_name='radeonsi',
    log_path='logs/copilot',
    max_iterations=10
)

# After accumulating patterns through iterations...
export_path = iteration.export_learned_patterns('patterns/radeonsi_patterns.json')
print(f"Exported to: {export_path}")
```

#### Import Patterns

```python
# In another project
iteration2 = CopilotStyleIteration(
    aros_path='aros-src',
    project_name='nouveau',
    log_path='logs/copilot2',
    max_iterations=10
)

# Import with merge (combines with existing patterns)
success = iteration2.import_learned_patterns(
    'patterns/radeonsi_patterns.json',
    merge=True
)

# Or import with replace (replaces all patterns)
success = iteration2.import_learned_patterns(
    'patterns/radeonsi_patterns.json',
    merge=False
)
```

#### Merge Behavior

When `merge=True`, the system intelligently combines patterns:

1. **New Phases**: Added directly to the pattern database
2. **Existing Phases**: Values are merged using weighted averages based on attempt counts
3. **Approaches**: Combined lists are deduplicated

Example merge:
```
Project A: SHADER_COMPILATION (8/10 success, 1.5 avg retries, 45s avg time)
Project B: SHADER_COMPILATION (5/8 success, 2.0 avg retries, 50s avg time)

Merged: SHADER_COMPILATION (13/18 success, 1.7 avg retries, 47s avg time)
```

#### Pattern File Format

```json
{
  "project_name": "radeonsi",
  "export_time": "2025-10-16T01:30:00Z",
  "learned_patterns": {
    "SHADER_COMPILATION": {
      "successes": 15,
      "total_attempts": 18,
      "avg_retries": 1.3,
      "avg_time": 42.0,
      "common_approaches": ["LLVM_BACKEND", "SPIR_V"]
    }
  },
  "total_iterations": 50,
  "overall_success_rate": 0.83,
  "metadata": {
    "version": "1.0",
    "format": "copilot_iteration_patterns"
  }
}
```

---

### 4. Enhanced Analytics 📈

Comprehensive analytics and reporting for iteration performance.

#### What It Does

The analytics engine provides:
- **Performance Summary**: Overall metrics and statistics
- **Phase Analysis**: Per-phase performance breakdown
- **Time Series Analysis**: Trends over iterations
- **Error Analysis**: Common errors and failure patterns
- **Actionable Recommendations**: AI-generated suggestions

#### Get Analytics

```python
iteration = CopilotStyleIteration(
    aros_path='aros-src',
    project_name='radeonsi',
    log_path='logs/copilot',
    max_iterations=10
)

# Run some iterations...
iteration.run()

# Get analytics engine
analytics = iteration.get_analytics()
```

#### Performance Summary

```python
summary = analytics.get_performance_summary()

print(f"Total Iterations: {summary['total_iterations']}")
print(f"Success Rate: {summary['success_rate']*100:.1f}%")
print(f"Average Time: {summary['average_time']:.1f}s")
print(f"Average Retries: {summary['average_retries']:.1f}")

# Phase-specific timings
for phase, timings in summary['phase_timings'].items():
    print(f"{phase}: {timings['average']:.1f}s avg")
```

#### Phase Analysis

```python
# Analyze specific phase
analysis = analytics.get_phase_analysis('SHADER_COMPILATION')

print(f"Success Rate: {analysis['success_rate']*100:.0f}%")
print(f"Trend: {analysis['trend']}")  # improving, declining, stable
print(f"Avg Retries: {analysis['avg_retries']:.1f}")
print(f"Avg Time: {analysis['avg_time']:.1f}s")

# Analyze all phases
all_phases = analytics.get_phase_analysis()
for phase, data in all_phases.items():
    print(f"{phase}: {data['success_rate']*100:.0f}% success")
```

#### Error Analysis

```python
error_analysis = analytics.get_error_analysis()

print(f"Total Failures: {error_analysis['total_failures']}")

# Most common errors
for error in error_analysis['most_common_errors']:
    print(f"  {error['type']}: {error['count']} times")

# Phases with most errors
for phase_err in error_analysis['phases_with_most_errors']:
    print(f"  {phase_err['phase']}: {phase_err['count']} failures")
```

#### Get Recommendations

```python
recommendations = analytics.get_recommendations()

for rec in recommendations:
    print(f"• {rec}")
```

Example recommendations:
```
⚠️ Low success rate (45%). Consider increasing exploration depth or adjusting model parameters.
⏱️ Long average iteration time (120s). Consider optimizing slow phases or using smaller models.
📈 Recent success rate is improving! Current approach is learning and adapting well.
⚠️ Phase 'MEMORY_MANAGER' has low success rate (30%). Consider specialized approach.
```

#### Generate Full Report

```python
# Generate and save comprehensive report
report = iteration.generate_analytics_report('reports/iteration_report.txt')

# Or just print to console
report = iteration.generate_analytics_report()
print(report)
```

Report includes:
- Performance summary with detailed metrics
- Time breakdown by phase
- Phase-by-phase analysis with trends
- Error analysis with common patterns
- Actionable recommendations

---

## Integration Examples

### Complete Workflow with All Features

```python
from src.copilot_iteration import CopilotStyleIteration
import sys

def main():
    # Initialize with state recovery
    iteration = CopilotStyleIteration(
        aros_path='aros-src',
        project_name='radeonsi',
        log_path='logs/copilot',
        max_iterations=20,
        max_retries=3,
        adaptive_retries=True
    )
    
    # Try to resume previous state
    if iteration.load_iteration_state():
        print("Resuming from previous session")
        
        # Import patterns from successful project
        iteration.import_learned_patterns('patterns/proven_patterns.json', merge=True)
    
    try:
        # Before starting, get recommendations
        task = {'phase': 'SHADER_COMPILATION', 'description': 'Implement SPIR-V compiler'}
        recommendation = iteration.get_pattern_recommendation('SHADER_COMPILATION', 'HIGH')
        
        print(f"Starting task with:")
        print(f"  Expected success: {recommendation['success_probability']*100:.0f}%")
        print(f"  Estimated time: {recommendation['estimated_time']:.0f}s")
        print(f"  Recommended retries: {recommendation['suggested_retries']}")
        
        # Run iterations
        summary = iteration.run()
        
        # Generate analytics report
        analytics = iteration.get_analytics()
        report = analytics.generate_report('reports/final_report.txt')
        print("\nAnalytics Report:")
        print(report)
        
        # Export successful patterns for others
        if summary['successful'] / summary['total_iterations'] > 0.7:
            export_path = iteration.export_learned_patterns('patterns/shader_patterns.json')
            print(f"\nExported successful patterns to: {export_path}")
        
        # Save final state
        iteration.save_iteration_state()
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted - saving state...")
        
        # Save checkpoint for resume
        if iteration.session_manager.current_session:
            checkpoint = iteration.session_manager.save_checkpoint("interrupted")
            print(f"Checkpoint saved: {checkpoint}")
        
        # Save iteration state
        iteration.save_iteration_state()
        
        return 130

if __name__ == '__main__':
    sys.exit(main())
```

---

## CLI Integration

These features can also be accessed via command-line:

```bash
# Get pattern recommendations
python3 -c "
from src.copilot_iteration import CopilotStyleIteration
it = CopilotStyleIteration('aros-src', 'radeonsi', 'logs', 10)
it.load_iteration_state()
rec = it.get_pattern_recommendation('SHADER_COMPILATION', 'HIGH')
print(f'Success probability: {rec[\"success_probability\"]*100:.0f}%')
print(f'Suggested retries: {rec[\"suggested_retries\"]}')
"

# Generate analytics report
python3 -c "
from src.copilot_iteration import CopilotStyleIteration
it = CopilotStyleIteration('aros-src', 'radeonsi', 'logs', 10)
it.load_iteration_state()
print(it.generate_analytics_report())
"

# Export patterns
python3 -c "
from src.copilot_iteration import CopilotStyleIteration
it = CopilotStyleIteration('aros-src', 'radeonsi', 'logs', 10)
it.load_iteration_state()
path = it.export_learned_patterns('patterns_export.json')
print(f'Exported to: {path}')
"
```

---

## Best Practices

### 1. Pattern Recommendations

- **Use Early**: Get recommendations before starting complex tasks
- **Update Complexity**: Adjust complexity level based on task understanding
- **Review Best Practices**: Always review the suggested best practices
- **Track Probability**: Monitor success probability trends over time

### 2. Checkpoint Diff

- **Regular Checkpoints**: Create checkpoints at logical milestones
- **Descriptive Names**: Use meaningful checkpoint names
- **Review Before Merge**: Compare checkpoints before merging changes
- **Document Diffs**: Use diffs for code review documentation

### 3. Pattern Export/Import

- **Version Control**: Keep pattern exports in version control
- **Merge Wisely**: Use merge mode for collaborative patterns
- **Namespace Patterns**: Use project-specific naming for phases
- **Periodic Exports**: Export patterns regularly as backup

### 4. Analytics

- **Regular Reviews**: Review analytics after every 5-10 iterations
- **Act on Recommendations**: Follow analytics recommendations
- **Share Reports**: Use reports for team discussions
- **Track Trends**: Monitor success rate and time trends

---

## Performance Impact

All new features are designed for minimal overhead:

| Feature | Performance Impact |
|---------|-------------------|
| Pattern Recommendations | <1ms per call |
| Checkpoint Diff | 10-50ms per comparison |
| Pattern Export | 20-50ms per export |
| Pattern Import | 50-200ms per import |
| Analytics Generation | 5-20ms per report |
| Full Report Generation | 50-100ms |

---

## Future Enhancements

Planned improvements for future versions:

1. **ML-Based Recommendations**: Use machine learning to improve predictions
2. **Visual Analytics**: Web-based dashboard for analytics
3. **Pattern Marketplace**: Share patterns with community
4. **Checkpoint Branching**: Create experimental branches from checkpoints
5. **Advanced Diff Views**: Side-by-side code comparison
6. **Real-time Notifications**: Alert on significant changes or issues
7. **Pattern Validation**: Verify pattern quality before import
8. **Multi-Project Analytics**: Compare patterns across projects

---

## Troubleshooting

### Pattern Recommendations Not Available

**Issue**: `get_pattern_recommendation()` returns default values

**Solution**: 
1. Ensure iterations have been completed
2. Check that patterns are being learned (verify `learned_patterns`)
3. Verify phase name matches exactly

### Checkpoint Diff Shows No Changes

**Issue**: Diff shows "No differences found"

**Solution**:
1. Verify checkpoints are from different sessions
2. Check that changes were made to iteration_context
3. Ensure checkpoints were saved after changes

### Pattern Import Fails

**Issue**: `import_learned_patterns()` returns False

**Solution**:
1. Verify export file exists and is readable
2. Check JSON format is valid
3. Ensure format version is compatible

### Analytics Report Empty

**Issue**: Report shows "No iteration history available"

**Solution**:
1. Complete at least one iteration
2. Verify iteration history is being tracked
3. Check that state was saved/loaded correctly

---

## See Also

- [COPILOT_ENHANCEMENTS.md](COPILOT_ENHANCEMENTS.md) - Previous enhancement features
- [ITERATION_ENHANCEMENTS.md](ITERATION_ENHANCEMENTS.md) - Core iteration enhancements
- [QUICKREF_ITERATION.md](QUICKREF_ITERATION.md) - Quick reference guide
- [examples/advanced_features_demo.py](../examples/advanced_features_demo.py) - Working examples
