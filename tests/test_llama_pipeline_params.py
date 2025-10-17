"""
Test for correct parameter usage with transformers pipeline and from_pretrained.
This test validates that we're using the correct parameter names for different loading methods.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import inspect

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLlamaPipelineParams(unittest.TestCase):
    """Test correct parameter usage for Llama model loading"""

    def test_pipeline_uses_dtype_parameter(self):
        """Test that pipeline() should use 'dtype' parameter, not 'torch_dtype'"""
        # We don't actually call pipeline() since it requires network access
        # Instead, we verify that the transformers.pipeline function signature accepts 'dtype'
        from transformers import pipeline
        import inspect
        
        # Get the signature of the pipeline function
        sig = inspect.signature(pipeline)
        params = sig.parameters
        
        # Verify that 'dtype' is a valid parameter
        self.assertIn('dtype', params, "pipeline() should accept 'dtype' parameter")
        
        # Verify the default value is 'auto'
        dtype_param = params['dtype']
        self.assertEqual(dtype_param.default, 'auto', "dtype default should be 'auto'")

    def test_from_pretrained_uses_torch_dtype_parameter(self):
        """Test that from_pretrained() should use 'torch_dtype' parameter"""
        from transformers import AutoModelForCausalLM
        import inspect
        
        # Get the signature of from_pretrained
        sig = inspect.signature(AutoModelForCausalLM.from_pretrained)
        params = sig.parameters
        
        # from_pretrained uses **kwargs, so torch_dtype is passed through kwargs
        # We verify that kwargs is present
        self.assertIn('kwargs', params, 
                     "AutoModelForCausalLM.from_pretrained() should accept **kwargs for torch_dtype")
        
        # Verify it's a VAR_KEYWORD parameter (**kwargs)
        self.assertEqual(params['kwargs'].kind, inspect.Parameter.VAR_KEYWORD,
                        "kwargs should be a VAR_KEYWORD parameter (**kwargs)")

    def test_parameter_documentation(self):
        """Test that we have documentation about the parameter difference"""
        # Check that the example file exists
        example_file = Path(__file__).parent.parent / "examples" / "llama_pipeline_example.py"
        self.assertTrue(example_file.exists(), 
                       "llama_pipeline_example.py should exist to document the parameter difference")
        
        # Check that it mentions both parameters
        content = example_file.read_text()
        self.assertIn("dtype", content, "Example should mention 'dtype' parameter")
        self.assertIn("torch_dtype", content, "Example should mention 'torch_dtype' parameter")
        self.assertIn("pipeline", content, "Example should mention pipeline() function")
        self.assertIn("from_pretrained", content, "Example should mention from_pretrained() function")

    def test_local_models_use_correct_parameters(self):
        """Test that our local model implementations use correct parameters"""
        # Check llm_interface.py
        llm_file = Path(__file__).parent.parent / "src" / "local_models" / "llm_interface.py"
        self.assertTrue(llm_file.exists(), "llm_interface.py should exist")
        
        content = llm_file.read_text()
        # Should use torch_dtype with from_pretrained (not pipeline)
        self.assertIn("torch_dtype", content, "llm_interface.py should use torch_dtype")
        self.assertIn("from_pretrained", content, "llm_interface.py should use from_pretrained")
        
        # Check codegen_model.py
        codegen_file = Path(__file__).parent.parent / "src" / "local_models" / "codegen_model.py"
        self.assertTrue(codegen_file.exists(), "codegen_model.py should exist")
        
        content = codegen_file.read_text()
        # Should use torch_dtype with from_pretrained (not pipeline)
        self.assertIn("torch_dtype", content, "codegen_model.py should use torch_dtype")
        self.assertIn("from_pretrained", content, "codegen_model.py should use from_pretrained")


class TestDtypeValidation(unittest.TestCase):
    """Test that dtype/torch_dtype values are used correctly"""

    def test_valid_dtype_values(self):
        """Test that valid dtype values are recognized"""
        import torch
        
        # Valid dtype values
        valid_dtypes = [
            "auto",
            torch.float16,
            torch.float32,
            torch.bfloat16,
        ]
        
        for dtype in valid_dtypes:
            # Just check that these are valid types
            if isinstance(dtype, str):
                self.assertEqual(dtype, "auto")
            else:
                self.assertTrue(hasattr(torch, dtype.__str__().split('.')[1]))


if __name__ == '__main__':
    unittest.main()
