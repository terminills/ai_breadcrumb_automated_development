#!/usr/bin/env python3
"""
Helper script to download AI models for AROS-Cognito
Supports downloading CodeGen and LLaMA-2 models with progress tracking
"""

import sys
import os
import argparse
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed with detailed diagnostics"""
    missing = []
    torch_info = {}
    transformers_info = {}
    
    try:
        import torch
        torch_info = {
            'version': torch.__version__,
            'cuda_available': torch.cuda.is_available(),
            'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
            'rocm_available': hasattr(torch.version, 'hip'),
            'rocm_version': torch.version.hip if hasattr(torch.version, 'hip') else None,
            'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
    except ImportError:
        missing.append("torch")
    except Exception as e:
        print(f"⚠️  PyTorch is installed but has issues: {e}")
    
    try:
        import transformers
        transformers_info = {
            'version': transformers.__version__
        }
    except ImportError:
        missing.append("transformers")
    except Exception as e:
        print(f"⚠️  Transformers is installed but has issues: {e}")
    
    if missing:
        print("❌ Missing required dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\nInstall with:")
        print("   pip install torch transformers")
        return False
    
    # Print detailed info when dependencies are available
    print("\n✓ PyTorch Information:")
    print(f"  Version: {torch_info.get('version', 'unknown')}")
    print(f"  CUDA Available: {torch_info.get('cuda_available', False)}")
    if torch_info.get('cuda_available'):
        print(f"  CUDA Version: {torch_info.get('cuda_version', 'unknown')}")
        print(f"  GPU Count: {torch_info.get('device_count', 0)}")
        
        # Show GPU details
        try:
            import torch
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                print(f"    GPU {i}: {gpu_name} ({gpu_mem:.1f}GB)")
        except Exception as e:
            print(f"  Could not get GPU details: {e}")
    
    if torch_info.get('rocm_available'):
        print(f"  ROCm Available: Yes")
        print(f"  ROCm Version: {torch_info.get('rocm_version', 'unknown')}")
    
    print(f"\n✓ Transformers Version: {transformers_info.get('version', 'unknown')}")
    
    return True


def download_codegen(force=False):
    """Download CodeGen model"""
    print("\n" + "="*60)
    print("  Downloading CodeGen Model")
    print("="*60)
    print("\nModel: Salesforce/codegen-350M-mono")
    print("Size: ~350MB")
    print("Purpose: Code generation")
    print("")
    
    if not force:
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return False
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("\n📥 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
        print("✓ Tokenizer downloaded")
        
        print("\n📥 Downloading model (this may take a few minutes)...")
        model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
        print("✓ Model downloaded")
        
        print("\n" + "="*60)
        print("  ✓ CodeGen installation complete!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading CodeGen: {e}")
        return False


def download_llama2(hf_token=None, force=False):
    """Download LLaMA-2 model"""
    print("\n" + "="*60)
    print("  Downloading LLaMA-2 Model")
    print("="*60)
    print("\nModel: meta-llama/Llama-2-7b-chat-hf")
    print("Size: ~13GB")
    print("Purpose: Reasoning and exploration")
    print("")
    
    # Check for HuggingFace token
    if not hf_token:
        hf_token = os.environ.get('HF_TOKEN')
    
    if not hf_token:
        print("⚠️  LLaMA-2 requires a HuggingFace token")
        print("")
        print("To get a token:")
        print("  1. Visit: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf")
        print("  2. Click 'Access repository' and fill out the form")
        print("  3. Go to: https://huggingface.co/settings/tokens")
        print("  4. Create a token with 'Read' access")
        print("")
        
        token_input = input("Enter your HuggingFace token (or press Enter to skip): ").strip()
        if not token_input:
            print("Skipped LLaMA-2 installation.")
            return False
        hf_token = token_input
    
    if not force:
        print("\n⚠️  This will download ~13GB of data")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return False
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("\n📥 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf",
            use_auth_token=hf_token
        )
        print("✓ Tokenizer downloaded")
        
        print("\n📥 Downloading model (~13GB - this may take 10-30 minutes)...")
        print("   Progress indicators may not show, please be patient...")
        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf",
            use_auth_token=hf_token
        )
        print("✓ Model downloaded")
        
        print("\n" + "="*60)
        print("  ✓ LLaMA-2 installation complete!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading LLaMA-2: {e}")
        print("\nPossible issues:")
        print("  - Invalid HuggingFace token")
        print("  - Repository access not granted")
        print("  - Network connection issues")
        print("  - Insufficient disk space")
        return False


def check_models():
    """Check which models are already downloaded"""
    print("\n" + "="*60)
    print("  Checking Installed Models")
    print("="*60)
    
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    models_status = {
        'CodeGen': False,
        'LLaMA-2': False
    }
    
    if cache_dir.exists():
        # Check for CodeGen
        codegen_dirs = list(cache_dir.glob("*codegen*"))
        if codegen_dirs:
            models_status['CodeGen'] = True
            print(f"\n✓ CodeGen: Installed")
            print(f"  Location: {codegen_dirs[0]}")
        else:
            print(f"\n✗ CodeGen: Not installed")
        
        # Check for LLaMA-2
        llama_dirs = list(cache_dir.glob("*Llama-2-7b-chat*"))
        if llama_dirs:
            models_status['LLaMA-2'] = True
            print(f"\n✓ LLaMA-2: Installed")
            print(f"  Location: {llama_dirs[0]}")
        else:
            print(f"\n✗ LLaMA-2: Not installed")
    else:
        print("\n✗ No models installed")
        print(f"  Cache directory does not exist: {cache_dir}")
    
    print("\n" + "="*60)
    
    return models_status


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download AI models for AROS-Cognito",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check which models are installed
  %(prog)s --check
  
  # Download CodeGen only (smaller, ~350MB)
  %(prog)s --codegen
  
  # Download both models
  %(prog)s --all
  
  # Download with HuggingFace token
  %(prog)s --all --token YOUR_HF_TOKEN
  
  # Download LLaMA-2 only
  %(prog)s --llama --token YOUR_HF_TOKEN

Note: The system works with mock models if real models aren't installed.
      Real models provide intelligent AI responses.
        """
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check which models are already installed'
    )
    parser.add_argument(
        '--codegen',
        action='store_true',
        help='Download CodeGen model (~350MB)'
    )
    parser.add_argument(
        '--llama',
        action='store_true',
        help='Download LLaMA-2 model (~13GB, requires HF token)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all models'
    )
    parser.add_argument(
        '--token',
        type=str,
        help='HuggingFace access token for LLaMA-2'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*60)
    print("  AROS-Cognito AI Model Installer")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("\n✓ Dependencies installed")
    
    # Handle check command
    if args.check:
        check_models()
        return 0
    
    # If no action specified, show help
    if not (args.codegen or args.llama or args.all):
        models_status = check_models()
        
        print("\nWhat would you like to do?")
        print("  1. Download CodeGen only (lightweight, ~350MB)")
        print("  2. Download LLaMA-2 only (requires HF token, ~13GB)")
        print("  3. Download both models")
        print("  4. Exit")
        print("")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            args.codegen = True
        elif choice == '2':
            args.llama = True
        elif choice == '3':
            args.all = True
        else:
            print("Exiting.")
            return 0
    
    # Download models
    success = True
    
    if args.codegen or args.all:
        if not download_codegen(force=args.force):
            success = False
    
    if args.llama or args.all:
        if not download_llama2(hf_token=args.token, force=args.force):
            success = False
    
    # Final status
    print("\n" + "="*60)
    if success:
        print("  ✓ Installation Complete!")
        print("="*60)
        print("\nYou can now use real AI models in the system.")
        print("\nTo verify, run:")
        print("  python3 tests/test_mock_models.py")
    else:
        print("  ⚠️  Installation Incomplete")
        print("="*60)
        print("\nSome models failed to install.")
        print("The system will use mock models as fallback.")
        print("\nFor help, see: AI_MODEL_SETUP.md")
    print("")
    
    return 0 if success else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
