"""
Local Model Integration
Provides interfaces for local codegen and LLM models
"""

import sys
from unittest.mock import MagicMock


def _apply_pytorch_onnx_workaround():
    """
    Apply workaround for PyTorch 2.3.1+ DiagnosticOptions import error.
    
    PyTorch 2.3.1+ changed internal ONNX APIs that transformers/accelerate rely on.
    This workaround prevents the ImportError by mocking the problematic module.
    
    See: https://github.com/huggingface/transformers/issues/XXXXX
    """
    if 'torch.onnx._internal.exporter' not in sys.modules:
        sys.modules['torch.onnx._internal.exporter'] = MagicMock()


# Apply the workaround early to prevent import errors
_apply_pytorch_onnx_workaround()

from .model_loader import LocalModelLoader
from .codegen_model import CodegenModel
from .llm_interface import LocalLLM
from .mock_models import MockCodegenModel, MockLLM

__all__ = ['LocalModelLoader', 'CodegenModel', 'LocalLLM', 'MockCodegenModel', 'MockLLM']
