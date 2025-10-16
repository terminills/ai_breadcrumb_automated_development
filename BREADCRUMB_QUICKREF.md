# AI Breadcrumb Quick Reference

## Core Tags (Required)

```c
// AI_PHASE: FEATURE_NAME              // Development phase identifier
// AI_STATUS: IMPLEMENTED               // Status: NOT_STARTED, PARTIAL, IMPLEMENTED, FIXED
// AI_NOTE: Brief context and next steps
// AI_BREADCRUMB: feature_marker_v1     // File-level feature marker for bidirectional mapping
```

## Reference Tags

```c
// LINUX_REF: path/to/linux/source.c   // Linux kernel/Mesa source reference
// AROS_IMPL: AROS-specific details     // AROS implementation notes
// AMIGAOS_REF: path/to/amigaos/source // AmigaOS source reference
```

## Error Tracking Tags

```c
// COMPILER_ERR: exact error message    // Compiler error for learning
// RUNTIME_ERR: observed behavior       // Runtime error observation
// FIX_REASON: explanation of fix       // Why this fix works
// AI_PATTERN: FIX_PATTERN_V1          // Pattern identifier for reuse
```

## Security Tags

```c
// HUMAN_OVERRIDE: manual intervention  // Document human changes
```

## Bidirectional Mapping Example

```c
// File: shader_init.c
// AI_PHASE: SHADER_INIT
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: graphics_pipeline
// AI_BLOCKS: SHADER_COMPILE
void init_shaders() { }

// File: shader_compile.c
// AI_PHASE: SHADER_COMPILE
// AI_STATUS: IMPLEMENTED
// AI_BREADCRUMB: graphics_pipeline    // Same marker = related
// AI_DEPENDENCIES: SHADER_INIT        // Explicit dependency
void compile_shader() { }
```

## Python API Quick Reference

```python
from src.breadcrumb_parser.parser import BreadcrumbParser

# Parse files
parser = BreadcrumbParser()
parser.parse_file('myfile.c')

# Get breadcrumbs by phase
breadcrumbs = parser.get_breadcrumbs_by_phase('SHADER_INIT')

# Get breadcrumbs by status
partial = parser.get_breadcrumbs_by_status('PARTIAL')

# Group by AI_BREADCRUMB marker
breadcrumb_map = parser.get_breadcrumb_map()
# Returns: {'marker1': [bc1, bc2], 'marker2': [bc3, bc4]}

# Find related breadcrumbs (bidirectional)
related = parser.find_related_breadcrumbs(breadcrumb)
# Returns all related through markers, dependencies, blocks, references

# Get statistics
stats = parser.get_statistics()
# Returns: {'total_breadcrumbs': N, 'phases': {...}, 'statuses': {...}}
```

## Relationship Types

### 1. Marker-Based (AI_BREADCRUMB)
Components with same marker are related

### 2. Dependency-Based (AI_DEPENDENCIES)
Component explicitly depends on others

### 3. Blocking-Based (AI_BLOCKS)
Component blocks others from executing

### 4. Reference-Based (LINUX_REF, AMIGAOS_REF)
Components referencing same external source are related

### 5. Correction-Based (PREVIOUS_IMPLEMENTATION_REF, CORRECTION_REF)
Links between original and corrected implementations

## Best Practices

1. **Always use required tags**: AI_PHASE, AI_STATUS
2. **Use AI_BREADCRUMB** to link related components across files
3. **Document relationships** with AI_DEPENDENCIES and AI_BLOCKS
4. **Keep markers consistent** across related components
5. **Think bidirectionally** - relationships work both ways

## Common Patterns

### Feature Development
```c
// AI_PHASE: FEATURE_IMPL
// AI_STATUS: PARTIAL
// AI_BREADCRUMB: feature_name
// AI_NOTE: Work in progress
```

### Bug Fix
```c
// AI_PHASE: BUG_FIX
// AI_STATUS: FIXED
// FIX_REASON: Root cause explanation
// COMPILER_ERR: original error
```

### Porting Code
```c
// AI_PHASE: PORT_FEATURE
// AI_STATUS: IMPLEMENTED
// LINUX_REF: path/to/linux/source
// AROS_IMPL: AROS-specific adaptations
```

## Testing

```bash
# Run breadcrumb tests
python3 tests/test_breadcrumb_enhancements.py

# Run interactive demo
python3 examples/breadcrumb_mapping_demo.py

# View a specific breadcrumb file
python3 -c "
from src.breadcrumb_parser.parser import BreadcrumbParser
parser = BreadcrumbParser()
bcs = parser.parse_file('myfile.c')
for bc in bcs:
    print(f'{bc.phase}: {bc.status}')
"
```

## Documentation

- **README.md** - Complete system overview with examples
- **BREADCRUMB_ENHANCEMENT_SUMMARY.md** - Implementation details
- **docs/BREADCRUMB_MAPPING_GUIDE.md** - Visual guide with diagrams
- **examples/breadcrumb_mapping_demo.py** - Interactive demonstration

## Quick Start

```bash
# 1. Add breadcrumbs to your code
# 2. Parse with BreadcrumbParser
# 3. Use get_breadcrumb_map() to group related components
# 4. Use find_related_breadcrumbs() to navigate relationships
```

---

For detailed information, see the full documentation in README.md
