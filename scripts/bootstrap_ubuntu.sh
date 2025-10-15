#!/bin/bash
# Ubuntu 22.04.3 Bootstrap Script for AROS-Cognito AI Development System
# This script provides a complete setup from scratch including:
# - System dependency installation
# - ROCm validation (5.7.1)
# - GitHub token management and repo cloning
# - Database schema initialization
# - UI configuration for network access
# - PyTorch with ROCm support

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/config.json"
TOKEN_FILE="$HOME/.aros_github_token"

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
    print_info "Installing system dependencies..."
    echo ""
    
    # Check if we need sudo
    if [ "$EUID" -ne 0 ]; then
        print_info "This script requires sudo access for system packages"
        SUDO="sudo"
    else
        SUDO=""
    fi
    
    # Update package list
    print_info "Updating package lists..."
    $SUDO apt-get update -qq
    
    # Install essential build tools
    print_info "Installing build essentials..."
    $SUDO apt-get install -y -qq \
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
    print_info "The system will continue with CPU-only PyTorch"
    print_info "To install ROCm 5.7.1, visit: https://rocmdocs.amd.com/"
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

# Function to setup Python virtual environment (optional but recommended)
setup_python_env() {
    print_info "Setting up Python environment..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION detected"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    python3 -m pip install --upgrade pip -q
    
    print_success "Python environment ready"
}

# Function to install PyTorch with ROCm support
install_pytorch() {
    print_info "Installing PyTorch..."
    echo ""
    
    if command_exists rocminfo && [ -n "$ROCM_VERSION" ]; then
        print_info "Installing PyTorch with ROCm $ROCM_VERSION support..."
        bash "$SCRIPT_DIR/setup.sh" --amd
    else
        print_info "Installing generic PyTorch..."
        bash "$SCRIPT_DIR/setup.sh"
    fi
    
    print_success "PyTorch installation complete"
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
    
    # Check Python packages
    print_info "Checking Python packages..."
    python3 -c "import flask; print('  Flask:', flask.__version__)" || print_error "Flask not installed"
    python3 -c "import torch; print('  PyTorch:', torch.__version__)" || print_error "PyTorch not installed"
    
    # Check ROCm/CUDA availability
    python3 << 'PYTHON_CHECK'
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
    
    STARTUP_SCRIPT="$PROJECT_ROOT/start_ui.sh"
    
    cat > "$STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
# Quick start script for AROS-Cognito UI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting AROS-Cognito Monitoring UI..."
echo ""

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "Access the UI at:"
echo "  - Local:   http://localhost:5000"
if [ -n "$LOCAL_IP" ]; then
    echo "  - Network: http://$LOCAL_IP:5000"
fi
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$SCRIPT_DIR/ui"
python3 app.py
EOF
    
    chmod +x "$STARTUP_SCRIPT"
    print_success "Startup script created: ./start_ui.sh"
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
    echo "Next Steps:"
    echo ""
    echo "1. Start the Monitoring UI:"
    echo "   ${GREEN}./start_ui.sh${NC}"
    echo "   or"
    echo "   ${GREEN}cd ui && python3 app.py${NC}"
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
    echo "Documentation:"
    echo "   - Setup Guide:   ${BLUE}cat SETUP.md${NC}"
    echo "   - System Guide:  ${BLUE}cat SYSTEM_OVERVIEW.md${NC}"
    echo "   - Quick Ref:     ${BLUE}cat QUICKREF_SYNC.md${NC}"
    echo ""
}

# Main execution flow
main() {
    check_ubuntu_version
    install_system_dependencies
    check_rocm
    get_github_token
    clone_repositories
    setup_python_env
    install_pytorch
    initialize_database
    configure_ui_network
    verify_installation
    create_startup_script
    display_summary
}

# Run main function
main
