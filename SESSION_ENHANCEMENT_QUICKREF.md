# Session Enhancement Quick Reference

## What's New

Sessions now have **detailed breadcrumb tracking and recall** to follow the breadcrumb spec and avoid repeated work.

## Key Features

### 1. Breadcrumb Usage Tracking
Every breadcrumb consulted is tracked with:
- File location and line number
- Usage count (how many times referenced)
- Phase, status, pattern, and strategy info

### 2. Pattern Recognition
Automatically extracts patterns from breadcrumbs with:
- Pattern name (e.g., `DEVICE_INIT_V1`)
- Usage count (how often used)
- Success rate (percentage of successful uses)

### 3. Duplicate Work Detection
Warns about similar completed tasks:
- Identifies tasks with similar keywords
- Shows completed implementations
- Suggests reusing existing approaches

### 4. Influence Tracking
Tracks which breadcrumbs influenced which decisions:
- Exploration decisions
- Reasoning/strategy formulation
- Code generation
- Reviews and iterations

## Quick Start

### View Session Details in UI

1. Navigate to http://localhost:5000/sessions
2. Click "Show Details" on any session
3. Scroll to "📚 Breadcrumb Recall & Pattern Reuse" section

You'll see:
- Breadcrumbs consulted: 12
- Patterns recalled: DEVICE_INIT_V1, MEMORY_POOL_V2
- ✓ Avoided duplicate work: 2 items (in green)
- Most used breadcrumbs with usage counts

### Get Statistics via API

```bash
curl http://localhost:5000/api/sessions/session_1729177425/breadcrumb_recall
```

Returns:
```json
{
    "breadcrumbs_consulted": 12,
    "patterns_recalled": ["DEVICE_INIT_V1", "MEMORY_POOL_V2"],
    "work_avoided": 2,
    "influence_count": 8,
    "most_used_breadcrumbs": [
        ["file.c:145", 5],
        ["file.c:89", 3]
    ]
}
```

### Python API

```python
from src.interactive_session import SessionManager

# Create session
session_mgr = SessionManager(model_loader, aros_path, log_path)
session_id = session_mgr.start_session("Task description", context)

# Explore with breadcrumb tracking
exploration = session_mgr.explore("query")
# Automatically tracks: breadcrumbs, patterns, duplicate work

# Get recall stats
stats = session_mgr.get_breadcrumb_recall_stats()
print(f"Patterns recalled: {stats['unique_patterns_recalled']}")
print(f"Work avoided: {stats['work_items_avoided']}")
```

## Enhanced Logging

### Session Start
```
✨ Started session session_123: Task description
📚 Breadcrumb recall system active
🔍 Found 2 similar past work items:
   [1] Similar task description
       Used patterns: PATTERN_V1, PATTERN_V2
```

### Exploration Phase
```
🔍 Starting exploration...
  Found 12 relevant breadcrumbs
     [1] Phase: GPU_INIT, Status: PARTIAL
         Pattern: DEVICE_INIT_V1
         Strategy: Initialize GPU device...
  🎯 Identified 3 reusable patterns:
     • DEVICE_INIT_V1: Used 4 times, Success rate: 75.0%
  ⚠️  Duplicate work detection: Found 2 similar completed tasks
```

### Session End
```
📊 Breadcrumb Recall Statistics:
   Breadcrumbs consulted: 12
   Patterns recalled: 3
   Work items avoided: 2
   Most used breadcrumbs:
      • file.c:145: 5 times
      • file.c:89: 3 times
```

## Benefits

1. **Better Transparency**: See exactly which breadcrumbs influenced decisions
2. **Avoid Duplicate Work**: Automatic detection of similar completed tasks
3. **Pattern Reuse**: Learn from past successes with success rates
4. **Breadcrumb Compliance**: Sessions follow the breadcrumb spec for recall
5. **Debugging**: Track breadcrumb influences for better debugging

## Common Use Cases

### Check What Patterns Are Available
Look at exploration phase output for "🎯 Identified N reusable patterns"

### Avoid Repeating Work
Watch for "⚠️ Duplicate work detection: Found N similar completed tasks"

### See Which Breadcrumbs Were Most Useful
Check session details or end statistics for "Most used breadcrumbs"

### Track Decision Influences
Review breadcrumb influences in session details panel

## Files to Check

- **ENHANCED_SESSION_TRACKING.md** - Full technical documentation
- **ENHANCED_SESSION_EXAMPLE.md** - Complete example output
- **test_enhanced_session_tracking.py** - Test suite and examples

## Questions?

See the comprehensive documentation:
- Technical details: `ENHANCED_SESSION_TRACKING.md`
- Examples: `ENHANCED_SESSION_EXAMPLE.md`
- Summary: `SESSION_ENHANCEMENT_SUMMARY.md`
