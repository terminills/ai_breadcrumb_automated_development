#!/usr/bin/env python3
"""
Example: Using Llama-2 with Transformers Pipeline
Demonstrates the correct way to use the transformers pipeline with Llama models.

IMPORTANT: The pipeline() function uses 'dtype' parameter, NOT 'torch_dtype'
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def example_correct_usage():
    """Demonstrates CORRECT usage of pipeline with Llama"""
    try:
        from transformers import pipeline
        import torch
        
        print("=" * 70)
        print("CORRECT: Using 'dtype' parameter with pipeline()")
        print("=" * 70)
        
        # CORRECT: Use 'dtype' parameter (not 'torch_dtype')
        pipe = pipeline(
            "text-generation",
            model="meta-llama/Llama-2-7b-chat-hf",
            dtype="auto",  # CORRECT: 'dtype' parameter
            device_map="auto"
        )
        
        prompt = "Explain the AI breadcrumb patent concept in under 150 words:"
        out = pipe(prompt, max_new_tokens=200)
        print(out[0]["generated_text"])
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This example requires the model to be downloaded.")
        print("Run: python3 scripts/download_models.py --all --token YOUR_HF_TOKEN")


def example_incorrect_usage():
    """Demonstrates INCORRECT usage (what causes the error)"""
    try:
        from transformers import pipeline
        
        print("\n" + "=" * 70)
        print("INCORRECT: Using 'torch_dtype' parameter with pipeline()")
        print("=" * 70)
        
        # INCORRECT: 'torch_dtype' is not a valid parameter for pipeline()
        # This will cause a TypeError or unexpected behavior
        pipe = pipeline(
            "text-generation",
            model="meta-llama/Llama-2-7b-chat-hf",
            torch_dtype="auto",  # WRONG: 'torch_dtype' is not valid here
            device_map="auto"
        )
        
        prompt = "Test prompt"
        out = pipe(prompt, max_new_tokens=10)
        print(out[0]["generated_text"])
        
    except TypeError as e:
        print(f"TypeError as expected: {e}")
        print("\nThe 'torch_dtype' parameter is NOT valid for pipeline().")
        print("Use 'dtype' instead!")
    except Exception as e:
        print(f"Error: {e}")


def example_using_from_pretrained():
    """Demonstrates using from_pretrained() directly (where torch_dtype IS valid)"""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        print("\n" + "=" * 70)
        print("CORRECT: Using 'torch_dtype' with from_pretrained()")
        print("=" * 70)
        
        # When using from_pretrained() directly, 'torch_dtype' IS the correct parameter
        model_path = "meta-llama/Llama-2-7b-chat-hf"
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,  # CORRECT: 'torch_dtype' with from_pretrained()
            low_cpu_mem_usage=True,
            device_map="auto"
        )
        
        print("Model loaded successfully!")
        print(f"Model dtype: {model.dtype}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This example requires the model to be downloaded.")


def show_parameter_reference():
    """Show parameter reference for both methods"""
    print("\n" + "=" * 70)
    print("PARAMETER REFERENCE")
    print("=" * 70)
    
    print("\n1. Using pipeline() function:")
    print("   ✓ CORRECT: dtype='auto' or dtype=torch.float16")
    print("   ✗ WRONG:   torch_dtype='auto' or torch_dtype=torch.float16")
    print()
    print("   Example:")
    print("   pipe = pipeline('text-generation', model='...', dtype='auto')")
    
    print("\n2. Using from_pretrained() directly:")
    print("   ✓ CORRECT: torch_dtype=torch.float16")
    print("   ✗ WRONG:   dtype=torch.float16")
    print()
    print("   Example:")
    print("   model = AutoModelForCausalLM.from_pretrained(")
    print("       '...', torch_dtype=torch.float16)")
    
    print("\n3. Valid dtype values:")
    print("   - 'auto' (string, lets transformers decide)")
    print("   - torch.float16 (half precision)")
    print("   - torch.float32 (full precision)")
    print("   - torch.bfloat16 (bfloat16 precision, requires compatible hardware)")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point"""
    print("\nLlama Pipeline Usage Examples")
    print("=" * 70)
    print()
    print("This script demonstrates the correct way to use Llama models")
    print("with the transformers library.")
    print()
    
    # Show parameter reference first
    show_parameter_reference()
    
    # Show examples (will fail without downloaded models, but that's OK)
    print("\n\nAttempting to run examples...")
    print("(These will fail if models are not downloaded - that's expected)")
    print()
    
    # Show incorrect usage first to illustrate the problem
    example_incorrect_usage()
    
    # Then show correct usage
    example_correct_usage()
    
    # Show alternative method
    example_using_from_pretrained()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ Use 'dtype' with pipeline()")
    print("✓ Use 'torch_dtype' with from_pretrained()")
    print("✓ Both methods work, but use different parameter names!")
    print("=" * 70)


if __name__ == "__main__":
    main()
