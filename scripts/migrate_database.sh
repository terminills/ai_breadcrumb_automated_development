#!/bin/bash
# Database Schema Migration Script
# Ensures database schema is always up to date
# Run this on every startup to apply any schema changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_ROOT/logs"

# Schema version tracking
SCHEMA_VERSION_FILE="$LOGS_DIR/.schema_version"
CURRENT_SCHEMA_VERSION=1

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Get current schema version
get_schema_version() {
    if [ -f "$SCHEMA_VERSION_FILE" ]; then
        cat "$SCHEMA_VERSION_FILE"
    else
        echo "0"
    fi
}

# Set schema version
set_schema_version() {
    echo "$1" > "$SCHEMA_VERSION_FILE"
}

# Initialize base schema (v1)
initialize_v1_schema() {
    print_info "Initializing database schema v1..."
    
    # Create directory structure
    mkdir -p "$LOGS_DIR/"{training,compile,errors,agent,reasoning,build}
    mkdir -p "$PROJECT_ROOT/models"
    
    # Initialize error database
    ERROR_DB="$LOGS_DIR/errors/error_database.json"
    if [ ! -f "$ERROR_DB" ]; then
        cat > "$ERROR_DB" << 'EOF'
{
  "schema_version": 1,
  "errors": {}
}
EOF
        print_success "Error database initialized"
    fi
    
    # Initialize reasoning database
    REASONING_DB="$LOGS_DIR/reasoning/reasoning_database.json"
    if [ ! -f "$REASONING_DB" ]; then
        cat > "$REASONING_DB" << 'EOF'
{
  "schema_version": 1,
  "current": null,
  "history": [],
  "statistics": {
    "total_reasoning_sessions": 0,
    "successful_iterations": 0,
    "failed_iterations": 0,
    "average_iterations_per_task": 0,
    "patterns": {},
    "breadcrumb_usage": {}
  }
}
EOF
        print_success "Reasoning database initialized"
    fi
    
    # Initialize training state
    TRAINING_STATE="$LOGS_DIR/training/training_state.json"
    if [ ! -f "$TRAINING_STATE" ]; then
        cat > "$TRAINING_STATE" << 'EOF'
{
  "schema_version": 1,
  "status": "not_started",
  "current_epoch": 0,
  "total_epochs": 0,
  "last_checkpoint": null,
  "training_history": []
}
EOF
        print_success "Training state initialized"
    fi
    
    # Initialize compilation state
    COMPILE_STATE="$LOGS_DIR/compile/compile_state.json"
    if [ ! -f "$COMPILE_STATE" ]; then
        cat > "$COMPILE_STATE" << 'EOF'
{
  "schema_version": 1,
  "total_compilations": 0,
  "successful_compilations": 0,
  "failed_compilations": 0,
  "last_compilation": null,
  "compilation_history": []
}
EOF
        print_success "Compilation state initialized"
    fi
    
    print_success "Schema v1 initialized"
}

# Migrate schema if needed
migrate_schema() {
    current_version=$(get_schema_version)
    
    print_info "Current schema version: $current_version"
    print_info "Target schema version: $CURRENT_SCHEMA_VERSION"
    
    if [ "$current_version" -eq "$CURRENT_SCHEMA_VERSION" ]; then
        print_success "Schema is up to date"
        return 0
    fi
    
    print_info "Migrating schema from v$current_version to v$CURRENT_SCHEMA_VERSION..."
    
    # Apply migrations
    if [ "$current_version" -lt 1 ]; then
        initialize_v1_schema
    fi
    
    # Add future migrations here
    # if [ "$current_version" -lt 2 ]; then
    #     migrate_v1_to_v2
    # fi
    
    # Update version
    set_schema_version "$CURRENT_SCHEMA_VERSION"
    print_success "Schema migration complete"
}

# Verify database integrity
verify_databases() {
    print_info "Verifying database integrity..."
    
    local all_ok=true
    
    # Check error database
    ERROR_DB="$LOGS_DIR/errors/error_database.json"
    if [ -f "$ERROR_DB" ]; then
        if python3 -c "import json; json.load(open('$ERROR_DB'))" 2>/dev/null; then
            print_success "Error database: OK"
        else
            print_warning "Error database: Invalid JSON, reinitializing..."
            rm "$ERROR_DB"
            initialize_v1_schema
            all_ok=false
        fi
    else
        print_warning "Error database: Missing, creating..."
        initialize_v1_schema
        all_ok=false
    fi
    
    # Check reasoning database
    REASONING_DB="$LOGS_DIR/reasoning/reasoning_database.json"
    if [ -f "$REASONING_DB" ]; then
        if python3 -c "import json; json.load(open('$REASONING_DB'))" 2>/dev/null; then
            print_success "Reasoning database: OK"
        else
            print_warning "Reasoning database: Invalid JSON, reinitializing..."
            rm "$REASONING_DB"
            initialize_v1_schema
            all_ok=false
        fi
    else
        print_warning "Reasoning database: Missing, creating..."
        initialize_v1_schema
        all_ok=false
    fi
    
    if [ "$all_ok" = true ]; then
        print_success "All databases verified"
    fi
}

# Backup databases before migration
backup_databases() {
    print_info "Creating database backup..."
    
    BACKUP_DIR="$LOGS_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup error database
    if [ -f "$LOGS_DIR/errors/error_database.json" ]; then
        cp "$LOGS_DIR/errors/error_database.json" "$BACKUP_DIR/"
    fi
    
    # Backup reasoning database
    if [ -f "$LOGS_DIR/reasoning/reasoning_database.json" ]; then
        cp "$LOGS_DIR/reasoning/reasoning_database.json" "$BACKUP_DIR/"
    fi
    
    print_success "Backup created at: $BACKUP_DIR"
}

# Main execution
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         Database Schema Migration                          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Create backup if databases exist
    if [ -f "$LOGS_DIR/errors/error_database.json" ] || [ -f "$LOGS_DIR/reasoning/reasoning_database.json" ]; then
        backup_databases
    fi
    
    # Run migration
    migrate_schema
    
    # Verify integrity
    verify_databases
    
    echo ""
    print_success "Database schema is ready"
    echo ""
}

main
