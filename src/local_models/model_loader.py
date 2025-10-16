"""
Local Model Loader
Handles loading and initialization of local AI models
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LocalModelLoader:
    """Loads and manages local AI models"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._default_config_path()
        self.config = self._load_config()
        self.models = {}
        
    def _default_config_path(self) -> str:
        """Get default config path"""
        return str(Path(__file__).parent.parent.parent / "config" / "models.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Model config not found at {self.config_path}, using defaults")
            return self._default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading model config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "codegen": {
                "model_type": "salesforce/codegen",
                "model_path": "models/codegen-350M-mono",
                "device": "cpu",
                "max_length": 512,
                "temperature": 0.7,
                "top_p": 0.95
            },
            "llm": {
                "model_type": "local",
                "model_path": "models/llama-2-7b",
                "device": "cpu",
                "max_length": 2048,
                "temperature": 0.8,
                "context_window": 4096
            },
            "exploration": {
                "enabled": True,
                "max_files_to_scan": 50,
                "similarity_threshold": 0.7
            }
        }
    
    def _get_diagnostic_info(self) -> str:
        """Get diagnostic information about system state"""
        info_lines = []
        
        # Check PyTorch
        try:
            import torch
            info_lines.append(f"  PyTorch: v{torch.__version__} ✓")
            
            if torch.cuda.is_available():
                info_lines.append(f"  CUDA: v{torch.version.cuda} ({torch.cuda.device_count()} GPU(s)) ✓")
                for i in range(torch.cuda.device_count()):
                    gpu_name = torch.cuda.get_device_name(i)
                    info_lines.append(f"    - GPU {i}: {gpu_name}")
            else:
                info_lines.append(f"  CUDA: Not available (CPU only)")
            
            if hasattr(torch.version, 'hip'):
                info_lines.append(f"  ROCm: v{torch.version.hip} ✓")
            
        except ImportError:
            info_lines.append("  PyTorch: Not installed ✗")
        except Exception as e:
            info_lines.append(f"  PyTorch: Error - {e}")
        
        # Check Transformers
        try:
            import transformers
            info_lines.append(f"  Transformers: v{transformers.__version__} ✓")
        except ImportError:
            info_lines.append("  Transformers: Not installed ✗")
        except Exception as e:
            info_lines.append(f"  Transformers: Error - {e}")
        
        # Check disk space
        try:
            import psutil
            disk = psutil.disk_usage(str(Path.home()))
            free_gb = disk.free / (1024**3)
            info_lines.append(f"  Disk Space: {free_gb:.1f}GB free")
            
            if free_gb < 15:
                info_lines.append("    ⚠️  Low disk space - may cause model loading issues")
        except:
            pass
        
        # Check models
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        if cache_dir.exists():
            codegen_exists = bool(list(cache_dir.glob("*codegen*")))
            llama_exists = bool(list(cache_dir.glob("*Llama-2*")))
            
            if codegen_exists:
                info_lines.append("  CodeGen Model: Downloaded ✓")
            else:
                info_lines.append("  CodeGen Model: Not downloaded ✗")
            
            if llama_exists:
                info_lines.append("  LLaMA-2 Model: Downloaded ✓")
            else:
                info_lines.append("  LLaMA-2 Model: Not downloaded ✗")
        else:
            info_lines.append("  Models: None downloaded")
        
        return "\n".join(info_lines)
    
    def get_codegen_config(self) -> Dict[str, Any]:
        """Get codegen model configuration"""
        return self.config.get("codegen", {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.config.get("llm", {})
    
    def get_exploration_config(self) -> Dict[str, Any]:
        """Get exploration configuration"""
        return self.config.get("exploration", {})
    
    def load_model(self, model_name: str, use_mock: bool = False, **kwargs):
        """
        Load a model by name
        Returns the loaded model instance
        
        Args:
            model_name: Name of the model to load ('codegen', 'llm')
            use_mock: If True, explicitly use mock model (for testing only)
            **kwargs: Additional configuration options
        """
        if model_name in self.models:
            logger.info(f"Model {model_name} already loaded")
            return self.models[model_name]
        
        # If explicitly requested, use mock model
        if use_mock:
            return self._load_mock_model(model_name)
        
        try:
            if model_name == "codegen":
                from .codegen_model import CodegenModel
                config = self.get_codegen_config()
                config.update(kwargs)
                model = CodegenModel(config)
                self.models[model_name] = model
                return model
            
            elif model_name == "llm":
                from .llm_interface import LocalLLM
                config = self.get_llm_config()
                config.update(kwargs)
                model = LocalLLM(config)
                self.models[model_name] = model
                return model
            
            else:
                raise ValueError(f"Unknown model name: {model_name}")
                
        except ImportError as e:
            error_msg = self._format_missing_dependency_error(model_name, e)
            logger.error(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            error_msg = self._format_model_load_error(model_name, e)
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _format_missing_dependency_error(self, model_name: str, error: Exception) -> str:
        """Format a helpful error message for missing dependencies"""
        diagnostic_info = self._get_diagnostic_info()
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║  AI MODEL DEPENDENCY ERROR                                       ║
╚══════════════════════════════════════════════════════════════════╝

Failed to load {model_name} model: {error}

DIAGNOSTIC INFORMATION:
{diagnostic_info}

PROBLEM:
  Required Python packages are not installed or have compatibility issues.

SOLUTION:
  1. Run system diagnostics:
     $ python3 scripts/check_system_diagnostics.py
  
  2. Install the required dependencies:
     $ pip install torch transformers
  
  3. Or use the setup script:
     $ ./scripts/setup.sh

For more information, see: AI_MODEL_SETUP.md

Note: You can use --use-mock flag for testing without real models,
      but this will only provide template-based responses.
"""
    
    def _format_model_load_error(self, model_name: str, error: Exception) -> str:
        """Format a helpful error message for model loading failures"""
        error_str = str(error)
        
        # Check if it's a model not found error
        if "not found" in error_str.lower() or "no such file" in error_str.lower():
            return f"""
╔══════════════════════════════════════════════════════════════════╗
║  AI MODEL NOT FOUND                                              ║
╚══════════════════════════════════════════════════════════════════╝

Failed to load {model_name} model: {error}

PROBLEM:
  The AI model files are not downloaded.

SOLUTION:
  Download the required models using:
  
  $ python3 scripts/download_models.py --{model_name}
  
  Or download all models:
  
  $ python3 scripts/download_models.py --all

QUICK FIX:
  For CodeGen only (~350MB):
  $ python3 scripts/download_models.py --codegen
  
  For full AI stack (~13GB, requires HuggingFace token):
  $ python3 scripts/download_models.py --all --token YOUR_HF_TOKEN

For detailed instructions, see: AI_MODEL_SETUP.md

Note: You can use --use-mock flag for testing without real models,
      but this will only provide template-based responses.
"""
        else:
            return f"""
╔══════════════════════════════════════════════════════════════════╗
║  AI MODEL LOADING ERROR                                          ║
╚══════════════════════════════════════════════════════════════════╝

Failed to load {model_name} model: {error}

TROUBLESHOOTING:
  1. Check if you have enough disk space (~13GB needed)
  2. Verify PyTorch is installed: pip install torch transformers
  3. Try downloading models: python3 scripts/download_models.py --check
  4. See detailed guide: AI_MODEL_SETUP.md

NEED HELP?
  • Check model status: python3 scripts/download_models.py --check
  • View setup guide: cat AI_MODEL_SETUP.md
  • Run bootstrap: ./scripts/bootstrap_ubuntu.sh

Note: You can use --use-mock flag for testing without real models,
      but this will only provide template-based responses.
"""
    
    def _load_mock_model(self, model_name: str):
        """
        Load a mock model for testing when explicitly requested
        
        Args:
            model_name: Name of the model to mock
            
        Returns:
            Mock model instance
        """
        from .mock_models import MockCodegenModel, MockLLM
        
        logger.warning("="*70)
        logger.warning("  USING MOCK MODEL - NOT REAL AI")
        logger.warning("="*70)
        logger.warning(f"Mock {model_name} model will provide template-based responses only.")
        logger.warning("For real AI capabilities, install models: python3 scripts/download_models.py")
        logger.warning("="*70)
        
        if model_name == "codegen":
            config = self.get_codegen_config()
            model = MockCodegenModel(config)
            self.models[model_name] = model
            return model
        elif model_name == "llm":
            config = self.get_llm_config()
            model = MockLLM(config)
            self.models[model_name] = model
            return model
        else:
            raise ValueError(f"Unknown model name for mocking: {model_name}")
    
    def unload_model(self, model_name: str):
        """Unload a model to free memory"""
        if model_name in self.models:
            del self.models[model_name]
            logger.info(f"Unloaded model: {model_name}")
    
    def list_loaded_models(self) -> list:
        """List currently loaded models"""
        return list(self.models.keys())
