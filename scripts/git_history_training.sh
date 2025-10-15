#!/bin/bash

# Git Commit History to AI Training Data Converter
# Parses commit history and generates training data for LLaMA codegen models
#
# Pipeline: Git History → Commit Parser → Breadcrumb Generator → Training Data
#
# This script extracts commits, analyzes changes, and generates breadcrumb-annotated
# training examples suitable for fine-tuning code generation models.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 1
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Default options
OUTPUT_DIR="./training_data"
OUTPUT_FORMAT="jsonl"
MAX_COMMITS=1000
MIN_LINES_CHANGED=5
MAX_LINES_CHANGED=500
INCLUDE_DIFFS=true
INCLUDE_BREADCRUMBS=true
BRANCH="HEAD"
SINCE_DATE=""
UNTIL_DATE=""
FILE_PATTERN="*.c *.h"
VERBOSE=false
REPO_PATH=""

print_usage() {
    echo -e "${CYAN}Git Commit History to AI Training Data Converter${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS] [REPO_PATH]"
    echo ""
    echo "Options:"
    echo "  -o, --output DIR         Output directory (default: ./training_data)"
    echo "  -f, --format FORMAT      Output format: jsonl, json, csv (default: jsonl)"
    echo "  -n, --max-commits NUM    Maximum commits to process (default: 1000)"
    echo "  -m, --min-lines NUM      Minimum lines changed per commit (default: 5)"
    echo "  -M, --max-lines NUM      Maximum lines changed per commit (default: 500)"
    echo "  -b, --branch BRANCH      Branch to analyze (default: HEAD)"
    echo "  -s, --since DATE         Include commits since date (YYYY-MM-DD)"
    echo "  -u, --until DATE         Include commits until date (YYYY-MM-DD)"
    echo "  -p, --pattern PATTERN    File pattern to include (default: '*.c *.h')"
    echo "  --no-diffs               Don't include diffs in output"
    echo "  --no-breadcrumbs         Don't extract breadcrumb metadata"
    echo "  -v, --verbose            Verbose output"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Process last 500 commits"
    echo "  $0 -n 500 /path/to/repo"
    echo ""
    echo "  # Process commits from last year"
    echo "  $0 --since 2024-01-01 /path/to/repo"
    echo ""
    echo "  # Focus on kernel code only"
    echo "  $0 -p 'rom/kernel/*.c arch/*/kernel/*.c' /path/to/repo"
    echo ""
    echo "  # Generate CSV format for analysis"
    echo "  $0 -f csv -o ./analysis /path/to/repo"
    echo ""
    echo "Training Data Structure:"
    echo "  - Commit metadata (hash, author, date, message)"
    echo "  - Changed files with diffs"
    echo "  - Extracted breadcrumb annotations"
    echo "  - Before/after code snippets"
    echo "  - Problem-solution pairs"
    echo ""
}

log_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[INFO]${NC} $1" >&2
    fi
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -n|--max-commits)
            MAX_COMMITS="$2"
            shift 2
            ;;
        -m|--min-lines)
            MIN_LINES_CHANGED="$2"
            shift 2
            ;;
        -M|--max-lines)
            MAX_LINES_CHANGED="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -s|--since)
            SINCE_DATE="$2"
            shift 2
            ;;
        -u|--until)
            UNTIL_DATE="$2"
            shift 2
            ;;
        -p|--pattern)
            FILE_PATTERN="$2"
            shift 2
            ;;
        --no-diffs)
            INCLUDE_DIFFS=false
            shift
            ;;
        --no-breadcrumbs)
            INCLUDE_BREADCRUMBS=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            if [ -z "$REPO_PATH" ]; then
                REPO_PATH="$1"
            else
                log_error "Unknown option: $1"
                print_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Use default repo path if not specified
if [ -z "$REPO_PATH" ]; then
    REPO_PATH="$PROJECT_ROOT/aros-src"
fi

# Validate format
if [[ "$OUTPUT_FORMAT" != "jsonl" && "$OUTPUT_FORMAT" != "json" && "$OUTPUT_FORMAT" != "csv" ]]; then
    log_error "Invalid format '$OUTPUT_FORMAT'. Use jsonl, json, or csv."
    exit 1
fi

# Check if repository exists
if [ ! -d "$REPO_PATH" ]; then
    log_error "Repository path does not exist: $REPO_PATH"
    exit 1
fi

if [ ! -d "$REPO_PATH/.git" ]; then
    log_error "Not a git repository: $REPO_PATH"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR" || {
    log_error "Failed to create output directory: $OUTPUT_DIR"
    exit 1
}

log_info "Repository: $REPO_PATH"
log_info "Output directory: $OUTPUT_DIR"
log_info "Output format: $OUTPUT_FORMAT"
log_info "Max commits: $MAX_COMMITS"

# JSON escape function
json_escape() {
    local input="$1"
    # Escape backslashes, quotes, newlines, tabs, etc.
    echo "$input" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/\t/\\t/g' | sed 's/\r/\\r/g'
}

# Extract breadcrumb metadata from file content
extract_breadcrumbs() {
    local content="$1"

    # Check if content has breadcrumbs
    if ! echo "$content" | grep -q "AI_PHASE:" 2>/dev/null; then
        echo "{}"
        return
    fi

    # Extract breadcrumb fields
    local phase=$(echo "$content" | grep "AI_PHASE:" | head -1 | sed 's/.*AI_PHASE:[[:space:]]*//' | tr -d '\r\n')
    local status=$(echo "$content" | grep "AI_STATUS:" | head -1 | sed 's/.*AI_STATUS:[[:space:]]*//' | tr -d '\r\n')
    local pattern=$(echo "$content" | grep "AI_PATTERN:" | head -1 | sed 's/.*AI_PATTERN:[[:space:]]*//' | tr -d '\r\n')
    local strategy=$(echo "$content" | grep "AI_STRATEGY:" | head -1 | sed 's/.*AI_STRATEGY:[[:space:]]*//' | tr -d '\r\n')

    # Build JSON object
    cat <<EOF
{
  "phase": "${phase}",
  "status": "${status}",
  "pattern": "${pattern}",
  "strategy": "${strategy}"
}
EOF
}

# Process commits and generate training data
process_commits() {
    local output_file="$OUTPUT_DIR/training_data.$OUTPUT_FORMAT"
    local temp_log="$OUTPUT_DIR/commits.log"
    
    log_info "Extracting commit history from $REPO_PATH..."
    
    # Build git log command arguments
    local git_args=(
        "--no-pager" "log"
        "--pretty=format:%H|%an|%ae|%ad|%s"
        "--numstat"
    )
    
    if [ -n "$SINCE_DATE" ]; then
        git_args+=("--since=$SINCE_DATE")
    fi
    
    if [ -n "$UNTIL_DATE" ]; then
        git_args+=("--until=$UNTIL_DATE")
    fi
    
    git_args+=("-n" "$MAX_COMMITS" "$BRANCH")
    
    # Execute git log from the repository directory
    (cd "$REPO_PATH" && git "${git_args[@]}") > "$temp_log" 2>&1 || {
        log_error "Failed to extract git log"
        exit 1
    }
    
    log_success "Extracted commit history"
    
    # Process commits based on format
    if [ "$OUTPUT_FORMAT" = "jsonl" ]; then
        process_commits_jsonl "$temp_log" "$output_file"
    elif [ "$OUTPUT_FORMAT" = "json" ]; then
        process_commits_json "$temp_log" "$output_file"
    elif [ "$OUTPUT_FORMAT" = "csv" ]; then
        process_commits_csv "$temp_log" "$output_file"
    fi
    
    rm -f "$temp_log"
}

# Process commits to JSONL format
process_commits_jsonl() {
    local log_file="$1"
    local output_file="$2"
    
    log_info "Processing commits to JSONL format..."
    
    > "$output_file"
    
    local commit_count=0
    local current_hash=""
    local current_author=""
    local current_email=""
    local current_date=""
    local current_message=""
    local files_changed=0
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^[a-f0-9]{40}\| ]]; then
            # New commit line
            if [ -n "$current_hash" ] && [ $files_changed -ge $MIN_LINES_CHANGED ] && [ $files_changed -le $MAX_LINES_CHANGED ]; then
                # Write previous commit
                cat >> "$output_file" <<EOF
{"hash":"$current_hash","author":"$(json_escape "$current_author")","email":"$current_email","date":"$(json_escape "$current_date")","message":"$(json_escape "$current_message")","files_changed":$files_changed}
EOF
                ((commit_count++))
            fi
            
            # Parse new commit
            IFS='|' read -r current_hash current_author current_email current_date current_message <<< "$line"
            files_changed=0
        elif [[ "$line" =~ ^[0-9]+[[:space:]]+[0-9]+[[:space:]] ]]; then
            # Numstat line (additions/deletions/filename)
            ((files_changed++))
        fi
    done < "$log_file"
    
    # Write last commit
    if [ -n "$current_hash" ] && [ $files_changed -ge $MIN_LINES_CHANGED ] && [ $files_changed -le $MAX_LINES_CHANGED ]; then
        cat >> "$output_file" <<EOF
{"hash":"$current_hash","author":"$(json_escape "$current_author")","email":"$current_email","date":"$(json_escape "$current_date")","message":"$(json_escape "$current_message")","files_changed":$files_changed}
EOF
        ((commit_count++))
    fi
    
    log_success "Processed $commit_count commits to $output_file"
}

# Process commits to JSON format
process_commits_json() {
    local log_file="$1"
    local output_file="$2"
    
    log_info "Processing commits to JSON format..."
    
    echo '{"commits":[' > "$output_file"
    
    local commit_count=0
    local current_hash=""
    local current_author=""
    local current_email=""
    local current_date=""
    local current_message=""
    local files_changed=0
    local first_commit=true
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^[a-f0-9]{40}\| ]]; then
            # New commit line
            if [ -n "$current_hash" ] && [ $files_changed -ge $MIN_LINES_CHANGED ] && [ $files_changed -le $MAX_LINES_CHANGED ]; then
                # Write previous commit
                if [ "$first_commit" = false ]; then
                    echo "," >> "$output_file"
                fi
                cat >> "$output_file" <<EOF
{"hash":"$current_hash","author":"$(json_escape "$current_author")","email":"$current_email","date":"$(json_escape "$current_date")","message":"$(json_escape "$current_message")","files_changed":$files_changed}
EOF
                ((commit_count++))
                first_commit=false
            fi
            
            # Parse new commit
            IFS='|' read -r current_hash current_author current_email current_date current_message <<< "$line"
            files_changed=0
        elif [[ "$line" =~ ^[0-9]+[[:space:]]+[0-9]+[[:space:]] ]]; then
            # Numstat line
            ((files_changed++))
        fi
    done < "$log_file"
    
    # Write last commit
    if [ -n "$current_hash" ] && [ $files_changed -ge $MIN_LINES_CHANGED ] && [ $files_changed -le $MAX_LINES_CHANGED ]; then
        if [ "$first_commit" = false ]; then
            echo "," >> "$output_file"
        fi
        cat >> "$output_file" <<EOF
{"hash":"$current_hash","author":"$(json_escape "$current_author")","email":"$current_email","date":"$(json_escape "$current_date")","message":"$(json_escape "$current_message")","files_changed":$files_changed}
EOF
        ((commit_count++))
    fi
    
    echo "]}" >> "$output_file"
    
    log_success "Processed $commit_count commits to $output_file"
}

# Process commits to CSV format
process_commits_csv() {
    local log_file="$1"
    local output_file="$2"
    
    log_info "Processing commits to CSV format..."
    
    echo "hash,author,email,date,message,files_changed" > "$output_file"
    
    local commit_count=0
    local current_hash=""
    local current_author=""
    local current_email=""
    local current_date=""
    local current_message=""
    local files_changed=0
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^[a-f0-9]{40}\| ]]; then
            # New commit line
            if [ -n "$current_hash" ] && [ $files_changed -ge $MIN_LINES_CHANGED ] && [ $files_changed -le $MAX_LINES_CHANGED ]; then
                # Write previous commit (CSV escape quotes by doubling them)
                local csv_message=$(echo "$current_message" | sed 's/"/""/g')
                local csv_author=$(echo "$current_author" | sed 's/"/""/g')
                echo "$current_hash,\"$csv_author\",$current_email,\"$current_date\",\"$csv_message\",$files_changed" >> "$output_file"
                ((commit_count++))
            fi
            
            # Parse new commit
            IFS='|' read -r current_hash current_author current_email current_date current_message <<< "$line"
            files_changed=0
        elif [[ "$line" =~ ^[0-9]+[[:space:]]+[0-9]+[[:space:]] ]]; then
            # Numstat line
            ((files_changed++))
        fi
    done < "$log_file"
    
    # Write last commit
    if [ -n "$current_hash" ] && [ $files_changed -ge $MIN_LINES_CHANGED ] && [ $files_changed -le $MAX_LINES_CHANGED ]; then
        local csv_message=$(echo "$current_message" | sed 's/"/""/g')
        local csv_author=$(echo "$current_author" | sed 's/"/""/g')
        echo "$current_hash,\"$csv_author\",$current_email,\"$current_date\",\"$csv_message\",$files_changed" >> "$output_file"
        ((commit_count++))
    fi
    
    log_success "Processed $commit_count commits to $output_file"
}

# Generate summary statistics
generate_summary() {
    local output_file="$OUTPUT_DIR/training_data.$OUTPUT_FORMAT"
    local summary_file="$OUTPUT_DIR/summary.json"
    
    log_info "Generating summary statistics..."
    
    local commit_count=0
    if [ "$OUTPUT_FORMAT" = "jsonl" ]; then
        commit_count=$(wc -l < "$output_file")
    elif [ "$OUTPUT_FORMAT" = "json" ]; then
        commit_count=$(grep -c '"hash"' "$output_file")
    elif [ "$OUTPUT_FORMAT" = "csv" ]; then
        commit_count=$(($(wc -l < "$output_file") - 1))
    fi
    
    cat > "$summary_file" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "repository": "$REPO_PATH",
  "output_format": "$OUTPUT_FORMAT",
  "total_commits": $commit_count,
  "max_commits_requested": $MAX_COMMITS,
  "min_lines_changed": $MIN_LINES_CHANGED,
  "max_lines_changed": $MAX_LINES_CHANGED,
  "branch": "$BRANCH",
  "since_date": "$SINCE_DATE",
  "until_date": "$UNTIL_DATE",
  "output_file": "$output_file"
}
EOF
    
    log_success "Summary written to $summary_file"
}

# Main execution
log_info "Starting git history training data extraction..."
echo ""

process_commits
generate_summary

echo ""
log_success "Training data extraction complete!"
log_success "Output: $OUTPUT_DIR/training_data.$OUTPUT_FORMAT"
log_success "Summary: $OUTPUT_DIR/summary.json"
