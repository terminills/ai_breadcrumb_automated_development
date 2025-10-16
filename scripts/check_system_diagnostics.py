#!/usr/bin/env python3
"""
Comprehensive System Diagnostics for AROS-Cognito
Checks PyTorch, CUDA, ROCm, models, and all dependencies with detailed version info
"""

import importlib
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class DiagnosticChecker:
    """Run comprehensive system diagnostics"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
        
    def check_python(self) -> Dict:
        """Check Python version and environment"""
        return {
            'version': sys.version,
            'version_info': {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor,
                'micro': sys.version_info.micro
            },
            'executable': sys.executable,
            'platform': platform.platform(),
            'architecture': platform.machine()
        }
    
    def check_pytorch(self) -> Dict:
        """Check PyTorch installation and capabilities"""
        result = {
            'installed': False,
            'version': None,
            'cuda_available': False,
            'cuda_version': None,
            'rocm_available': False,
            'rocm_version': None,
            'device_count': 0,
            'devices': [],
            'build_info': {}
        }
        
        try:
            import torch
            result['installed'] = True
            result['version'] = torch.__version__
            
            # Check CUDA
            result['cuda_available'] = torch.cuda.is_available()
            if result['cuda_available']:
                result['cuda_version'] = torch.version.cuda
                result['device_count'] = torch.cuda.device_count()
                
                # Get device info
                for i in range(result['device_count']):
                    device_info = {
                        'id': i,
                        'name': torch.cuda.get_device_name(i),
                        'capability': torch.cuda.get_device_capability(i),
                        'memory': {
                            'total': torch.cuda.get_device_properties(i).total_memory,
                            'allocated': torch.cuda.memory_allocated(i),
                            'cached': torch.cuda.memory_reserved(i)
                        }
                    }
                    result['devices'].append(device_info)
            
            # Check ROCm
            if hasattr(torch.version, 'hip'):
                result['rocm_available'] = True
                result['rocm_version'] = torch.version.hip
            
            # Get build configuration
            result['build_info'] = {
                'cuda_compiled': torch.version.cuda is not None,
                'cudnn_version': torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None,
                'openmp': torch.has_openmp
            }
            
        except ImportError as e:
            result['error'] = str(e)
            self.errors.append(f"PyTorch not installed: {e}")
        except Exception as e:
            result['error'] = str(e)
            self.errors.append(f"Error checking PyTorch: {e}")
        
        return result
    
    def check_transformers(self) -> Dict:
        """Check transformers library"""
        result = {
            'installed': False,
            'version': None,
            'cache_dir': None,
            'models_cached': []
        }
        
        try:
            import transformers
            result['installed'] = True
            result['version'] = transformers.__version__
            
            # Check cache directory
            cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
            result['cache_dir'] = str(cache_dir)
            
            if cache_dir.exists():
                # List cached models
                model_dirs = []
                for item in cache_dir.iterdir():
                    if item.is_dir():
                        model_dirs.append({
                            'name': item.name,
                            'size_mb': sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / (1024 * 1024),
                            'modified': item.stat().st_mtime
                        })
                result['models_cached'] = model_dirs[:10]  # Limit to first 10
                
        except ImportError as e:
            result['error'] = str(e)
            self.errors.append(f"Transformers not installed: {e}")
        except Exception as e:
            result['error'] = str(e)
            self.warnings.append(f"Error checking transformers cache: {e}")
        
        return result
    
    def check_required_packages(self) -> Dict:
        """Check all required Python packages"""
        # Map package names to their import names
        required = {
            'flask': 'flask',
            'torch': 'torch',
            'transformers': 'transformers',
            'GitPython': 'git',
            'psutil': 'psutil',
            'colorama': 'colorama',
            'pyyaml': 'yaml',
            'tqdm': 'tqdm',
            'pyarrow': 'pyarrow',
            'datasets': 'datasets'
        }
        
        results = {}
        for package_name, module_name in required.items():
            try:
                mod = importlib.import_module(module_name)
                version = getattr(mod, '__version__', 'unknown')
                results[package_name] = {
                    'installed': True,
                    'version': version
                }
            except ImportError:
                results[package_name] = {
                    'installed': False,
                    'error': 'Not installed'
                }
                self.warnings.append(f"Package '{package_name}' not installed")
        
        return results
    
    def check_gpu_drivers(self) -> Dict:
        """Check GPU drivers (NVIDIA/AMD)"""
        result = {
            'nvidia': {
                'available': False,
                'driver_version': None,
                'cuda_version': None,
                'gpus': []
            },
            'amd': {
                'available': False,
                'driver_version': None,
                'rocm_version': None,
                'gpus': []
            }
        }
        
        # Check NVIDIA
        try:
            nvidia_smi = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,driver_version,memory.total', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if nvidia_smi.returncode == 0:
                result['nvidia']['available'] = True
                
                for line in nvidia_smi.stdout.strip().split('\n'):
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 4:
                            result['nvidia']['gpus'].append({
                                'id': parts[0],
                                'name': parts[1],
                                'driver': parts[2],
                                'memory': parts[3]
                            })
                            if not result['nvidia']['driver_version']:
                                result['nvidia']['driver_version'] = parts[2]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check AMD ROCm
        try:
            rocm_smi = subprocess.run(
                ['rocm-smi', '--showproductname'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if rocm_smi.returncode == 0:
                result['amd']['available'] = True
                
                # Try to get ROCm version
                try:
                    rocm_version_file = Path('/opt/rocm/.info/version')
                    if rocm_version_file.exists():
                        result['amd']['rocm_version'] = rocm_version_file.read_text().strip()
                except:
                    pass
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return result
    
    def check_disk_space(self) -> Dict:
        """Check available disk space"""
        try:
            import psutil
            
            home_disk = psutil.disk_usage(str(Path.home()))
            cache_dir = Path.home() / ".cache"
            
            result = {
                'home': {
                    'total_gb': home_disk.total / (1024**3),
                    'used_gb': home_disk.used / (1024**3),
                    'free_gb': home_disk.free / (1024**3),
                    'percent_used': home_disk.percent
                }
            }
            
            if cache_dir.exists():
                cache_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                result['cache_size_gb'] = cache_size / (1024**3)
            
            return result
            
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def check_models_status(self) -> Dict:
        """Check status of AI models"""
        result = {
            'codegen': {'installed': False, 'path': None, 'size_mb': None},
            'llama2': {'installed': False, 'path': None, 'size_mb': None}
        }
        
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        if cache_dir.exists():
            # Check for CodeGen
            codegen_dirs = list(cache_dir.glob("*codegen*"))
            if codegen_dirs:
                result['codegen']['installed'] = True
                result['codegen']['path'] = str(codegen_dirs[0])
                result['codegen']['size_mb'] = sum(
                    f.stat().st_size for f in codegen_dirs[0].rglob('*') if f.is_file()
                ) / (1024 * 1024)
            
            # Check for LLaMA-2
            llama_dirs = list(cache_dir.glob("*Llama-2*"))
            if llama_dirs:
                result['llama2']['installed'] = True
                result['llama2']['path'] = str(llama_dirs[0])
                result['llama2']['size_mb'] = sum(
                    f.stat().st_size for f in llama_dirs[0].rglob('*') if f.is_file()
                ) / (1024 * 1024)
        
        return result
    
    def run_all_checks(self) -> Dict:
        """Run all diagnostic checks"""
        print("Running comprehensive system diagnostics...\n")
        
        self.results = {
            'python': self.check_python(),
            'pytorch': self.check_pytorch(),
            'transformers': self.check_transformers(),
            'packages': self.check_required_packages(),
            'gpu_drivers': self.check_gpu_drivers(),
            'disk_space': self.check_disk_space(),
            'models': self.check_models_status()
        }
        
        return self.results
    
    def print_report(self):
        """Print a formatted diagnostic report"""
        print("=" * 80)
        print("  AROS-Cognito System Diagnostics Report")
        print("=" * 80)
        print()
        
        # Python
        print("📦 Python Environment")
        print("-" * 80)
        py = self.results['python']
        print(f"  Version: {py['version_info']['major']}.{py['version_info']['minor']}.{py['version_info']['micro']}")
        print(f"  Executable: {py['executable']}")
        print(f"  Platform: {py['platform']}")
        print(f"  Architecture: {py['architecture']}")
        print()
        
        # PyTorch
        print("🔥 PyTorch")
        print("-" * 80)
        pt = self.results['pytorch']
        if pt['installed']:
            print(f"  ✓ Installed: v{pt['version']}")
            print(f"  CUDA Available: {'Yes' if pt['cuda_available'] else 'No'}")
            if pt['cuda_available']:
                print(f"  CUDA Version: {pt['cuda_version']}")
                print(f"  GPU Count: {pt['device_count']}")
                for gpu in pt['devices']:
                    mem_gb = gpu['memory']['total'] / (1024**3)
                    print(f"    - GPU {gpu['id']}: {gpu['name']} ({mem_gb:.1f}GB)")
            
            if pt['rocm_available']:
                print(f"  ROCm Available: Yes")
                print(f"  ROCm Version: {pt['rocm_version']}")
            else:
                print(f"  ROCm Available: No")
        else:
            print(f"  ✗ Not installed")
            if 'error' in pt:
                print(f"  Error: {pt['error']}")
        print()
        
        # Transformers
        print("🤗 Transformers")
        print("-" * 80)
        tf = self.results['transformers']
        if tf['installed']:
            print(f"  ✓ Installed: v{tf['version']}")
            print(f"  Cache Directory: {tf['cache_dir']}")
            if tf['models_cached']:
                print(f"  Cached Models: {len(tf['models_cached'])}")
                for model in tf['models_cached'][:5]:
                    print(f"    - {model['name'][:60]}... ({model['size_mb']:.1f}MB)")
        else:
            print(f"  ✗ Not installed")
        print()
        
        # GPU Drivers
        print("🎮 GPU Drivers")
        print("-" * 80)
        gpu = self.results['gpu_drivers']
        
        if gpu['nvidia']['available']:
            print(f"  NVIDIA Driver: {gpu['nvidia']['driver_version']}")
            print(f"  GPUs Detected: {len(gpu['nvidia']['gpus'])}")
            for g in gpu['nvidia']['gpus']:
                print(f"    - {g['name']} ({g['memory']})")
        else:
            print("  NVIDIA: Not detected")
        
        if gpu['amd']['available']:
            print(f"  AMD ROCm: {gpu['amd']['rocm_version'] or 'Detected'}")
        else:
            print("  AMD ROCm: Not detected")
        print()
        
        # Disk Space
        print("💾 Disk Space")
        print("-" * 80)
        disk = self.results['disk_space']
        if 'home' in disk:
            print(f"  Total: {disk['home']['total_gb']:.1f}GB")
            print(f"  Used: {disk['home']['used_gb']:.1f}GB ({disk['home']['percent_used']:.1f}%)")
            print(f"  Free: {disk['home']['free_gb']:.1f}GB")
            if 'cache_size_gb' in disk:
                print(f"  Cache Size: {disk['cache_size_gb']:.1f}GB")
        print()
        
        # Models
        print("🤖 AI Models")
        print("-" * 80)
        models = self.results['models']
        
        if models['codegen']['installed']:
            print(f"  ✓ CodeGen: Installed ({models['codegen']['size_mb']:.1f}MB)")
            print(f"    Path: {models['codegen']['path']}")
        else:
            print(f"  ✗ CodeGen: Not installed")
        
        if models['llama2']['installed']:
            print(f"  ✓ LLaMA-2: Installed ({models['llama2']['size_mb']:.1f}MB)")
            print(f"    Path: {models['llama2']['path']}")
        else:
            print(f"  ✗ LLaMA-2: Not installed")
        print()
        
        # Required Packages
        print("📚 Required Packages")
        print("-" * 80)
        packages = self.results['packages']
        
        installed = [name for name, info in packages.items() if info['installed']]
        missing = [name for name, info in packages.items() if not info['installed']]
        
        print(f"  Installed: {len(installed)}/{len(packages)}")
        
        if missing:
            print(f"  Missing packages:")
            for pkg in missing:
                print(f"    - {pkg}")
        else:
            print(f"  ✓ All required packages installed")
        
        print()
        
        # Summary
        print("=" * 80)
        print("  Summary")
        print("=" * 80)
        
        issues = []
        
        if not pt['installed']:
            issues.append("❌ PyTorch is not installed")
        elif not pt['cuda_available'] and not pt['rocm_available']:
            issues.append("⚠️  No GPU acceleration available (CPU only)")
        
        if not tf['installed']:
            issues.append("❌ Transformers library not installed")
        
        if not models['codegen']['installed'] and not models['llama2']['installed']:
            issues.append("⚠️  No AI models installed")
        
        if missing:
            issues.append(f"⚠️  {len(missing)} required packages missing")
        
        if disk.get('home', {}).get('free_gb', 0) < 15:
            issues.append("⚠️  Low disk space (< 15GB free)")
        
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  {issue}")
            print()
            print("Recommendations:")
            if not pt['installed'] or not tf['installed']:
                print("  1. Install PyTorch and Transformers:")
                print("     pip install torch transformers")
            if not models['codegen']['installed']:
                print("  2. Download AI models:")
                print("     python3 scripts/download_models.py --codegen")
            if missing:
                print("  3. Install missing packages:")
                print(f"     pip install {' '.join(missing)}")
        else:
            print("✓ System is ready for AI development!")
        
        print()
        print("=" * 80)
    
    def export_json(self, output_file: str):
        """Export results as JSON"""
        import json
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"Diagnostics exported to: {output_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run comprehensive system diagnostics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--json',
        type=str,
        metavar='FILE',
        help='Export results to JSON file'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    
    checker = DiagnosticChecker()
    checker.run_all_checks()
    
    if not args.quiet:
        checker.print_report()
    
    if args.json:
        checker.export_json(args.json)
    
    # Return exit code based on critical issues
    if not checker.results['pytorch']['installed']:
        return 1
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDiagnostics cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error running diagnostics: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
