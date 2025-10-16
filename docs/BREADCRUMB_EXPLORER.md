# Breadcrumb Explorer

The Breadcrumb Explorer is a dedicated UI page for managing, searching, and visualizing AI breadcrumbs in the AROS development system.

## Overview

As the codebase grows and accumulates hundreds or thousands of breadcrumbs, the main dashboard becomes cluttered. The Breadcrumb Explorer provides a scalable, feature-rich interface for working with breadcrumbs efficiently.

## Features

### 🔍 Search & Filtering

The sidebar provides comprehensive filtering options:

- **Free-text Search**: Search across AI notes, fix reasons, Linux references, and other text fields
- **Phase Filter**: Filter by development phase (e.g., graphics_pipeline_v2, kernel_memory_init)
- **Status Filter**: Filter by implementation status (IMPLEMENTED, PARTIAL, NOT_STARTED)
- **Marker Filter**: Filter by AI_BREADCRUMB marker for feature grouping
- **File Path Filter**: Search for breadcrumbs in specific files
- **Complexity Filter**: Filter by AI_COMPLEXITY range (1-10)

All filters can be combined for powerful, multi-criteria searches.

### 📊 Summary Cards

At the top of the page, four summary cards provide quick insights:

1. **Total Breadcrumbs**: Overall count of all breadcrumbs
2. **Implemented**: Count of completed items (green)
3. **Partial**: Count of in-progress items (yellow)
4. **Not Started**: Count of pending items (red)

Click any card to quickly filter by that status.

### 📋 Breadcrumb Table

The main table displays breadcrumbs with:

- **File**: Filename (hover for full path)
- **Line**: Line number in file
- **Phase**: Development phase with color-coded badge
- **Status**: Implementation status with color-coded badge
- **Marker**: AI_BREADCRUMB marker for grouping
- **Priority**: Task priority (CRITICAL, HIGH, MEDIUM, LOW)

**Pagination**: 50 items per page with next/previous navigation

**Interaction**: Click any row to open the detail drawer

### 🗂️ Detail Drawer

Clicking a breadcrumb opens a detailed view sliding in from the right:

#### Basic Information
- File path and line number
- Phase, status, and marker
- Strategy used

#### AI Metadata
- **AI Note**: What the AI learned or accomplished
- **Fix Reason**: Why a fix was needed
- **Details**: Implementation details
- **AI Context**: Structured JSON data (if present)

#### Task Metadata
- Priority level
- Complexity rating (1-10)
- Estimated time
- Assigned AI agent

#### Dependencies & Relationships
- **Dependencies**: What this breadcrumb depends on
- **Blocks**: What this breadcrumb blocks
- **Related Breadcrumbs**: Other breadcrumbs in the same file or with the same marker

#### Actions
- **View File**: Navigate to the source file (placeholder)
- **Open Graph**: View relationship graph (placeholder)

### 🕸️ Relationship Graph (Coming Soon)

The graph visualization feature will use **vis-network** or **cytoscape.js** to show:

- Nodes representing breadcrumbs (colored by status)
- Edges showing dependencies and blocking relationships
- Clusters by AI_BREADCRUMB marker
- Interactive zoom and drag navigation

Backend support is already implemented via `/api/breadcrumbs/graph`.

## API Endpoints

### GET /api/breadcrumbs/search

Search and filter breadcrumbs with pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Results per page (default: 50, max: 100)
- `q` (string): Free-text search query
- `phase` (string): Filter by phase
- `status` (string): Filter by status
- `marker` (string): Filter by AI_BREADCRUMB
- `file` (string): Filter by file path
- `min_complexity` (int): Minimum complexity (1-10)
- `max_complexity` (int): Maximum complexity (1-10)

**Response:**
```json
{
  "breadcrumbs": [...],
  "total": 463,
  "page": 1,
  "per_page": 50,
  "total_pages": 10
}
```

### GET /api/breadcrumbs/:id

Get detailed information about a specific breadcrumb by index.

**Response:**
```json
{
  "breadcrumb": { ... },
  "related": [...]
}
```

### GET /api/breadcrumbs/graph

Get graph data for visualization.

**Query Parameters:**
- `marker` (string): Filter graph by specific marker
- `file` (string): Filter graph by file path

**Response:**
```json
{
  "nodes": [
    {
      "id": 0,
      "label": "graphics_pipeline_v2:45",
      "color": "#4ade80",
      "status": "IMPLEMENTED",
      ...
    }
  ],
  "edges": [
    {
      "from": 0,
      "to": 1,
      "label": "depends on",
      "arrows": "to"
    }
  ]
}
```

### GET /api/breadcrumbs/filters

Get available filter options (phases, statuses, markers, files).

**Response:**
```json
{
  "phases": ["graphics_pipeline_v2", ...],
  "statuses": ["IMPLEMENTED", "PARTIAL", "NOT_STARTED"],
  "markers": ["graphics_pipeline_v2", ...],
  "files": ["rom/kernel/memory.c", ...]
}
```

## Usage

### Accessing the Explorer

1. From the main dashboard, click the **"🧭 Open Breadcrumb Explorer"** button in the AI Breadcrumbs card
2. Or navigate directly to `/breadcrumbs`

### Searching and Filtering

1. Enter search terms in the sidebar
2. Select filters from dropdowns
3. Set complexity range if needed
4. Click **"Apply Filters"**
5. Results update automatically

### Viewing Details

1. Click any row in the table
2. Detail drawer slides in from the right
3. Review all metadata and relationships
4. Click related breadcrumbs to navigate
5. Close drawer with the **×** button

### Clearing Filters

Click the **"Clear Filters"** button to reset all filters and show all breadcrumbs.

## Sample Data

A sample dataset is provided in `breadcrumbs.sample.json`:
- 10 sample breadcrumbs
- 6 different phases
- Mix of statuses (IMPLEMENTED, PARTIAL, NOT_STARTED)
- Various complexity levels and priorities

To use the sample data:
```bash
cp breadcrumbs.sample.json breadcrumbs.json
```

Then access the UI at http://localhost:5000/breadcrumbs

## Performance

The Breadcrumb Explorer is designed to handle large datasets efficiently:

- **Pagination**: Loads only 50 items at a time
- **Server-side filtering**: Filtering happens on the backend
- **Lazy loading**: Detail drawer loads data on-demand
- **Auto-refresh**: Updates every 30 seconds without full page reload

Tested with 463 breadcrumbs with excellent performance. Should scale to tens of thousands without issues.

## Future Enhancements

1. **Graph Visualization**: Complete integration with vis-network or cytoscape.js
2. **History & Diff**: Track changes to breadcrumbs over time
3. **Export**: Export filtered results to CSV/JSON
4. **Sorting**: Click column headers to sort
5. **Advanced Search**: Regular expressions and complex queries
6. **Bookmarkable URLs**: Save and share specific filter combinations
7. **Batch Operations**: Update multiple breadcrumbs at once

## Technical Details

### Frontend
- Pure HTML, CSS, and JavaScript (no framework required)
- Responsive design (works on mobile and tablet)
- Consistent with main dashboard styling
- Glassmorphism design language

### Backend
- Flask routes in `ui/app.py`
- Uses existing `breadcrumb_parser` infrastructure
- Reads from `breadcrumbs.json` (generated by scan)
- Efficient filtering and pagination

### Data Flow
1. User scans codebase → `breadcrumbs.json` created
2. Explorer reads `breadcrumbs.json`
3. API endpoints filter and paginate results
4. Frontend displays and allows interaction
5. Auto-refresh keeps data current

## Troubleshooting

### No breadcrumbs showing

**Issue**: Explorer shows "No breadcrumbs found"

**Solutions**:
1. Run a breadcrumb scan from the main dashboard
2. Check if `breadcrumbs.json` exists
3. Verify AROS repository is cloned

### Filters not working

**Issue**: Applying filters shows no results

**Solutions**:
1. Try clearing filters first
2. Check if filter values match actual data
3. Look at browser console for errors

### Performance issues

**Issue**: Page loads slowly with many breadcrumbs

**Solutions**:
1. Reduce `per_page` parameter
2. Use more specific filters
3. Check server resources

## Contributing

When adding new features to the Breadcrumb Explorer:

1. Add backend API route in `ui/app.py`
2. Update frontend JavaScript in `breadcrumbs.html`
3. Maintain styling consistency
4. Update this documentation
5. Test with large datasets

## References

- Main dashboard: `/` 
- API endpoints: `/api/breadcrumbs/*`
- Template: `ui/templates/breadcrumbs.html`
- Backend: `ui/app.py`
