# AI Breadcrumb Scanning and UI Guide

This guide explains how to use the breadcrumb scanning tools and the monitoring UI.

## Quick Start

### Starting the UI

The easiest way to start the monitoring UI:

```bash
./start_ui.sh
```

Then open your browser to: **http://localhost:5000**

### Scanning Breadcrumbs

To scan the AROS source directory for breadcrumbs:

```bash
# Scan aros-src directory
python3 scripts/scan_breadcrumbs.py aros-src

# Scan with maximum file limit
python3 scripts/scan_breadcrumbs.py aros-src --max-files 100

# Export to JSON
python3 scripts/scan_breadcrumbs.py aros-src --output breadcrumbs.json

# Scan specific directory
python3 scripts/scan_breadcrumbs.py /path/to/directory
```

## Features

### Breadcrumb Scanner (`scripts/scan_breadcrumbs.py`)

The scanner extracts AI breadcrumb metadata from C/C++ source files:

- **Automatic Detection**: Finds all `.c`, `.h`, `.cpp`, `.hpp` files
- **Validation**: Checks breadcrumb format and completeness
- **Statistics**: Provides breakdown by phase and status
- **Export**: Save results to JSON for further analysis

#### Output Example

```
Scanning directory: ./aros-src
Looking for extensions: .c, .h, .cpp, .hpp

Found 3 files to scan

[1/3] ✓ printer_driver.c: 3 breadcrumbs
[2/3] ✓ sample_driver.c: 5 breadcrumbs
[3/3] ✓ kernel_core.c: 3 breadcrumbs

Scanned 3 files
Files with breadcrumbs: 3
Total breadcrumbs found: 11

============================================================
BREADCRUMB STATISTICS
============================================================

Total Breadcrumbs: 11
Files with Breadcrumbs: 3

By Phase:
  PRINTER_STACK: 2
  GRAPHICS_PIPELINE: 2
  KERNEL_INIT: 2
  ...

By Status:
  IMPLEMENTED: 5
  PARTIAL: 3
  NOT_STARTED: 2
  FIXED: 1
```

### Monitoring UI

The web UI provides real-time monitoring of:

#### Dashboard Cards

1. **System Status**
   - AROS repository status
   - Training status
   - Iteration loop status

2. **AI Breadcrumbs**
   - Total breadcrumb count
   - Files tracked
   - Validation errors
   - Phase distribution with color-coded badges

3. **Compilation Loop**
   - Total iterations
   - Success/failure counts
   - Error statistics

4. **Error Intelligence**
   - Unique errors tracked
   - Resolved vs unresolved
   - Error patterns

5. **AI Reasoning**
   - Reasoning events
   - Success rate
   - Pattern usage

#### Live Sections

- **AI Currently Thinking About**: Real-time AI reasoning display
- **Recent Decisions & Reasoning**: Historical reasoning log
- **Pattern Usage Statistics**: Most used patterns and success rates
- **Recent Breadcrumbs**: Latest breadcrumbs with file locations
- **Compilation Logs**: Build output and errors

### API Endpoints

The UI exposes RESTful API endpoints:

```bash
# System status
curl http://localhost:5000/api/status

# Breadcrumb statistics
curl http://localhost:5000/api/breadcrumbs

# Compilation statistics
curl http://localhost:5000/api/compilation

# Error tracking
curl http://localhost:5000/api/errors

# AI reasoning (current)
curl http://localhost:5000/api/reasoning/current

# AI reasoning (history)
curl http://localhost:5000/api/reasoning/history?limit=10

# AI reasoning (statistics)
curl http://localhost:5000/api/reasoning/stats

# AI reasoning (patterns)
curl http://localhost:5000/api/reasoning/patterns
```

## Configuration

The system is configured via `config/config.json`:

```json
{
  "aros_local_path": "./aros-src",
  "logs_path": "./logs",
  "model_path": "./models",
  "ui": {
    "host": "0.0.0.0",
    "port": 5000,
    "refresh_interval": 5
  }
}
```

## Directory Structure

```
.
├── aros-src/           # AROS source code (gitignored)
├── logs/               # Log files (gitignored)
│   ├── errors/
│   ├── reasoning/
│   ├── training/
│   └── compilation/
├── models/             # AI models (gitignored)
├── scripts/
│   └── scan_breadcrumbs.py  # Breadcrumb scanner
├── ui/
│   ├── app.py          # Flask application
│   └── templates/
│       └── index.html  # UI template
└── start_ui.sh         # UI startup script
```

## Development

### Running Tests

Test the scanner on sample files:

```bash
# Create sample files in aros-src/
python3 scripts/scan_breadcrumbs.py aros-src
```

### Manual UI Testing

1. Start the server:
   ```bash
   python3 ui/app.py
   ```

2. Open browser to: http://localhost:5000

3. Test API endpoints:
   ```bash
   curl http://localhost:5000/api/status
   curl http://localhost:5000/api/breadcrumbs
   ```

## Troubleshooting

### UI won't start

Check dependencies:
```bash
pip install -r requirements.txt
```

### No breadcrumbs found

- Ensure aros-src directory exists and contains C files
- Check that files have proper breadcrumb format
- Verify file extensions (.c, .h, .cpp, .hpp)

### API returns empty data

- The aros-src directory needs valid C files with breadcrumbs
- Check that the server is running: `curl http://localhost:5000/api/status`
- Review server logs for errors

## Example Breadcrumb Format

```c
// AI_PHASE: GRAPHICS_PIPELINE
// AI_STATUS: IMPLEMENTED
// AI_STRATEGY: Implement basic graphics initialization using HIDD system
// AI_DETAILS: Initialize graphics hardware and prepare for rendering
// AI_VERSION: 1.0
// AI_PATTERN: HARDWARE_INIT_V1
static BOOL init_graphics_hardware(struct GraphicsContext *ctx)
{
    // Implementation
}
```

## Next Steps

1. Clone the full AROS repository:
   ```bash
   ./scripts/clone_aros.sh
   ```

2. Scan the entire codebase:
   ```bash
   python3 scripts/scan_breadcrumbs.py aros-src --output full_scan.json
   ```

3. Start the UI to monitor development:
   ```bash
   ./start_ui.sh
   ```

## Support

For more information, see:
- [AI_BREADCRUMB_GUIDE.md](AI_BREADCRUMB_GUIDE.md) - Complete breadcrumb system guide
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) - Architecture details
- [README.md](README.md) - Main project documentation
