# Interactive Development - Example Workflows

This document provides real-world examples of using the interactive development features to accomplish common tasks.

## Workflow 1: Understanding Existing Code

**Goal**: Understand how GPU memory allocation works in the existing codebase

**Steps**:

1. Start chat mode:
```bash
python3 scripts/interactive_chat.py
```

2. Explore the codebase:
```
> explore GPU memory allocation in radeonsi
```

**Output**: Lists relevant files, breadcrumbs, and patterns

3. Get explanation:
```
> explain MEMORY_ALLOC_V2 pattern
```

**Output**: Detailed explanation of the pattern

4. Review specific implementation:
```
> review
[paste code snippet]
###
```

**Output**: Analysis and suggestions

**Result**: You now understand the existing patterns and can build on them.

---

## Workflow 2: Implementing a New Feature

**Goal**: Add a new texture upload function

**Steps**:

1. Run interactive demo to see the full process:
```bash
python3 scripts/interactive_demo.py
```

Select "Texture Upload" when prompted.

2. Use chat mode to refine:
```bash
python3 scripts/interactive_chat.py
> explore texture upload implementations
> generate texture upload function with error handling
```

3. Review generated code:
```
> review
[paste generated code]
###
```

4. Iterate based on feedback:
```
> generate improved texture upload with memory alignment
```

**Result**: Complete implementation with breadcrumbs, ready to integrate.

---

## Workflow 3: Debugging Compilation Errors

**Goal**: Fix compilation errors in existing code

**Steps**:

1. Start full copilot iteration:
```bash
./scripts/run_copilot_iteration.sh radeonsi 5
```

2. Monitor in Web UI:
```bash
# In another terminal
./start_ui.sh
# Open http://localhost:5000
```

3. Check error tracking:
- Navigate to "Errors" tab
- See unresolved errors
- View patterns and suggestions

4. Use chat mode for specific fixes:
```bash
python3 scripts/interactive_chat.py
> explain [error message]
> generate fix for [specific issue]
```

**Result**: Errors tracked, patterns identified, fixes generated.

---

## Workflow 4: Learning from Examples

**Goal**: Learn how to implement a similar feature to existing code

**Steps**:

1. Explore existing examples:
```bash
python3 scripts/interactive_chat.py
> explore shader compilation examples
```

2. See the demo:
```bash
python3 scripts/interactive_demo.py
```
Choose "Shader Compilation"

3. Examine API examples:
```bash
less examples/copilot_api_example.py
```

4. Try it yourself:
```python
from src.interactive_session import SessionManager
from src.local_models import LocalModelLoader

loader = LocalModelLoader()
session = SessionManager(loader, 'aros-src', 'logs')

session_id = session.start_session(
    task_description="Implement custom shader loader",
    context={'phase': 'SHADER_PIPELINE'}
)

exploration = session.explore("shader compilation patterns")
generation = session.generate(use_exploration=True)

print(generation['code'])
```

**Result**: Understanding of patterns, ability to implement similar features.

---

## Workflow 5: Code Review Workflow

**Goal**: Review a pull request with AI assistance

**Steps**:

1. Get the changes:
```bash
git diff main..feature-branch > changes.txt
```

2. Use chat mode for analysis:
```bash
python3 scripts/interactive_chat.py
> review
[paste code from changes.txt]
###
```

3. Ask specific questions:
```
> explain why this memory allocation approach was used
> status
> history
```

4. Generate improvements:
```
> generate improved version with better error handling
```

**Result**: Comprehensive review with suggestions and improvements.

---

## Workflow 6: Documentation-Driven Development

**Goal**: Understand system before implementing

**Steps**:

1. Quick start:
```bash
./scripts/quickstart_interactive.sh
```
Choose option 4 (Documentation)

2. Read interactive guide:
```bash
less docs/INTERACTIVE_GUIDE.md
```

3. Try examples:
```bash
python3 examples/copilot_api_example.py
```

4. Run demo:
```bash
python3 scripts/interactive_demo.py
```

5. Start implementing:
```bash
python3 scripts/interactive_chat.py
> explore [your feature]
> generate [your feature]
```

**Result**: Well-informed implementation based on documentation and examples.

---

## Workflow 7: Rapid Prototyping

**Goal**: Quickly prototype a new feature

**Steps**:

1. Use chat mode for quick generation:
```bash
python3 scripts/interactive_chat.py
```

2. Generate multiple variations:
```
> generate command buffer management v1
> generate command buffer management v2 with async support
> generate command buffer management v3 with error recovery
```

3. Review each:
```
> review
[paste v1]
###

> review
[paste v2]
###
```

4. Choose the best and iterate:
```
> generate final version combining best features
```

**Result**: Multiple prototypes to choose from, refined final version.

---

## Workflow 8: Continuous Integration

**Goal**: Integrate AI assistance into CI/CD pipeline

**Steps**:

1. Create CI script:
```bash
#!/bin/bash
# .github/scripts/ai-assist.sh

# Find incomplete tasks
python3 scripts/scan_breadcrumbs.py aros-src --output breadcrumbs.json

# Generate implementations
./scripts/run_copilot_iteration.sh auto 10

# Check results
python3 -c "
from src.breadcrumb_parser import BreadcrumbParser
parser = BreadcrumbParser()
incomplete = parser.get_breadcrumbs_by_status('PARTIAL')
if len(incomplete) > 10:
    print(f'Warning: {len(incomplete)} incomplete tasks')
"
```

2. Add to workflow:
```yaml
# .github/workflows/ai-assist.yml
name: AI Development Assistance
on: [push, pull_request]
jobs:
  ai-assist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run AI assistance
        run: |
          pip install -r requirements.txt
          .github/scripts/ai-assist.sh
```

**Result**: Automated AI-assisted development in CI/CD.

---

## Workflow 9: Team Collaboration

**Goal**: Share AI insights with team

**Steps**:

1. Generate code:
```bash
python3 scripts/interactive_chat.py
> explore feature requirements
> generate implementation
```

2. Save session:
```bash
cp logs/sessions/session_*.json team/session-feature-x.json
```

3. Team member reviews:
```bash
cat team/session-feature-x.json
python3 scripts/interactive_chat.py
> review
[paste code from session]
###
```

4. Iterate together:
```
> explain reasoning for approach
> generate alternative implementation
```

**Result**: Shared context, collaborative improvement.

---

## Workflow 10: Performance Analysis

**Goal**: Analyze and improve performance

**Steps**:

1. Start with exploration:
```bash
python3 scripts/interactive_chat.py
> explore performance bottlenecks in memory allocation
```

2. Check existing patterns:
```
> explain MEMORY_ALLOC_V2 pattern
```

3. Generate optimized version:
```
> generate optimized memory allocation with caching
```

4. Run full iteration with monitoring:
```bash
# Terminal 1
./scripts/run_copilot_iteration.sh memory_mgmt 10

# Terminal 2
./start_ui.sh
# Monitor performance metrics in UI
```

**Result**: Optimized implementation with performance considerations.

---

## Tips for All Workflows

### 1. Always Start with Exploration
```
> explore [topic]
```
Understanding context leads to better generation.

### 2. Use History
```
> history
```
Review what you've done, learn from it.

### 3. Iterate
Don't expect perfection first try:
```
> generate v1
> review
> generate v2 with improvements
```

### 4. Combine Tools
- Use demo for learning
- Use chat for quick tasks
- Use copilot for full development
- Use UI for monitoring

### 5. Save Your Work
Sessions are saved in `logs/sessions/`. Review them later to learn patterns.

### 6. Build Context
Each interaction adds to the context. The more you use it, the better it gets.

### 7. Be Specific
❌ "help with code"
✓ "explore GPU memory patterns in radeonsi driver"

---

## Common Patterns

### Pattern: Explore → Generate → Review → Iterate

Most effective workflow:
```
1. explore [topic]
2. generate [feature] 
3. review [generated code]
4. generate improved version
5. status (check progress)
```

### Pattern: Demo → Learn → Apply

For new features:
```
1. python3 scripts/interactive_demo.py
2. Watch the workflow
3. Apply to your own code
```

### Pattern: Quick Generate → Refine

For rapid development:
```
1. generate quick prototype
2. review
3. generate refinement 1
4. generate refinement 2
5. select best version
```

---

## Next Steps

After trying these workflows:
- Create your own workflows
- Customize scripts for your needs
- Share successful patterns with team
- Contribute improvements back

**Questions?** See:
- `docs/INTERACTIVE_GUIDE.md` - Full guide
- `docs/COPILOT_STYLE_ITERATION.md` - Technical details
- `examples/` - Code examples
