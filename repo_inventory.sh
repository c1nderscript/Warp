#!/bin/bash

# Repository Inventory Shell Script
# Alternative implementation using shell commands

set -euo pipefail

RUST_BASE="/home/cinder/Documents/repos/Surrentumlabs/Rust Component Repos"
TS_BASE="/home/cinder/Documents/repos/Surrentumlabs/Typescript Component Repos"
OUTPUT_JSON="/tmp/repo_inventory_shell.json"
OUTPUT_YAML="/tmp/repo_inventory_shell.yaml"

echo "=== Repository Inventory (Shell Script Version) ==="
echo "Timestamp: $(date -Iseconds)"

# Initialize JSON structure
cat > "$OUTPUT_JSON" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "tool": "shell_script",
  "rust_repos": [
EOF

# Process Rust repositories
echo "Processing Rust repositories..."
rust_count=0
first_rust=true

for repo_dir in "$RUST_BASE"/*; do
    if [[ -d "$repo_dir" ]]; then
        repo_name=$(basename "$repo_dir")
        echo "  Processing Rust repo: $repo_name"
        
        # Add comma for non-first entries
        if [[ "$first_rust" != true ]]; then
            echo "    ," >> "$OUTPUT_JSON"
        fi
        first_rust=false
        
        echo "    {" >> "$OUTPUT_JSON"
        echo "      \"name\": \"$repo_name\"," >> "$OUTPUT_JSON"
        echo "      \"repo_type\": \"rust\"," >> "$OUTPUT_JSON"
        echo "      \"path\": \"$repo_dir\"," >> "$OUTPUT_JSON"
        
        cargo_toml="$repo_dir/Cargo.toml"
        if [[ -f "$cargo_toml" ]]; then
            # Parse Cargo.toml using toml_get or basic parsing
            if command -v toml_get &> /dev/null; then
                package_name=$(toml_get "$cargo_toml" package.name 2>/dev/null || echo "null")
                version=$(toml_get "$cargo_toml" package.version 2>/dev/null || echo "null")
                edition=$(toml_get "$cargo_toml" package.edition 2>/dev/null || echo "null")
            else
                # Basic grep-based parsing
                package_name=$(grep '^name = ' "$cargo_toml" | sed 's/name = "\(.*\)"/\1/' 2>/dev/null || echo "null")
                version=$(grep '^version = ' "$cargo_toml" | sed 's/version = "\(.*\)"/\1/' 2>/dev/null || echo "null")
                edition=$(grep '^edition = ' "$cargo_toml" | sed 's/edition = "\(.*\)"/\1/' 2>/dev/null || echo "null")
            fi
            
            echo "      \"package_name\": \"$package_name\"," >> "$OUTPUT_JSON"
            echo "      \"version\": \"$version\"," >> "$OUTPUT_JSON"
            echo "      \"edition\": \"$edition\"," >> "$OUTPUT_JSON"
            echo "      \"parse_error\": null" >> "$OUTPUT_JSON"
        else
            echo "      \"package_name\": null," >> "$OUTPUT_JSON"
            echo "      \"version\": null," >> "$OUTPUT_JSON"
            echo "      \"edition\": null," >> "$OUTPUT_JSON"
            echo "      \"parse_error\": \"Cargo.toml not found\"" >> "$OUTPUT_JSON"
        fi
        
        echo "    }" >> "$OUTPUT_JSON"
        ((rust_count++))
    fi
done

echo "  ]," >> "$OUTPUT_JSON"
echo "  \"typescript_repos\": [" >> "$OUTPUT_JSON"

# Process TypeScript repositories
echo "Processing TypeScript repositories..."
ts_count=0
first_ts=true

for repo_dir in "$TS_BASE"/*; do
    if [[ -d "$repo_dir" ]]; then
        repo_name=$(basename "$repo_dir")
        echo "  Processing TypeScript repo: $repo_name"
        
        # Add comma for non-first entries
        if [[ "$first_ts" != true ]]; then
            echo "    ," >> "$OUTPUT_JSON"
        fi
        first_ts=false
        
        echo "    {" >> "$OUTPUT_JSON"
        echo "      \"name\": \"$repo_name\"," >> "$OUTPUT_JSON"
        echo "      \"repo_type\": \"typescript\"," >> "$OUTPUT_JSON"
        echo "      \"path\": \"$repo_dir\"," >> "$OUTPUT_JSON"
        
        package_json="$repo_dir/package.json"
        if [[ -f "$package_json" ]]; then
            # Parse package.json using jq if available
            if command -v jq &> /dev/null; then
                package_name=$(jq -r '.name // "null"' "$package_json" 2>/dev/null || echo "null")
                version=$(jq -r '.version // "null"' "$package_json" 2>/dev/null || echo "null")
                
                echo "      \"package_name\": \"$package_name\"," >> "$OUTPUT_JSON"
                echo "      \"version\": \"$version\"," >> "$OUTPUT_JSON"
                echo "      \"parse_error\": null" >> "$OUTPUT_JSON"
            else
                # Basic grep-based parsing
                package_name=$(grep '"name":' "$package_json" | head -1 | sed 's/.*"name": *"\([^"]*\)".*/\1/' 2>/dev/null || echo "null")
                version=$(grep '"version":' "$package_json" | head -1 | sed 's/.*"version": *"\([^"]*\)".*/\1/' 2>/dev/null || echo "null")
                
                echo "      \"package_name\": \"$package_name\"," >> "$OUTPUT_JSON"
                echo "      \"version\": \"$version\"," >> "$OUTPUT_JSON"
                echo "      \"parse_error\": null" >> "$OUTPUT_JSON"
            fi
        else
            echo "      \"package_name\": null," >> "$OUTPUT_JSON"
            echo "      \"version\": null," >> "$OUTPUT_JSON"
            echo "      \"parse_error\": \"package.json not found\"" >> "$OUTPUT_JSON"
        fi
        
        echo "    }" >> "$OUTPUT_JSON"
        ((ts_count++))
    fi
done

# Close JSON structure
echo "  ]," >> "$OUTPUT_JSON"
echo "  \"summary\": {" >> "$OUTPUT_JSON"
echo "    \"total_rust_repos\": $rust_count," >> "$OUTPUT_JSON"
echo "    \"total_typescript_repos\": $ts_count" >> "$OUTPUT_JSON"
echo "  }" >> "$OUTPUT_JSON"
echo "}" >> "$OUTPUT_JSON"

echo ""
echo "=== INVENTORY SUMMARY (Shell Version) ==="
echo "Rust repositories processed: $rust_count"
echo "TypeScript repositories processed: $ts_count"
echo "JSON output written to: $OUTPUT_JSON"

# Also create a simple YAML version
cat > "$OUTPUT_YAML" << EOF
timestamp: "$(date -Iseconds)"
tool: "shell_script"
summary:
  total_rust_repos: $rust_count
  total_typescript_repos: $ts_count
  tool_used: "shell script with grep/jq parsing"
rust_repos_count: $rust_count
typescript_repos_count: $ts_count
notes:
  - "This is a simplified shell version"
  - "For full dependency parsing, use the Rust version"
  - "See $OUTPUT_JSON for detailed JSON output"
EOF

echo "YAML summary written to: $OUTPUT_YAML"
echo ""
echo "✅ Shell script inventory completed successfully!"
