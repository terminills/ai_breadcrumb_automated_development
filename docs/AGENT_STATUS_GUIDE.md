# AI Agent Status Guide

## Overview

The AI Agent Status feature provides real-time visibility into the AI agents working on your codebase. This feature transforms the UI from a static page into a dynamic dashboard showing active AI operations.

## Features

### Agent Status Card

The Agent Status card appears on the main dashboard and displays:

- **Active Agents Count**: Number of AI agents currently working
- **Idle Agents Count**: Number of agents waiting for tasks
- **Individual Agent Details**: For each agent:
  - Name and type
  - Status badge (Active/Idle) with color coding
  - Current task description
  - Current phase of operation
  - Progress information (if applicable)
  - Detailed metrics and phase status

### Visual Features

- **Pulsing Glow Animation**: Active agents have a glowing animation to draw attention
- **Progress Bars**: Show completion percentage for trackable tasks
- **Color Coding**:
  - Green: Active agents with pulsing effect
  - Gray: Idle agents waiting for work
- **Real-time Updates**: Auto-refreshes every 5 seconds

## Agent Types

### 1. Copilot Iteration Agent

The main code generation and iteration agent.

**Shows when active:**
- Current iteration number and total
- Task being implemented (e.g., "Implementing graphics pipeline")
- Current phase (exploration, reasoning, generation, review, compilation, learning)
- Progress percentage
- Phase completion status for all 6 phases

**Example:**
```
Copilot Iteration Agent          [ACTIVE]
Task: Implementing memory manager
Phase: learning
Progress: 5/10 (50%)
Details:
  - Exploration: completed
  - Reasoning: completed
  - Generation: completed
  - Review: completed
  - Compilation: completed
  - Learning: running
```

### 2. Interactive Session Agent

Handles interactive development sessions.

**Shows when active:**
- Session task description
- Number of conversation turns
- Code files generated
- Session ID

**Example:**
```
Interactive Session Agent        [ACTIVE]
Task: Add memory allocation system
Phase: interactive
2 steps
Details:
  - Turns: 2
  - Code Generated: 2
```

### 3. Reasoning Agent

AI reasoning and decision-making agent.

**Shows when active:**
- Current reasoning task
- Reasoning phase (analyzing, planning, implementing, testing)
- Number of breadcrumbs consulted
- Patterns identified
- Reasoning steps completed

### 4. Idle Agents

When no active agents are running, the UI shows idle agents:
- Code Exploration Agent
- Code Generation Agent
- Compilation & Testing Agent

## API Endpoint

### GET `/api/agents/status`

Returns the current status of all AI agents.

**Response Format:**
```json
{
  "agents": [
    {
      "id": "copilot_iteration",
      "name": "Copilot Iteration Agent",
      "status": "active",
      "current_task": "Implementing memory manager",
      "phase": "learning",
      "progress": {
        "current": 5,
        "total": 10,
        "percentage": 50.0
      },
      "last_update": "2025-10-16T17:27:38.699152",
      "details": {
        "exploration": "completed",
        "reasoning": "completed",
        "generation": "completed",
        "review": "completed",
        "compilation": "completed",
        "learning": "running"
      }
    }
  ],
  "total_active": 2,
  "total_idle": 0,
  "timestamp": "2025-10-16T17:28:47.872996"
}
```

## Integration

### How Agent Status is Determined

The system checks multiple sources to determine agent status:

1. **Iteration State File** (`logs/iteration_state.json`)
   - Updated by `CopilotStyleIteration` during active iterations
   - Must be updated within last 5 minutes to be considered active

2. **Reasoning Tracker** (`logs/reasoning/current_reasoning.json`)
   - Tracks active AI reasoning operations
   - Shows real-time thinking and decision-making

3. **Session Files** (`logs/sessions/session_*.json`)
   - Tracks interactive development sessions
   - Shows conversation turns and generated code

### State Files

Agent status relies on these state files:

```
logs/
├── iteration_state.json      # Current iteration status
├── reasoning/
│   └── current_reasoning.json  # Active reasoning
└── sessions/
    └── session_*.json         # Interactive sessions
```

## Demo Mode

### Using the Demo Script

For testing and demonstration purposes, use the `demo_agents.py` script:

```bash
# Create a single snapshot of demo data
python3 scripts/demo_agents.py --once

# Run a continuous demo cycle (10 iterations)
python3 scripts/demo_agents.py

# Custom cycle (20 iterations, 3 seconds between updates)
python3 scripts/demo_agents.py -i 20 -d 3.0
```

**Demo Script Options:**
- `-i, --iterations`: Number of iterations to simulate (default: 10)
- `-d, --delay`: Delay between iterations in seconds (default: 2.0)
- `--once`: Create demo data once and exit

### What the Demo Creates

The demo script simulates realistic agent activity by creating:

1. **Iteration State**: Random tasks like "Implementing graphics pipeline", "shader compiler", etc.
2. **Reasoning Data**: Simulated AI decision-making with breadcrumbs and patterns
3. **Session Data**: Interactive development sessions with turns and generated code

## Development

### Adding New Agent Types

To add a new agent type to the status display:

1. **Update API Endpoint** (`ui/app.py`):
```python
# In api_agents_status() function
agents.append({
    'id': 'your_agent_id',
    'name': 'Your Agent Name',
    'status': 'active',  # or 'idle'
    'current_task': 'Task description',
    'phase': 'current_phase',
    'progress': {
        'current': current_value,
        'total': total_value,
        'percentage': percentage
    },
    'last_update': datetime.now().isoformat(),
    'details': {
        'key1': 'value1',
        'key2': 'value2'
    }
})
```

2. **Create State File**: Your agent should write its state to a JSON file in the logs directory

3. **Test**: Use the demo script or create actual agent operations

### Styling

Agent status styling is defined in `ui/templates/index.html`:

- `.agent-item`: Base agent container
- `.agent-item.active`: Active agent with pulse animation
- `.agent-item.idle`: Idle agent (dimmed)
- `.agent-status-badge`: Status badge styling
- `.agent-progress-bar`: Progress bar container

## Troubleshooting

### No Agents Showing

**Problem**: UI shows "No agents available"

**Solutions**:
1. Check if state files exist:
   ```bash
   ls -la logs/iteration_state.json
   ls -la logs/reasoning/
   ls -la logs/sessions/
   ```

2. Run the demo script to create test data:
   ```bash
   python3 scripts/demo_agents.py --once
   ```

3. Check Flask server logs for errors

### Agents Stuck as "Idle"

**Problem**: Agents show as idle when they should be active

**Solutions**:
1. Check the `last_update` timestamp in state files
2. Agents are considered active only if updated within last 5 minutes
3. Ensure your agent code is updating state files regularly

### API Returns Error

**Problem**: `/api/agents/status` returns an error

**Solutions**:
1. Check Flask logs: The error will be logged
2. Verify logs directory exists and is writable
3. Check JSON syntax in state files

## Best Practices

1. **Update Frequency**: Update agent state every 1-5 seconds during active operations
2. **Clean Shutdown**: Mark agents as idle when operations complete
3. **Error Handling**: Handle file read/write errors gracefully
4. **Progress Tracking**: Provide meaningful progress information when possible
5. **Phase Names**: Use clear, descriptive phase names

## Future Enhancements

Potential improvements to the agent status system:

- [ ] WebSocket support for instant updates (no polling)
- [ ] Agent performance metrics (operations/second, success rate)
- [ ] Agent history and timeline view
- [ ] Agent logs accessible from status card
- [ ] Agent control buttons (pause, stop, restart)
- [ ] Multi-agent coordination visualization
- [ ] Resource usage per agent (CPU, memory)
- [ ] Agent dependency graph

## Related Documentation

- [System Overview](../SYSTEM_OVERVIEW.md)
- [Copilot Iteration Guide](COPILOT_STYLE_ITERATION.md)
- [Interactive Development Guide](INTERACTIVE_GUIDE.md)
- [UI Development Guide](UI_DEVELOPMENT.md)
