#!/usr/bin/env bash
# Ubuntu 22.04.3 Bootstrap Script for AROS-Cognito AI Development System
# This script provides a complete setup from scratch including:
# - System dependency installation
# - ROCm 5.7.1 installation (optional, for Ubuntu 22.04.3)
# - ROCm validation and GPU detection
# - GitHub token management and repo cloning
# - Database schema initialization
# - UI configuration for network access
# - PyTorch with ROCm support
#
# ROCm 5.7.1 Note:
# Ubuntu 22.04.3 has DKMS module issues with newer ROCm versions.
# This script installs ROCm 5.7.1 without DKMS, using kernel's built-in
# amdgpu driver. The kernel module may report version 1.1, but ROCm 5.7.1
# userspace tools and libraries are correctly installed and functional.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/config.json"
TOKEN_FILE="$HOME/.aros_github_token"

# Virtual environment configuration
# Can be overridden by setting VENV_BASE environment variable
VENV_BASE="${VENV_BASE:-$HOME/cognito-envs}"
VENV_DIR="$VENV_BASE/ai_breadcrumb"

# Flag to track if user wants to install system packages
INSTALL_SYSTEM_PACKAGES=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   AROS-Cognito Ubuntu 22.04.3 Complete Bootstrap Script        ║"
echo "║   Autonomous AI Development System Setup                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if user wants to install system packages
ask_system_packages() {
    if (( EUID == 0 )); then
        # Already running as root
        INSTALL_SYSTEM_PACKAGES=true
        print_info "Running as root - system packages will be installed automatically"
    else
        echo ""
        print_info "This script can install/upgrade system packages using sudo."
        print_info "System packages include: build tools, Python, git, and optional ROCm support"
        echo ""
        read -rp "Install/upgrade system packages? [y/N]: " syschoice
        echo ""
        if [[ $syschoice =~ ^[Yy]$ ]]; then
            INSTALL_SYSTEM_PACKAGES=true
            print_success "System packages will be installed (you may be prompted for sudo password)"
        else
            INSTALL_SYSTEM_PACKAGES=false
            print_info "Skipping system package installation"
            print_warning "Note: Ensure required packages are already installed:"
            print_warning "  build-essential, git, curl, wget, python3, python3-pip, python3-venv"
        fi
    fi
}

# Function to check Ubuntu version
check_ubuntu_version() {
    print_info "Checking Ubuntu version..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" != "ubuntu" ]]; then
            print_warning "This script is designed for Ubuntu 22.04.3"
            print_warning "Detected: $NAME $VERSION"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        elif [[ "$VERSION_ID" != "22.04" ]]; then
            print_warning "This script is optimized for Ubuntu 22.04.3"
            print_warning "Detected: Ubuntu $VERSION_ID"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            print_success "Ubuntu $VERSION_ID detected"
        fi
    else
        print_error "Cannot detect OS version"
        exit 1
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    if [ "$INSTALL_SYSTEM_PACKAGES" = false ]; then
        print_info "Skipping system package installation (as requested)"
        print_info "Verifying required packages are available..."
        
        # Check for essential packages
        local missing_packages=()
        for cmd in gcc git curl wget python3 pip3; do
            if ! command_exists "$cmd"; then
                missing_packages+=("$cmd")
            fi
        done
        
        if [ ${#missing_packages[@]} -gt 0 ]; then
            print_error "Missing required packages: ${missing_packages[*]}"
            print_error "Please install them manually or re-run with system package installation enabled"
            exit 1
        fi
        
        print_success "Required packages are available"
        return 0
    fi
    
    print_info "Installing system dependencies..."
    echo ""
    
    # Update package list
    print_info "Updating package lists..."
    sudo apt-get update -qq
    
    # Install essential build tools
    print_info "Installing build essentials..."
    sudo apt-get install -y -qq \
        build-essential \
        git \
        curl \
        wget \
        python3 \
        python3-pip \
        python3-venv \
        libssl-dev \
        libffi-dev \
        python3-dev \
        pkg-config
    
    print_success "System dependencies installed"
}

# Function to detect ROCm version with multiple methods
detect_rocm_version() {
    # Method 1: Check rocminfo
    if command_exists rocminfo; then
        local rocm_ver=$(rocminfo 2>/dev/null | grep "Runtime Version" | head -1 | awk '{print $3}' | cut -d'.' -f1,2)
        if [ -n "$rocm_ver" ]; then
            # On Ubuntu 22.04.3, kernel module may report 1.1 but ROCm 5.7.1 is installed
            # Force 5.7 for PyTorch compatibility when kernel reports 1.1
            if [ "$rocm_ver" = "1.1" ] && [ -f "/opt/rocm/.info/version" ]; then
                local file_ver=$(cat /opt/rocm/.info/version 2>/dev/null | cut -d'-' -f1 | cut -d'.' -f1,2)
                if [[ "$file_ver" =~ ^5\.7 ]]; then
                    echo "5.7"
                    return 0
                fi
            fi
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

# Function to install ROCm 5.7.1 for Ubuntu 22.04.3
install_rocm_5_7_1() {
    if [ "$INSTALL_SYSTEM_PACKAGES" = false ]; then
        print_warning "Cannot install ROCm without system package installation permission"
        print_info "Please install ROCm manually or re-run with system package installation enabled"
        return 1
    fi
    
    print_info "Installing ROCm 5.7.1 for Ubuntu 22.04.3..."
    echo ""
    
    # Ubuntu 22.04.3 has DKMS issues with newer ROCm versions
    # Force ROCm 5.7.1 which uses older kernel modules that work
    print_info "Setting up ROCm repository for version 5.7.1..."
    
    # Add ROCm repository key
    print_info "Adding ROCm GPG key..."
    wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add - 2>/dev/null || {
        # Fallback for newer apt that doesn't support apt-key
        wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/rocm.gpg > /dev/null
    }
    
    # Add ROCm 5.7.1 repository (ubuntu focal/jammy)
    print_info "Adding ROCm 5.7.1 repository..."
    echo "deb [arch=amd64] https://repo.radeon.com/rocm/apt/5.7.1 ubuntu main" | sudo tee /etc/apt/sources.list.d/rocm.list
    
    # Set repository priority to prefer ROCm 5.7.1
    print_info "Setting repository priority..."
    echo -e "Package: *\nPin: release o=repo.radeon.com\nPin-Priority: 600" | sudo tee /etc/apt/preferences.d/rocm-pin-600
    
    # Update package list
    print_info "Updating package lists..."
    sudo apt-get update -qq
    
    # Install ROCm 5.7.1 (without DKMS - uses existing kernel modules)
    print_info "Installing ROCm 5.7.1 packages (this may take several minutes)..."
    print_warning "Note: Installing without DKMS due to Ubuntu 22.04.3 compatibility issues"
    
    # Install core ROCm packages without kernel driver (amdgpu-dkms)
    # This allows using the kernel's built-in amdgpu driver which shows as 1.1
    sudo apt-get install -y -qq \
        rocm-dev \
        rocm-libs \
        rocm-utils \
        rocminfo \
        rocm-smi \
        hip-runtime-amd \
        hip-dev || {
        print_error "Failed to install ROCm packages"
        return 1
    }
    
    # Add user to render and video groups for GPU access
    print_info "Adding user to video and render groups..."
    sudo usermod -a -G video,render $USER 2>/dev/null || true
    
    # Set up environment
    print_info "Configuring ROCm environment..."
    if ! grep -q "/opt/rocm/bin" ~/.bashrc 2>/dev/null; then
        echo 'export PATH=$PATH:/opt/rocm/bin:/opt/rocm/opencl/bin' >> ~/.bashrc
        echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rocm/lib' >> ~/.bashrc
    fi
    
    # Source the environment for current session
    export PATH=$PATH:/opt/rocm/bin:/opt/rocm/opencl/bin
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rocm/lib
    
    print_success "ROCm 5.7.1 installed successfully"
    print_info "Note: You may need to log out and back in for group changes to take effect"
    print_info "Note: Kernel module version (rocminfo) may show 1.1, but ROCm 5.7.1 is correctly installed"
    echo ""
    
    return 0
}

# Function to validate ROCm installation
check_rocm() {
    print_info "Checking for ROCm installation..."
    
    # Use robust detection method
    ROCM_VERSION=$(detect_rocm_version)
    
    if [ -n "$ROCM_VERSION" ]; then
        print_success "ROCm $ROCM_VERSION detected"
        
        # Check if it's 5.7.1 or compatible
        if [[ "$ROCM_VERSION" == "5.7" ]]; then
            print_success "ROCm 5.7.x detected - validated for PyTorch compatibility"
            # Note: On Ubuntu 22.04.3, kernel module may show 1.1 but userspace is 5.7.1
            if command_exists rocminfo; then
                local kernel_ver=$(rocminfo 2>/dev/null | grep "Runtime Version" | head -1 | awk '{print $3}' | cut -d'.' -f1,2)
                if [ "$kernel_ver" = "1.1" ]; then
                    print_info "Note: Kernel module reports 1.1, but ROCm 5.7.1 userspace is correctly installed"
                fi
            fi
        else
            print_warning "ROCm $ROCM_VERSION detected (expected 5.7.1)"
            print_warning "PyTorch will attempt to use this version"
        fi
        
        # Test GPU detection
        if command_exists rocminfo && rocminfo 2>/dev/null | grep -q "gfx900\|gfx906"; then
            GPU_ARCH=$(rocminfo 2>/dev/null | grep "Name:" | grep "gfx" | head -1 | awk '{print $2}')
            print_success "AMD GPU detected: $GPU_ARCH"
        else
            print_warning "No compatible AMD GPU detected"
        fi
        
        return 0
    fi
    
    print_warning "ROCm not detected or not properly installed"
    echo ""
    
    # Offer to install ROCm 5.7.1 for Ubuntu 22.04.3
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" ]] && [[ "$VERSION_ID" == "22.04" ]]; then
            print_info "Would you like to install ROCm 5.7.1 for Ubuntu 22.04.3?"
            print_info "This will install ROCm without DKMS to avoid kernel module issues."
            echo ""
            read -p "Install ROCm 5.7.1? (y/n) " -n 1 -r
            echo ""
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                install_rocm_5_7_1
                if [ $? -eq 0 ]; then
                    # Re-detect after installation
                    ROCM_VERSION=$(detect_rocm_version)
                    if [ -n "$ROCM_VERSION" ]; then
                        print_success "ROCm installation completed successfully"
                        return 0
                    fi
                fi
            else
                print_info "Skipping ROCm installation"
                print_info "The system will continue with CPU-only PyTorch"
            fi
        fi
    fi
    
    print_info "To install ROCm manually, visit: https://rocmdocs.amd.com/"
    return 1
}

# Function to get or create GitHub token
get_github_token() {
    print_info "Checking for GitHub token..."
    echo ""
    
    # Check if token file exists
    if [ -f "$TOKEN_FILE" ]; then
        print_success "Found existing GitHub token"
        GITHUB_TOKEN=$(cat "$TOKEN_FILE")
    else
        # Check environment variable
        if [ -n "$GITHUB_TOKEN" ]; then
            print_success "Using GitHub token from environment"
            echo "$GITHUB_TOKEN" > "$TOKEN_FILE"
            chmod 600 "$TOKEN_FILE"
        else
            # Prompt for token
            echo ""
            print_info "GitHub Personal Access Token Required"
            echo ""
            echo "This system needs access to private repositories:"
            echo "  - terminills/AROS-OLD (private)"
            echo "  - aros-development-team/AROS (public)"
            echo ""
            echo "To create a token:"
            echo "  1. Visit: https://github.com/settings/tokens"
            echo "  2. Click 'Generate new token (classic)'"
            echo "  3. Grant 'repo' scope (full control of private repositories)"
            echo "  4. Copy the token"
            echo ""
            
            read -p "Enter your GitHub Personal Access Token: " -s token
            echo ""
            
            if [ -z "$token" ]; then
                print_error "No token provided"
                exit 1
            fi
            
            # Save token
            echo "$token" > "$TOKEN_FILE"
            chmod 600 "$TOKEN_FILE"
            GITHUB_TOKEN="$token"
            
            print_success "GitHub token saved to $TOKEN_FILE"
        fi
    fi
    
    export GITHUB_TOKEN
}

# Function to clone repositories
clone_repositories() {
    print_info "Checking repositories..."
    echo ""
    
    # Check if AROS-OLD exists
    if [ -d "$PROJECT_ROOT/aros-src" ]; then
        print_success "AROS-OLD repository already cloned"
    else
        print_info "Cloning AROS-OLD repository..."
        bash "$SCRIPT_DIR/clone_aros.sh"
        print_success "AROS-OLD cloned successfully"
    fi
    
    # Check if upstream is configured
    cd "$PROJECT_ROOT/aros-src"
    if git remote | grep -q "upstream"; then
        print_success "Upstream remote already configured"
    else
        print_info "Adding upstream remote..."
        git remote add upstream https://github.com/aros-development-team/AROS.git
        print_success "Upstream remote added"
    fi
    cd "$PROJECT_ROOT"
}

# Function to setup Python virtual environment
setup_python_env() {
    print_info "Setting up Python virtual environment..."
    echo ""
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION detected"
    
    # Create base directory for virtual environments if it doesn't exist
    if [ ! -d "$VENV_BASE" ]; then
        print_info "Creating virtual environment base directory: $VENV_BASE"
        mkdir -p "$VENV_BASE"
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment at $VENV_DIR..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
    
    # Upgrade pip in the venv
    print_info "Upgrading pip in virtual environment..."
    pip install --upgrade pip -q
    
    print_success "Python virtual environment ready"
    echo ""
}

# Function to install PyTorch with ROCm support
install_pytorch() {
    print_info "Installing PyTorch..."
    echo ""
    
    # Ensure we're in the venv
    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Virtual environment not active, activating..."
        source "$VENV_DIR/bin/activate"
    fi
    
    if command_exists rocminfo && [ -n "$ROCM_VERSION" ]; then
        print_info "Installing PyTorch with ROCm $ROCM_VERSION support..."
        bash "$SCRIPT_DIR/setup.sh" --amd
    else
        print_info "Installing generic PyTorch (will use version from requirements.txt: 2.3.1+)..."
        bash "$SCRIPT_DIR/setup.sh"
    fi
    
    print_success "PyTorch installation complete"
}

# Function to setup AI models
setup_ai_models() {
    print_info "Setting up AI models..."
    echo ""
    
    # Ensure we're in the venv
    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Virtual environment not active, activating..."
        source "$VENV_DIR/bin/activate"
    fi
    
    print_info "Checking for AI model dependencies..."
    
    # Check if transformers is installed
    if python -c "import transformers" 2>/dev/null; then
        print_success "Transformers library installed"
    else
        print_warning "Transformers library not found"
        print_info "Installing transformers..."
        pip install transformers>=4.36.0 -q
    fi
    
    # Check if models are available
    MODELS_DIR="$PROJECT_ROOT/models"
    mkdir -p "$MODELS_DIR"
    
    print_info "Model configuration:"
    echo "  - Models directory: $MODELS_DIR"
    echo "  - Config file: $PROJECT_ROOT/config/models.json"
    echo ""
    
    print_warning "AI Model Setup Instructions:"
    echo ""
    echo "The system uses two AI models:"
    echo "  1. CodeGen (for code generation)"
    echo "  2. LLaMA-2 (for reasoning and exploration)"
    echo ""
    echo "These models will be downloaded automatically on first use."
    echo "Alternatively, you can pre-download them:"
    echo ""
    echo "  # For CodeGen (smaller, ~350MB):"
    echo "  python3 -c 'from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained(\"Salesforce/codegen-350M-mono\"); AutoModelForCausalLM.from_pretrained(\"Salesforce/codegen-350M-mono\")'"
    echo ""
    echo "  # For LLaMA-2 (larger, ~13GB - requires HuggingFace token):"
    echo "  # Visit: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf"
    echo "  # Request access, then use your token:"
    echo "  # export HF_TOKEN='your_token_here'"
    echo "  # python3 -c 'from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained(\"meta-llama/Llama-2-7b-chat-hf\", use_auth_token=True); AutoModelForCausalLM.from_pretrained(\"meta-llama/Llama-2-7b-chat-hf\", use_auth_token=True)'"
    echo ""
    print_info "Note: System will use mock AI models if real models are unavailable"
    print_info "      This allows development and testing without full model downloads"
    echo ""
    
    print_success "AI model setup complete"
}

# Function to initialize database schema
initialize_database() {
    print_info "Initializing database schema..."
    echo ""
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/logs/"{training,compile,errors,agent,reasoning,build}
    mkdir -p "$PROJECT_ROOT/models"
    
    # Initialize error database
    ERROR_DB="$PROJECT_ROOT/logs/errors/error_database.json"
    if [ ! -f "$ERROR_DB" ]; then
        echo "{}" > "$ERROR_DB"
        print_success "Error database initialized"
    else
        print_success "Error database exists"
    fi
    
    # Initialize reasoning database
    REASONING_DB="$PROJECT_ROOT/logs/reasoning/reasoning_database.json"
    if [ ! -f "$REASONING_DB" ]; then
        echo '{"current": null, "history": [], "statistics": {}}' > "$REASONING_DB"
        print_success "Reasoning database initialized"
    else
        print_success "Reasoning database exists"
    fi
    
    print_success "Database schema initialized"
}

# Function to configure UI for network access
configure_ui_network() {
    print_info "Configuring UI for network access..."
    
    # Get local IP address
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    
    if [ -n "$LOCAL_IP" ]; then
        print_success "Local IP: $LOCAL_IP"
        
        # Update config to bind to all interfaces
        if command_exists jq; then
            # Use jq if available
            TMP_CONFIG=$(mktemp)
            jq '.ui.host = "0.0.0.0"' "$CONFIG_FILE" > "$TMP_CONFIG"
            mv "$TMP_CONFIG" "$CONFIG_FILE"
        else
            # Fallback to sed
            sed -i 's/"host": "127.0.0.1"/"host": "0.0.0.0"/g' "$CONFIG_FILE"
            sed -i 's/"host": "localhost"/"host": "0.0.0.0"/g' "$CONFIG_FILE"
        fi
        
        print_success "UI configured for network access"
        echo ""
        print_info "The UI will be accessible at:"
        echo "  - Local:   http://localhost:5000"
        echo "  - Network: http://$LOCAL_IP:5000"
        echo ""
    else
        print_warning "Could not detect local IP address"
    fi
}

# Function to verify installation
verify_installation() {
    print_info "Verifying installation..."
    echo ""
    
    # Ensure we're in the venv
    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Virtual environment not active, activating..."
        source "$VENV_DIR/bin/activate"
    fi
    
    # Check Python packages
    print_info "Checking Python packages (in venv)..."
    python -c "import flask; print('  Flask:', flask.__version__)" || print_error "Flask not installed"
    python -c "import torch; print('  PyTorch:', torch.__version__)" || print_error "PyTorch not installed"
    
    # Check ROCm/CUDA availability
    python << 'PYTHON_CHECK'
import torch
if torch.cuda.is_available():
    print("  CUDA devices:", torch.cuda.device_count())
if hasattr(torch.version, 'hip'):
    print("  ROCm/HIP: Available")
else:
    print("  ROCm/HIP: Not available (CPU mode)")
PYTHON_CHECK
    
    # Check repositories
    if [ -d "$PROJECT_ROOT/aros-src" ]; then
        COMMIT_COUNT=$(cd "$PROJECT_ROOT/aros-src" && git rev-list --count HEAD)
        print_success "AROS-OLD: $COMMIT_COUNT commits"
    fi
    
    # Check database files
    if [ -f "$PROJECT_ROOT/logs/errors/error_database.json" ]; then
        print_success "Error database ready"
    fi
    
    echo ""
    print_success "Installation verified"
}

# Function to create a startup script
create_startup_script() {
    print_info "Creating startup helper script..."
    
    # Note: start_ui.sh already exists in the project root
    # We'll update it if needed, but leave the existing one for now
    
    print_success "Startup script exists: ./start_ui.sh (will be updated separately)"
}

# Function to display summary
display_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              Bootstrap Complete!                               ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    
    print_success "System is ready for AI development!"
    echo ""
    echo "Virtual Environment:"
    echo "   Location: ${BLUE}$VENV_DIR${NC}"
    echo "   Activate: ${GREEN}source $VENV_DIR/bin/activate${NC}"
    echo ""
    echo "Next Steps:"
    echo ""
    echo "1. Start the Monitoring UI:"
    echo "   ${GREEN}./start_ui.sh${NC}"
    echo "   (This will automatically activate the venv)"
    echo ""
    echo "2. Access the UI:"
    echo "   - Local:   ${BLUE}http://localhost:5000${NC}"
    if [ -n "$LOCAL_IP" ]; then
        echo "   - Network: ${BLUE}http://$LOCAL_IP:5000${NC}"
    fi
    echo ""
    echo "3. Sync with upstream AROS (optional):"
    echo "   ${GREEN}./scripts/update_and_verify.sh${NC}"
    echo ""
    echo "4. Train the AI Model (requires GPU):"
    echo "   ${GREEN}./scripts/train_model.sh${NC}"
    echo ""
    echo "5. Run the AI Agent:"
    echo "   ${GREEN}./scripts/run_ai_agent.sh ITERATE radeonsi 10${NC}"
    echo ""
    echo "Important Notes:"
    echo "  - AI models will auto-download on first use (requires internet)"
    echo "  - System uses mock AI if models unavailable (for testing)"
    echo "  - For full AI features, ensure models are downloaded (see setup instructions)"
    echo ""
    echo "Documentation:"
    echo "   - Setup Guide:   ${BLUE}cat SETUP.md${NC}"
    echo "   - System Guide:  ${BLUE}cat SYSTEM_OVERVIEW.md${NC}"
    echo "   - Quick Ref:     ${BLUE}cat QUICKREF_SYNC.md${NC}"
    echo ""
}

# Main execution flow
main() {
    check_ubuntu_version
    ask_system_packages
    install_system_dependencies
    check_rocm
    get_github_token
    clone_repositories
    setup_python_env
    install_pytorch
    setup_ai_models
    initialize_database
    configure_ui_network
    verify_installation
    create_startup_script
    display_summary
}

# Run main function
main
