# Distributed AI Development Guide

This guide explains how to use the distributed AI breadcrumb fields for coordinating multiple AI agents working on the AROS codebase.

## Overview

The distributed AI development extension allows multiple AI agents to work on different tasks concurrently while maintaining coordination through breadcrumb metadata.

## New Fields

### AI_ASSIGNED_TO
**Type:** String (agent identifier)  
**Purpose:** Identifies which agent is currently working on this task  
**Example:** `agent_7f3a9b`, `agent_vulkan_001`

When null/empty, the task is available for claiming by any agent.

### AI_CLAIMED_AT
**Type:** ISO 8601 timestamp  
**Purpose:** Records when the task was claimed by an agent  
**Example:** `2025-10-15T14:32:00Z`

Used for timeout detection and analytics.

### AI_ESTIMATED_TIME
**Type:** String (duration)  
**Purpose:** Agent's estimate of completion time  
**Format:** `<number>h` or `<number>m`  
**Example:** `2.5h`, `45m`, `1.5h`

Improves scheduling decisions over time with historical data.

### AI_PRIORITY
**Type:** Integer (1-10)  
**Purpose:** Task priority for scheduling  
**Range:** 1 (lowest) to 10 (highest)  
**Example:** `5`, `10`, `3`

Higher priority tasks should be addressed first.

### AI_DEPENDENCIES
**Type:** Comma-separated list  
**Purpose:** Phases that must complete before this task can start  
**Example:** `LLVM_INIT, MEMORY_MANAGER`

Ensures proper task ordering.

### AI_BLOCKS
**Type:** Comma-separated list  
**Purpose:** Phases that are blocked by this task  
**Example:** `RENDER_PIPELINE, TEXTURE_UPLOAD`

Helps identify critical path tasks.

### AI_COMPLEXITY
**Type:** Enum  
**Purpose:** Indicates task complexity  
**Valid Values:** `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`  
**Example:** `MEDIUM`

Helps agents self-select appropriate tasks based on capability.

### AI_BOUNTY
**Type:** String (optional)  
**Purpose:** Economic incentive for completion  
**Example:** `$50`, `100 tokens`

For future economic models of AI agent coordination.

### AI_TIMEOUT
**Type:** ISO 8601 timestamp  
**Purpose:** When the task assignment expires  
**Example:** `2025-10-15T17:02:00Z`

After timeout, task becomes available for other agents.

### AI_RETRY_COUNT
**Type:** Integer  
**Purpose:** Number of retry attempts  
**Example:** `0`, `1`, `2`

Tracks how many times the task has been retried.

### AI_MAX_RETRIES
**Type:** Integer  
**Purpose:** Maximum retry attempts before escalation  
**Example:** `3`

Prevents infinite retry loops.

## Usage Examples

### Example 1: Claiming a Task

```c
// AI_PHASE: SHADER_COMPILATION
// AI_STATUS: NOT_STARTED
// AI_PRIORITY: 8
// AI_COMPLEXITY: HIGH
// AI_DEPENDENCIES: LLVM_INIT
```

Agent claims the task:

```c
// AI_PHASE: SHADER_COMPILATION
// AI_STATUS: PARTIAL
// AI_ASSIGNED_TO: agent_shader_001
// AI_CLAIMED_AT: 2025-10-15T14:32:00Z
// AI_ESTIMATED_TIME: 3h
// AI_PRIORITY: 8
// AI_COMPLEXITY: HIGH
// AI_DEPENDENCIES: LLVM_INIT
// AI_TIMEOUT: 2025-10-15T17:32:00Z
// AI_RETRY_COUNT: 0
// AI_MAX_RETRIES: 3
```

### Example 2: Task with Dependencies

```c
// AI_PHASE: TEXTURE_UPLOAD
// AI_STATUS: NOT_STARTED
// AI_PRIORITY: 6
// AI_COMPLEXITY: MEDIUM
// AI_DEPENDENCIES: MEMORY_MANAGER, SHADER_COMPILATION
// AI_BLOCKS: RENDER_COMPLETE, POST_PROCESSING
```

This task:
- Cannot start until MEMORY_MANAGER and SHADER_COMPILATION are complete
- Blocks RENDER_COMPLETE and POST_PROCESSING from starting

### Example 3: Task Retry After Failure

```c
// AI_PHASE: MEMORY_INIT
// AI_STATUS: PARTIAL
// AI_ASSIGNED_TO: agent_mem_002
// AI_CLAIMED_AT: 2025-10-15T16:00:00Z
// AI_ESTIMATED_TIME: 1.5h
// AI_PRIORITY: 10
// AI_COMPLEXITY: CRITICAL
// AI_TIMEOUT: 2025-10-15T17:30:00Z
// AI_RETRY_COUNT: 2
// AI_MAX_RETRIES: 3
// AI_NOTE: Previous attempts failed due to alignment issues
```

This shows a task on its second retry (will escalate after one more failure).

## Orchestration Strategies

### FIFO Round Robin (Recommended)

1. Maintain a queue of available tasks (STATUS: NOT_STARTED)
2. Agents poll for tasks in round-robin fashion
3. Agent claims task by updating breadcrumb fields
4. Agent works on task
5. On completion or timeout, task returns to queue or completes

Benefits:
- Fair distribution of work
- No agent starvation
- Simple and predictable
- Natural backpressure

### Priority-Based Scheduling

1. Sort available tasks by AI_PRIORITY (highest first)
2. Consider AI_COMPLEXITY for agent capability matching
3. Check AI_DEPENDENCIES are satisfied
4. Assign to available agent

Benefits:
- Critical tasks addressed first
- Better resource utilization
- Complexity-aware assignment

### Dependency-Aware Scheduling

1. Build dependency graph from AI_DEPENDENCIES and AI_BLOCKS
2. Identify tasks with satisfied dependencies
3. Schedule tasks on critical path first
4. Monitor AI_BLOCKS to identify bottlenecks

Benefits:
- Optimal task ordering
- Identifies critical path
- Reduces idle time

## Validation

The validator automatically checks:
- AI_COMPLEXITY is one of: LOW, MEDIUM, HIGH, CRITICAL
- AI_PRIORITY is between 1-10
- All other distributed fields accept any string value

## Parser Support

The breadcrumb parser automatically extracts all distributed AI fields:

```python
from src.breadcrumb_parser import BreadcrumbParser

parser = BreadcrumbParser()
breadcrumbs = parser.parse_file('your_file.c')

for bc in breadcrumbs:
    if bc.ai_assigned_to:
        print(f"Task {bc.phase} assigned to {bc.ai_assigned_to}")
        print(f"Priority: {bc.ai_priority}")
        print(f"Complexity: {bc.ai_complexity}")
```

## Future Enhancements

Potential future additions:
- Real-time agent coordination service
- Automatic timeout detection and reassignment
- Agent capability profiles
- Economic bounty system
- Performance metrics and analytics
- Conflict resolution mechanisms
- Distributed lock management

## Best Practices

1. **Always set AI_TIMEOUT** when claiming a task
2. **Update AI_RETRY_COUNT** on each attempt
3. **Use realistic AI_ESTIMATED_TIME** for scheduling
4. **Set appropriate AI_PRIORITY** based on criticality
5. **Document dependencies** clearly in AI_DEPENDENCIES
6. **Update AI_STATUS** promptly to NOT_STARTED if abandoning task
7. **Set AI_MAX_RETRIES** to prevent infinite loops

## See Also

- [README.md](../README.md) - Main documentation
- [AI Breadcrumb Guide](https://github.com/terminills/AROS-OLD/blob/master/AI_BREADCRUMB_GUIDE.md)
- Issue comments for detailed distributed AI specification
