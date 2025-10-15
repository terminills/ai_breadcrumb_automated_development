#!/bin/bash
# Setup script for AROS-Cognito system
# Handles PyTorch installation with optional AMD ROCm support

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
USE_AMD=false
ROCM_VERSION=""
PYTORCH_VERSION="2.3.1"

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --amd           Install PyTorch with AMD ROCm support
    -h, --help      Display this help message

Examples:
    $0              Install generic PyTorch (CPU/CUDA)
    $0 --amd        Install PyTorch with ROCm support (auto-detect version)

EOF
    exit 0
}

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect ROCm version
detect_rocm_version() {
    echo "Detecting ROCm version..."
    
    # Method 1: Check rocminfo
    if command_exists rocminfo; then
        local rocm_ver=$(rocminfo 2>/dev/null | grep "Runtime Version" | head -1 | awk '{print $3}' | cut -d'.' -f1,2)
        if [ -n "$rocm_ver" ]; then
            echo "$rocm_ver"
            return 0
        fi
    fi
    
    # Method 2: Check /opt/rocm/.info/version
    if [ -f "/opt/rocm/.info/version" ]; then
        local rocm_ver=$(cat /opt/rocm/.info/version | cut -d'-' -f1 | cut -d'.' -f1,2)
        if [ -n "$rocm_ver" ]; then
            echo "$rocm_ver"
            return 0
        fi
    fi
    
    # Method 3: Check /opt/rocm/bin/.info/version
    if [ -f "/opt/rocm/bin/.info/version" ]; then
        local rocm_ver=$(cat /opt/rocm/bin/.info/version | cut -d'-' -f1 | cut -d'.' -f1,2)
        if [ -n "$rocm_ver" ]; then
            echo "$rocm_ver"
            return 0
        fi
    fi
    
    # Method 4: Check dpkg for ROCm packages
    if command_exists dpkg; then
        local rocm_ver=$(dpkg -l | grep rocm-dev | awk '{print $3}' | cut -d'.' -f1,2 | head -1)
        if [ -n "$rocm_ver" ]; then
            echo "$rocm_ver"
            return 0
        fi
    fi
    
    # Method 5: Check rpm for ROCm packages (for RPM-based distros)
    if command_exists rpm; then
        local rocm_ver=$(rpm -qa | grep rocm | head -1 | grep -oP '\d+\.\d+' | head -1)
        if [ -n "$rocm_ver" ]; then
            echo "$rocm_ver"
            return 0
        fi
    fi
    
    return 1
}

# Function to install PyTorch with ROCm
install_pytorch_rocm() {
    local rocm_ver=$1
    local pytorch_ver=$2
    
    echo ""
    echo "Installing PyTorch $pytorch_ver with ROCm $rocm_ver support..."
    echo ""
    
    # Special handling for ROCm 5.7.1 - use AMD repository wheels
    if [[ "$rocm_ver" == "5.7" ]]; then
        echo "✓ Detected ROCm 5.7.x - using AMD repository wheels for optimal compatibility"
        echo ""
        
        # Check Python version for AMD wheels compatibility
        local python_ver=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [[ "$python_ver" != "3.10" ]]; then
            echo "⚠ Warning: Python $python_ver detected, but AMD ROCm 5.7 wheels are built for Python 3.10"
            echo "   Will attempt to use standard PyTorch installation instead..."
        else
            # Install torch and torchvision from AMD repository
            echo "Installing torch 2.0.1+rocm5.7 and torchvision 0.15.2+rocm5.7 from AMD repository..."
            pip install --ignore-installed \
                https://repo.radeon.com/rocm/manylinux/rocm-rel-5.7/torch-2.0.1%2Brocm5.7-cp310-cp310-linux_x86_64.whl \
                https://repo.radeon.com/rocm/manylinux/rocm-rel-5.7/torchvision-0.15.2%2Brocm5.7-cp310-cp310-linux_x86_64.whl
            
            if [ $? -eq 0 ]; then
                echo "✓ PyTorch and torchvision with ROCm 5.7 installed successfully"
                
                # Install torchaudio separately
                echo "Installing torchaudio 2.0.2..."
                pip install torchaudio==2.0.2
                
                # Force reinstall numpy<2 for compatibility
                echo "Ensuring numpy<2 for compatibility..."
                pip install "numpy<2" --force-reinstall
                
                echo "✓ ROCm 5.7 PyTorch stack installed successfully"
                return 0
            else
                echo "⚠ Warning: Failed to install PyTorch from AMD repository"
                echo "   Falling back to standard installation..."
            fi
        fi
    fi
    
    # Format ROCm version for PyTorch URL (e.g., 5.7 -> rocm5.7)
    local rocm_url_ver="rocm${rocm_ver}"
    
    # Install PyTorch with ROCm support from standard repository
    pip install torch==$pytorch_ver torchvision torchaudio --index-url https://download.pytorch.org/whl/$rocm_url_ver
    
    if [ $? -eq 0 ]; then
        echo "✓ PyTorch with ROCm $rocm_ver installed successfully"
        return 0
    else
        echo "⚠ Warning: Failed to install PyTorch with ROCm $rocm_ver"
        echo "   Trying without specifying exact version..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$rocm_url_ver
        return $?
    fi
}

# Function to install generic PyTorch
install_pytorch_generic() {
    echo ""
    echo "Installing generic PyTorch (CPU/CUDA)..."
    echo ""
    
    # Install requirements which includes torch
    pip install -r "$PROJECT_ROOT/requirements.txt"
    
    if [ $? -eq 0 ]; then
        echo "✓ Generic PyTorch installed successfully"
        return 0
    else
        echo "❌ Failed to install PyTorch"
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --amd)
            USE_AMD=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Main script
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     AROS-Cognito: PyTorch Setup Script                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
echo ""

if ! command_exists python3; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

if ! command_exists pip; then
    echo "❌ Error: pip is not installed"
    echo "   Please install pip"
    exit 1
fi

echo "✓ Python 3: $(python3 --version)"
echo "✓ pip: $(pip --version)"
echo ""

# Install base dependencies (excluding torch if AMD flag is set)
echo "Installing base dependencies..."
if [ "$USE_AMD" = true ]; then
    # Install all dependencies except torch, using --ignore-installed to avoid distutils conflicts
    pip install --ignore-installed flask>=3.0.0 transformers>=4.36.0 pyarrow>=14.0.0 datasets>=2.16.0 peft>=0.7.0 accelerate>=0.25.0 bitsandbytes>=0.41.0 GitPython>=3.1.40 watchdog>=3.0.0 psutil>=5.9.0 colorama>=0.4.6 pyyaml>=6.0 tqdm>=4.66.0
else
    # Just use requirements.txt
    true  # Will be handled below
fi
echo ""

# Install PyTorch based on flag
if [ "$USE_AMD" = true ]; then
    echo "AMD ROCm mode enabled"
    echo ""
    
    # Detect ROCm version
    ROCM_VERSION=$(detect_rocm_version)
    
    if [ -z "$ROCM_VERSION" ]; then
        echo "❌ Error: Could not detect ROCm version"
        echo ""
        echo "Please ensure ROCm is installed on your system."
        echo "You can check with: rocminfo"
        echo ""
        echo "If ROCm is installed in a non-standard location, you may need to:"
        echo "  1. Check /opt/rocm directory exists"
        echo "  2. Source the ROCm environment: source /opt/rocm/bin/setup_vars"
        echo ""
        exit 1
    fi
    
    echo "✓ Detected ROCm version: $ROCM_VERSION"
    echo ""
    
    # Verify ROCm version is supported
    case "$ROCM_VERSION" in
        5.0|5.1|5.2|5.3|5.4|5.5|5.6|5.7|6.0|6.1)
            echo "✓ ROCm $ROCM_VERSION is supported by PyTorch"
            ;;
        *)
            echo "⚠ Warning: ROCm $ROCM_VERSION may not be officially supported"
            echo "   Will attempt installation anyway..."
            ;;
    esac
    
    # Install PyTorch with ROCm
    install_pytorch_rocm "$ROCM_VERSION" "$PYTORCH_VERSION"
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Failed to install PyTorch with ROCm support"
        echo ""
        echo "You may need to:"
        echo "  1. Check that your ROCm installation is complete"
        echo "  2. Visit https://pytorch.org/get-started/locally/ for manual installation"
        echo "  3. Try installing a different PyTorch version compatible with your ROCm"
        echo ""
        exit 1
    fi
else
    # Install generic PyTorch
    install_pytorch_generic
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Failed to install PyTorch"
        exit 1
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 Setup Complete!                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Display PyTorch info
echo "Verifying PyTorch installation..."
python3 << 'PYTHON_CHECK'
try:
    import torch
    print(f"✓ PyTorch version: {torch.__version__}")
    print(f"✓ CUDA available: {torch.cuda.is_available()}")
    if hasattr(torch.version, 'hip'):
        print(f"✓ ROCm/HIP available: True")
        print(f"✓ ROCm version: {torch.version.hip}")
    else:
        print(f"✓ ROCm/HIP available: False")
except Exception as e:
    print(f"⚠ Warning: Could not verify PyTorch: {e}")
PYTHON_CHECK

echo ""
echo "Next steps:"
echo "  1. Run ./scripts/quickstart.sh to complete setup"
echo "  2. Or manually continue with ./scripts/clone_aros.sh"
echo ""
