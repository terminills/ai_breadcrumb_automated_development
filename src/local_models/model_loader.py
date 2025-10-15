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
    
    def get_codegen_config(self) -> Dict[str, Any]:
        """Get codegen model configuration"""
        return self.config.get("codegen", {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.config.get("llm", {})
    
    def get_exploration_config(self) -> Dict[str, Any]:
        """Get exploration configuration"""
        return self.config.get("exploration", {})
    
    def load_model(self, model_name: str, **kwargs):
        """
        Load a model by name
        Returns the loaded model instance
        """
        if model_name in self.models:
            logger.info(f"Model {model_name} already loaded")
            return self.models[model_name]
        
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
            logger.error(f"Failed to import model {model_name}: {e}")
            logger.info("Some dependencies may be missing. Install with: pip install torch transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def unload_model(self, model_name: str):
        """Unload a model to free memory"""
        if model_name in self.models:
            del self.models[model_name]
            logger.info(f"Unloaded model: {model_name}")
    
    def list_loaded_models(self) -> list:
        """List currently loaded models"""
        return list(self.models.keys())
