"""
Web UI for AI Breadcrumb Development Monitoring
Provides real-time monitoring of training, compilation, and error tracking
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.breadcrumb_parser import BreadcrumbParser, BreadcrumbValidator
from src.compiler_loop import CompilerLoop, ErrorTracker, ReasoningTracker

app = Flask(__name__)

# Load configuration
config_path = Path(__file__).parent.parent / 'config' / 'config.json'
with open(config_path) as f:
    config = json.load(f)

# Initialize components
aros_path = Path(__file__).parent.parent / config['aros_local_path']
logs_path = Path(__file__).parent.parent / config['logs_path']

parser = BreadcrumbParser()
validator = BreadcrumbValidator()
compiler_loop = None
error_tracker = ErrorTracker(str(logs_path / 'errors'))
reasoning_tracker = ReasoningTracker(str(logs_path / 'reasoning'))


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', config=config)


@app.route('/api/status')
def api_status():
    """Get overall system status"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'aros_cloned': aros_path.exists(),
        'config': config
    }
    return jsonify(status)


@app.route('/api/breadcrumbs')
def api_breadcrumbs():
    """Get breadcrumb statistics"""
    if not aros_path.exists():
        return jsonify({'error': 'AROS repository not cloned yet'})
    
    # Parse C files in AROS repo (limit for performance)
    c_files = list(aros_path.rglob('*.c'))[:100]  # Sample first 100 files
    
    parser.breadcrumbs = []  # Reset
    for c_file in c_files:
        try:
            parser.parse_file(str(c_file))
        except Exception as e:
            pass
    
    stats = parser.get_statistics()
    
    # Validate breadcrumbs
    validator.validate_breadcrumbs(parser.breadcrumbs)
    validation_report = validator.get_report()
    
    return jsonify({
        'statistics': stats,
        'validation': validation_report,
        'recent_breadcrumbs': [
            {
                'file': b.file_path,
                'line': b.line_number,
                'phase': b.phase,
                'status': b.status,
                'strategy': b.strategy
            }
            for b in parser.breadcrumbs[:20]
        ]
    })


@app.route('/api/compilation')
def api_compilation():
    """Get compilation statistics"""
    if compiler_loop:
        return jsonify(compiler_loop.get_error_summary())
    return jsonify({'message': 'No compilation runs yet'})


@app.route('/api/compilation/history')
def api_compilation_history():
    """Get compilation history"""
    if compiler_loop:
        return jsonify({
            'history': compiler_loop.compile_history[-10:]  # Last 10 compilations
        })
    return jsonify({'history': []})


@app.route('/api/errors')
def api_errors():
    """Get error tracking statistics"""
    return jsonify(error_tracker.get_statistics())


@app.route('/api/errors/unresolved')
def api_unresolved_errors():
    """Get unresolved errors"""
    return jsonify({
        'errors': error_tracker.get_unresolved_errors()
    })


@app.route('/api/training/status')
def api_training_status():
    """Get training status"""
    training_log = logs_path / 'training' / 'latest.json'
    
    if training_log.exists():
        with open(training_log) as f:
            return jsonify(json.load(f))
    
    return jsonify({
        'status': 'not_started',
        'message': 'No training runs found'
    })


@app.route('/api/logs/<log_type>')
def api_logs(log_type):
    """Get recent log entries"""
    log_dir = logs_path / log_type
    
    if not log_dir.exists():
        return jsonify({'logs': []})
    
    # Get most recent log files
    log_files = sorted(log_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    
    logs = []
    for log_file in log_files:
        try:
            with open(log_file) as f:
                logs.append(json.load(f))
        except Exception as e:
            pass
    
    return jsonify({'logs': logs})


@app.route('/api/clone_aros', methods=['POST'])
def api_clone_aros():
    """Clone AROS repository"""
    if aros_path.exists():
        return jsonify({'status': 'already_exists', 'message': 'AROS repository already cloned'})
    
    # This would be handled by the scripts
    return jsonify({'status': 'queued', 'message': 'Clone operation queued'})


@app.route('/api/reasoning/current')
def api_reasoning_current():
    """Get current AI reasoning in progress"""
    current = reasoning_tracker.get_current_reasoning()
    
    if current:
        return jsonify(current)
    
    return jsonify({
        'message': 'No active reasoning at this time',
        'status': 'idle'
    })


@app.route('/api/reasoning/history')
def api_reasoning_history():
    """Get recent reasoning history"""
    limit = request.args.get('limit', default=10, type=int)
    history = reasoning_tracker.get_recent_reasoning(limit=limit)
    
    return jsonify({
        'history': history,
        'count': len(history)
    })


@app.route('/api/reasoning/stats')
def api_reasoning_stats():
    """Get reasoning statistics and patterns"""
    return jsonify(reasoning_tracker.get_statistics())


@app.route('/api/reasoning/patterns')
def api_reasoning_patterns():
    """Get pattern usage statistics"""
    return jsonify({
        'patterns': reasoning_tracker.get_pattern_statistics()
    })


@app.route('/api/reasoning/breadcrumbs')
def api_reasoning_breadcrumbs():
    """Get breadcrumb effectiveness statistics"""
    return jsonify({
        'breadcrumb_effectiveness': reasoning_tracker.get_breadcrumb_effectiveness()
    })


@app.route('/api/reasoning/failed')
def api_reasoning_failed():
    """Get failed reasoning patterns for analysis"""
    failed = reasoning_tracker.get_failed_reasoning_patterns()
    
    return jsonify({
        'failed_reasoning': failed,
        'count': len(failed)
    })


@app.route('/api/reasoning/by_phase/<phase>')
def api_reasoning_by_phase(phase):
    """Query reasoning by phase"""
    results = reasoning_tracker.query_by_phase(phase)
    
    return jsonify({
        'phase': phase,
        'results': results,
        'count': len(results)
    })


@app.route('/api/reasoning/by_pattern/<pattern>')
def api_reasoning_by_pattern(pattern):
    """Query reasoning by pattern"""
    results = reasoning_tracker.query_by_pattern(pattern)
    
    return jsonify({
        'pattern': pattern,
        'results': results,
        'count': len(results)
    })


if __name__ == '__main__':
    host = config['ui']['host']
    port = config['ui']['port']
    print(f"Starting AI Breadcrumb Development Monitor on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
