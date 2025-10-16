# Cache Clear Guide

## Issue
When updating the web UI templates, your browser might still show the old version due to caching.

## Solution

### The Fix
The Flask app has been updated with proper cache-control headers to prevent browser caching of templates and API responses. This ensures you always see the latest version of the UI.

### If You Still See Old Content
If you're still seeing an old version after the update, try these steps:

#### Option 1: Hard Refresh (Recommended)
- **Windows/Linux**: Press `Ctrl + Shift + R` or `Ctrl + F5`
- **macOS**: Press `Cmd + Shift + R` or `Cmd + Option + R`

#### Option 2: Clear Browser Cache
1. Open your browser's Developer Tools (usually `F12`)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload" or "Clear Cache"

#### Option 3: Restart the Flask Server
1. Stop the current server (Ctrl+C)
2. Run `./start_ui.sh` again

## Verification
After clearing your cache, you should see:

1. **Main Dashboard (/)**: 
   - Iteration Progress card with copilot-style phase tracking
   - Code Generation live stream
   - Exploration, Review, and Compilation phase cards
   - Link to "🧭 Open Breadcrumb Explorer"

2. **Breadcrumb Explorer (/breadcrumbs)**:
   - Sidebar with filters
   - Search functionality
   - Paginated breadcrumb list
   - Graph visualization

## Technical Details
The following Flask configurations have been added to `ui/app.py`:

```python
# Disable template caching
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Add cache control headers
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
```

These settings ensure:
- Templates are reloaded on every request
- Browser doesn't cache any responses
- You always see the latest version
