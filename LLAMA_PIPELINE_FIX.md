# Llama Pipeline Parameter Fix

## Issue
Users may encounter errors when testing Llama models directly with the transformers `pipeline()` function. There are typically two issues:

1. **Compatibility Error**: `ImportError: cannot import name 'DiagnosticOptions' from 'torch.onnx._internal.exporter'`
   - This is a PyTorch 2.3.1+ API change that requires updated transformers/accelerate packages
   - **Fix**: Upgrade transformers>=4.40.0 and accelerate>=0.26.0, or use workarounds (see AI_MODEL_SETUP.md)
   - Note: Upgrading ONNX alone does NOT fix this issue
   - See `AI_MODEL_SETUP.md` for detailed troubleshooting steps including Python code workarounds

2. **Parameter Naming Error**: Using `torch_dtype` instead of `dtype` with `pipeline()`
   - This is documented below

## Problem - Parameter Naming
The second issue stems from using `torch_dtype="auto"` with the `pipeline()` function:

```python
# INCORRECT - causes errors
pipe = pipeline(
    "text-generation",
    model="meta-llama/Llama-2-7b-chat-hf",
    torch_dtype="auto",  # ❌ Wrong parameter name
    device_map="auto"
)
```

## Root Cause
The transformers library uses **different parameter names** depending on how you load the model:

- **pipeline() function**: Uses `dtype` parameter
- **from_pretrained() method**: Uses `torch_dtype` parameter

This inconsistency can be confusing for users.

## Solution
The correct usage for `pipeline()` is:

```python
# CORRECT
pipe = pipeline(
    "text-generation",
    model="meta-llama/Llama-2-7b-chat-hf",
    dtype="auto",  # ✅ Correct parameter name
    device_map="auto"
)
```

## Changes Made

### 1. Documentation (AI_MODEL_SETUP.md)
Added a comprehensive section explaining the difference between the two methods:
- Clear examples for both `pipeline()` and `from_pretrained()`
- Parameter reference table showing which parameter to use with each method
- Common error warnings

### 2. Example Script (examples/llama_pipeline_example.py)
Created a detailed example script that:
- Demonstrates CORRECT usage with `dtype`
- Shows INCORRECT usage with `torch_dtype` (and explains why it fails)
- Explains when to use each loading method
- Provides a parameter reference guide
- Shows valid dtype values

### 3. Tests (tests/test_llama_pipeline_params.py)
Added comprehensive tests to:
- Verify `pipeline()` accepts `dtype` parameter
- Verify `from_pretrained()` accepts `torch_dtype` parameter (via kwargs)
- Validate that our codebase uses the correct parameters
- Check that documentation exists for the parameter difference
- Test valid dtype values

## Parameter Reference

| Function | Parameter | Valid Values |
|----------|-----------|--------------|
| `pipeline()` | `dtype` | `"auto"`, `torch.float16`, `torch.float32`, `torch.bfloat16` |
| `from_pretrained()` | `torch_dtype` | `torch.float16`, `torch.float32`, `torch.bfloat16` |

## Why This Matters
Using the wrong parameter name can cause:
- TypeError exceptions
- Unexpected model behavior
- Models loading with wrong precision
- Confusion for developers new to transformers

## Verification
Our existing codebase already uses the correct parameters:
- `src/local_models/llm_interface.py` - Uses `torch_dtype` with `from_pretrained()` ✅
- `src/local_models/codegen_model.py` - Uses `torch_dtype` with `from_pretrained()` ✅

## How to Use

### Troubleshooting Steps
If you encounter errors when testing Llama models:

1. **First, fix DiagnosticOptions compatibility error** (PyTorch 2.3.1+ API change):
   ```bash
   # Upgrade transformers and accelerate (most reliable fix)
   pip install --upgrade transformers>=4.40.0 accelerate>=0.26.0
   ```
   
   **If that doesn't work**, use this Python workaround:
   ```python
   # Add at the very top of your script, before any transformers imports
   import sys
   from unittest.mock import MagicMock
   sys.modules['torch.onnx._internal.exporter'] = MagicMock()
   
   # Now import transformers
   from transformers import pipeline
   ```
   
   See `AI_MODEL_SETUP.md` for more solutions including environment variables.
   
   **Note**: 
   - Upgrading ONNX alone does NOT fix this issue.
   - The Python workaround is **automatically applied** in the AROS-Cognito codebase when using `src.local_models` modules.

2. **Then, fix parameter naming**:
   - Change `torch_dtype="auto"` to `dtype="auto"` in your `pipeline()` call
   - See examples below for correct usage

### For end users:
1. Read the updated `AI_MODEL_SETUP.md` for detailed guidance
2. Run `python3 examples/llama_pipeline_example.py` to see examples
3. Use the parameter reference table above
4. When using the AROS-Cognito model loaders, the DiagnosticOptions workaround is automatically applied

### For developers:
1. Use `dtype` when calling `pipeline()`
2. Use `torch_dtype` when calling `from_pretrained()`
3. Run `python3 -m unittest tests/test_llama_pipeline_params.py` to verify correctness
4. The DiagnosticOptions workaround is automatically applied in `src.local_models.__init__.py`, `llm_interface.py`, `codegen_model.py`, and `scripts/download_models.py`

## Related Files
- `AI_MODEL_SETUP.md` - Updated documentation
- `examples/llama_pipeline_example.py` - New example script
- `tests/test_llama_pipeline_params.py` - New test suite
- `src/local_models/llm_interface.py` - Existing code (already correct)
- `src/local_models/codegen_model.py` - Existing code (already correct)
