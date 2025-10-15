"""
Web UI for AI Breadcrumb Development Monitoring
Provides real-time monitoring of training, compilation, and error tracking
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import sys
import subprocess
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

# Run database migration on startup
print("Running database schema migration...")
migration_script = Path(__file__).parent.parent / 'scripts' / 'migrate_database.sh'
if migration_script.exists():
    try:
        result = subprocess.run([str(migration_script)], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Database schema up to date")
        else:
            print(f"⚠ Warning: Database migration had issues: {result.stderr}")
    except Exception as e:
        print(f"⚠ Warning: Could not run database migration: {e}")
else:
    print("⚠ Warning: Database migration script not found")

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
    # First try to read from breadcrumbs.json if it exists
    breadcrumbs_file = Path(__file__).parent.parent / 'breadcrumbs.json'
    
    if breadcrumbs_file.exists():
        try:
            with open(breadcrumbs_file) as f:
                data = json.load(f)
                
            # Get recent breadcrumbs (first 20)
            recent_breadcrumbs = []
            if 'breadcrumbs' in data:
                for b in data['breadcrumbs'][:20]:
                    recent_breadcrumbs.append({
                        'file': b.get('file_path', ''),
                        'line': b.get('line_number', 0),
                        'phase': b.get('phase', ''),
                        'status': b.get('status', ''),
                        'strategy': b.get('strategy', '')
                    })
            
            return jsonify({
                'statistics': data.get('statistics', {}),
                'validation': {'error_count': 0, 'warning_count': 0},  # From file, assume validated
                'recent_breadcrumbs': recent_breadcrumbs
            })
        except Exception as e:
            print(f"Error reading breadcrumbs.json: {e}")
    
    # Fallback to scanning (legacy behavior, limited for performance)
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


@app.route('/api/scan/breadcrumbs', methods=['POST'])
def api_scan_breadcrumbs():
    """Trigger breadcrumb scanning"""
    if not aros_path.exists():
        return jsonify({
            'status': 'error',
            'message': 'AROS repository not found. Please clone it first.'
        }), 400
    
    try:
        # Get options from request
        data = request.get_json() or {}
        max_files = data.get('max_files', None)
        full_scan = data.get('full_scan', False)
        
        # Run scan script
        scan_script = Path(__file__).parent.parent / 'scripts' / 'scan_breadcrumbs.py'
        breadcrumbs_output = Path(__file__).parent.parent / 'breadcrumbs.json'
        
        cmd = ['python3', str(scan_script), str(aros_path), '--output', str(breadcrumbs_output)]
        if max_files and not full_scan:
            cmd.extend(['--max-files', str(max_files)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': 'Breadcrumb scan completed successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Scan failed',
                'error': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Scan timed out after 5 minutes'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Scan failed: {str(e)}'
        }), 500


@app.route('/api/scan/status')
def api_scan_status():
    """Get scan status and last scan info"""
    scan_log = logs_path / 'scan_latest.json'
    
    if scan_log.exists():
        try:
            with open(scan_log) as f:
                return jsonify(json.load(f))
        except Exception:
            pass
    
    return jsonify({
        'status': 'never_run',
        'message': 'No scans have been run yet'
    })


@app.route('/api/training/start', methods=['POST'])
def api_training_start():
    """Trigger model training"""
    try:
        data = request.get_json() or {}
        
        # Get training parameters
        data_path = data.get('data_path', str(aros_path))
        output_path = data.get('output_path', str(Path(__file__).parent.parent / 'models' / 'aros-v1.3'))
        rocm_arch = data.get('rocm_arch', 'gfx900,gfx906')
        
        # Run training script
        train_script = Path(__file__).parent.parent / 'scripts' / 'train_model.sh'
        
        if not train_script.exists():
            return jsonify({
                'status': 'error',
                'message': 'Training script not found'
            }), 500
        
        # Run training asynchronously
        cmd = [str(train_script), data_path, output_path, rocm_arch]
        
        # Start training in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({
            'status': 'started',
            'message': 'Training started successfully',
            'pid': process.pid,
            'data_path': data_path,
            'output_path': output_path
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start training: {str(e)}'
        }), 500


@app.route('/api/iteration/start', methods=['POST'])
def api_iteration_start():
    """Trigger iteration loop"""
    try:
        data = request.get_json() or {}
        
        # Get iteration parameters
        mode = data.get('mode', 'ITERATE')
        project = data.get('project', 'radeonsi')
        max_iterations = data.get('max_iterations', 10)
        
        # Run AI agent script
        agent_script = Path(__file__).parent.parent / 'scripts' / 'run_ai_agent.sh'
        
        if not agent_script.exists():
            return jsonify({
                'status': 'error',
                'message': 'AI agent script not found'
            }), 500
        
        # Run iteration loop asynchronously
        cmd = [str(agent_script), mode, project, str(max_iterations)]
        
        # Start iteration in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({
            'status': 'started',
            'message': 'Iteration loop started successfully',
            'pid': process.pid,
            'mode': mode,
            'project': project,
            'max_iterations': max_iterations
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start iteration loop: {str(e)}'
        }), 500


@app.route('/api/iteration/status')
def api_iteration_status():
    """Get iteration loop status"""
    agent_log_dir = logs_path / 'agent'
    
    if not agent_log_dir.exists():
        return jsonify({
            'status': 'never_run',
            'message': 'No iteration loops have been run yet'
        })
    
    # Get most recent log file
    log_files = sorted(agent_log_dir.glob('agent_*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not log_files:
        return jsonify({
            'status': 'never_run',
            'message': 'No iteration logs found'
        })
    
    # Read the most recent log
    try:
        with open(log_files[0]) as f:
            log_content = f.read()
        
        return jsonify({
            'status': 'completed',
            'log_file': log_files[0].name,
            'log_preview': log_content[:500]  # First 500 chars
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to read log: {str(e)}'
        }), 500


@app.route('/api/projects/list')
def api_projects_list():
    """List available projects for iteration"""
    # Common AROS projects that can be targeted for development
    projects = [
        {
            'id': 'radeonsi',
            'name': 'RadeonSI Graphics Driver',
            'description': 'AMD Radeon GPU driver implementation',
            'path': 'workbench/devs/radeonsi'
        },
        {
            'id': 'graphics',
            'name': 'Graphics Pipeline',
            'description': 'Core graphics rendering pipeline',
            'path': 'workbench/libs/graphics'
        },
        {
            'id': 'kernel',
            'name': 'Kernel Components',
            'description': 'Operating system kernel',
            'path': 'rom/kernel'
        },
        {
            'id': 'intuition',
            'name': 'Intuition GUI',
            'description': 'Windowing and GUI system',
            'path': 'rom/intuition'
        },
        {
            'id': 'gallium',
            'name': 'Gallium3D Backend',
            'description': '3D graphics acceleration backend',
            'path': 'workbench/devs/gallium'
        },
        {
            'id': 'mesa',
            'name': 'Mesa Integration',
            'description': 'OpenGL implementation',
            'path': 'workbench/libs/mesa'
        }
    ]
    
    # Check which projects actually exist
    available_projects = []
    if aros_path.exists():
        for project in projects:
            project_path = aros_path / project['path']
            if project_path.exists():
                project['available'] = True
                available_projects.append(project)
            else:
                project['available'] = False
                available_projects.append(project)
    
    return jsonify({
        'projects': available_projects,
        'count': len(available_projects)
    })


if __name__ == '__main__':
    host = config['ui']['host']
    port = config['ui']['port']
    
    # Get local IP for display
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "unknown"
    
    print("")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  AI Breadcrumb Development Monitor                        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    print("Access the UI at:")
    print(f"  - Local:   http://localhost:{port}")
    if local_ip != "unknown" and host == "0.0.0.0":
        print(f"  - Network: http://{local_ip}:{port}")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    
    app.run(host=host, port=port, debug=False)
