#!/usr/bin/env python3
"""
Test script to demonstrate model loader diagnostic error messages
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from local_models.model_loader import LocalModelLoader
    
    loader = LocalModelLoader()
    # This will fail because torch is not installed
    loader.load_model('codegen', use_mock=False)
except Exception as e:
    print('Caught expected error:')
    error_msg = str(e)
    # Print first 800 chars to show diagnostic info
    if len(error_msg) > 800:
        print(error_msg[:800] + '...')
    else:
        print(error_msg)
