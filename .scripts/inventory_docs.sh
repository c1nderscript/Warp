#!/bin/bash
#
# Documentation Inventory Script for Surrentumlabs (Bash Version)
#
# This lightweight bash script recursively scans /home/cinder/Documents/repos/Surrentumlabs/** 
# for markdown documentation files and generates a JSON cache with metadata.
#
# Author: Created by Agent Mode for Surrentumlabs documentation management
# Purpose: Inventory all documentation files and metadata across Surrentumlabs
# Created: 2024-12-22
#
# Target files:
# - README.md, AGENTS.md, CHANGELOG.md, plan.md, toaster.md
# - docs/README.md, *.md inside docs/ directory
#
# For each file captures:
# - absolute path, repository root, repo name, repo category, 
# - primary language(s), last-modified timestamp (git log -1 --format=%ct FILE)
#
# Outputs to: .scripts/cache/docs_index.json

set -euo pipefail

# Base path to scan
BASE_PATH="/home/cinder/Documents/repos/Surrentumlabs"

# Output file
OUTPUT_DIR=".scripts/cache"
OUTPUT_FILE="$OUTPUT_DIR/docs_index_bash.json"

# Target filenames
TARGET_FILES=("README.md" "AGENTS.md" "CHANGELOG.md" "plan.md" "toaster.md")

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to get git timestamp for a file
get_git_timestamp() {
    local file_path="$1"
    local repo_dir=$(dirname "$file_path")
    
    # Try to get git timestamp
    if cd "$repo_dir" && git log -1 --format=%ct "$file_path" 2>/dev/null; then
        return 0
    else
        # Fallback to file system timestamp
        stat -c %Y "$file_path" 2>/dev/null || echo "0"
    fi
}

# Function to determine repo category based on parent directory
get_repo_category() {
    local repo_path="$1"
    local parent_dir=$(basename "$(dirname "$repo_path")")
    
    case "$parent_dir" in
        "Monorepos")
            echo "Monorepo"
            ;;
        "Rust Component Repos")
            echo "Rust Component"
            ;;
        "Typescript Component Repos")
            echo "TypeScript Component"
            ;;
        "Other"|"whiply_project")
            echo "Other"
            ;;
        *)
            echo "Other"
            ;;
    esac
}

# Function to detect primary languages
detect_languages() {
    local repo_path="$1"
    local languages=()
    
    cd "$repo_path" || return
    
    # Check for language indicators
    if [ -f "Cargo.toml" ] || [ -f "Cargo.lock" ] || [ -d "src" ]; then
        languages+=("Rust")
    fi
    
    if [ -f "package.json" ] || [ -f "tsconfig.json" ]; then
        languages+=("TypeScript")
        languages+=("JavaScript")
    fi
    
    if [ -f "go.mod" ] || [ -f "go.sum" ]; then
        languages+=("Go")
    fi
    
    if [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        languages+=("Python")
    fi
    
    if [ -f "CMakeLists.txt" ] || [ -f "Makefile" ]; then
        languages+=("C++")
    fi
    
    # If no languages found, default to Markdown
    if [ ${#languages[@]} -eq 0 ]; then
        languages=("Markdown")
    fi
    
    # Convert array to JSON format
    printf '%s\n' "${languages[@]}" | jq -R . | jq -s .
}

# Function to find repository root
find_repo_root() {
    local file_path="$1"
    local current_path=$(dirname "$file_path")
    
    while [ "$current_path" != "/" ]; do
        if [ -d "$current_path/.git" ]; then
            echo "$current_path"
            return
        fi
        current_path=$(dirname "$current_path")
    done
    
    # If no .git found, use directory of file
    dirname "$file_path"
}

echo "Starting documentation inventory scan (Bash version)"
echo "Base path: $BASE_PATH"
echo "Target files: ${TARGET_FILES[*]}"
echo "Target docs patterns: docs/README.md, docs/*.md"
echo "-----------------------------------------------------------"

# Check if base path exists
if [ ! -d "$BASE_PATH" ]; then
    echo "ERROR: Base path does not exist: $BASE_PATH"
    exit 1
fi

# Create temporary file for collecting results
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

echo "[]" > "$TEMP_FILE"

total_files=0

# Function to process a file
process_file() {
    local file_path="$1"
    local filename=$(basename "$file_path")
    
    # Check if this is a target file
    local should_include=false
    
    # Check exact filename matches
    for target in "${TARGET_FILES[@]}"; do
        if [ "$filename" = "$target" ]; then
            should_include=true
            break
        fi
    done
    
    # Check docs directory patterns
    if [[ "$file_path" == */docs/* ]] && [[ "$filename" == *.md ]]; then
        should_include=true
    fi
    
    if [ "$should_include" = true ]; then
        echo "Found: $file_path"
        
        local repo_root=$(find_repo_root "$file_path")
        local repo_name=$(basename "$repo_root")
        local repo_category=$(get_repo_category "$repo_root")
        local timestamp=$(get_git_timestamp "$file_path")
        local languages=$(detect_languages "$repo_root")
        local relative_path=$(realpath --relative-to="$repo_root" "$file_path")
        local last_modified_date=""
        
        if [ "$timestamp" != "0" ]; then
            last_modified_date=$(date -d "@$timestamp" --iso-8601=seconds)
        fi
        
        # Create JSON object for this file
        local json_obj=$(jq -n \
            --arg absolute_path "$file_path" \
            --arg repository_root "$repo_root" \
            --arg repo_name "$repo_name" \
            --arg repo_category "$repo_category" \
            --argjson primary_languages "$languages" \
            --arg last_modified_timestamp "$timestamp" \
            --arg last_modified_date "$last_modified_date" \
            --arg filename "$filename" \
            --arg relative_path "$relative_path" \
            '{
                absolute_path: $absolute_path,
                repository_root: $repository_root,
                repo_name: $repo_name,
                repo_category: $repo_category,
                primary_languages: $primary_languages,
                last_modified_timestamp: ($last_modified_timestamp | tonumber),
                last_modified_date: $last_modified_date,
                filename: $filename,
                relative_path: $relative_path
            }')
        
        # Add to results
        jq --argjson new_obj "$json_obj" '. += [$new_obj]' "$TEMP_FILE" > "$TEMP_FILE.tmp" && mv "$TEMP_FILE.tmp" "$TEMP_FILE"
        
        ((total_files++))
    fi
}

# Find and process all markdown files
while IFS= read -r -d '' file; do
    process_file "$file"
done < <(find "$BASE_PATH" -type f -name "*.md" -not -path "*/.git/*" -print0)

# Generate metadata
scan_timestamp=$(date --iso-8601=seconds)
repos_found=$(jq '[.[].repo_name] | unique | length' "$TEMP_FILE")

# Create final output
jq --arg scan_timestamp "$scan_timestamp" \
   --arg base_path "$BASE_PATH" \
   --arg total_files "$total_files" \
   --arg repositories_found "$repos_found" \
   --argjson target_files "$(printf '%s\n' "${TARGET_FILES[@]}" | jq -R . | jq -s .)" \
   '{
     metadata: {
       scan_timestamp: $scan_timestamp,
       base_path: $base_path,
       total_files: ($total_files | tonumber),
       repositories_found: ($repositories_found | tonumber),
       target_files: $target_files,
       docs_patterns: ["docs/README.md", "docs/*.md"]
     },
     documentation_files: .
   }' "$TEMP_FILE" > "$OUTPUT_FILE"

echo "-----------------------------------------------------------"
echo "Scan complete (Bash version)!"
echo "Total files found: $total_files"
echo "Repositories scanned: $repos_found"
echo "Results written to: $OUTPUT_FILE"
