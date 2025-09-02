# Documentation Inventory Scripts

This directory contains scripts for inventorying documentation files across the Surrentumlabs ecosystem.

## Scripts Overview

Three implementations are provided for different use cases and environments:

### 1. Python Version (`inventory_docs.py`)
- **Best for:** Full-featured scanning with robust error handling
- **Requirements:** Python 3.6+
- **Features:** 
  - Comprehensive language detection
  - Robust git integration
  - Detailed error reporting
  - Extensive metadata collection

### 2. Node.js Version (`inventory_docs.js`)  
- **Best for:** Async processing and JavaScript ecosystem integration
- **Requirements:** Node.js 12+
- **Features:**
  - Async file processing
  - Native JavaScript JSON handling
  - Modular design for integration

### 3. Bash Version (`inventory_docs.sh`)
- **Best for:** Lightweight scanning without external dependencies
- **Requirements:** Bash 4+, jq
- **Features:**
  - Minimal resource usage
  - Shell-native processing
  - Quick scanning

## Target Documentation Files

All scripts scan for these markdown files:

### Exact Filename Matches
- `README.md` - Project overview and setup instructions
- `AGENTS.md` - Agent configuration and rules (per RULE dqDrwrElzQfaQ6lVR1ZtY2)
- `CHANGELOG.md` - Version history and changes
- `plan.md` - Project planning and roadmaps
- `toaster.md` - Build and deployment configuration

### Documentation Directory Patterns
- `docs/README.md` - Main documentation entry point
- `docs/*.md` - Any markdown file inside docs directories

## Repository Categories

Files are automatically categorized based on their location:

- **Monorepo**: Files under `Surrentumlabs/Monorepos/`
- **Rust Component**: Files under `Surrentumlabs/Rust Component Repos/`  
- **TypeScript Component**: Files under `Surrentumlabs/Typescript Component Repos/`
- **Other**: Files under `Surrentumlabs/Other/` or `whiply_project/`

## Usage

### Python Version (Recommended)
```bash
python3 .scripts/inventory_docs.py
```

### Node.js Version
```bash
node .scripts/inventory_docs.js
```

### Bash Version
```bash
./.scripts/inventory_docs.sh
```

## Output Format

All scripts generate JSON output in `.scripts/cache/docs_index*.json` with this structure:

```json
{
  "metadata": {
    "scan_timestamp": "2024-12-22T10:30:21.850820",
    "base_path": "/home/cinder/Documents/repos/Surrentumlabs",
    "total_files": 2874,
    "repositories_found": 31,
    "categories": {
      "Monorepo": 381,
      "TypeScript Component": 317,
      "Other": 964,
      "Rust Component": 1212
    },
    "languages": {
      "Rust": 1197,
      "Go": 1153,
      "TypeScript": 729,
      "JavaScript": 729
    },
    "target_files": ["README.md", "AGENTS.md", "CHANGELOG.md", "plan.md", "toaster.md"],
    "docs_patterns": ["docs/README.md", "docs/*.md"]
  },
  "documentation_files": [
    {
      "absolute_path": "/home/cinder/Documents/repos/Surrentumlabs/...",
      "repository_root": "/home/cinder/Documents/repos/Surrentumlabs/...",
      "repo_name": "example-repo",
      "repo_category": "Rust Component",
      "primary_languages": ["Rust", "Go"],
      "last_modified_timestamp": 1756222935,
      "last_modified_date": "2025-08-26T15:42:15",
      "filename": "README.md",
      "relative_path": "README.md"
    }
  ]
}
```

## Metadata Fields

For each documentation file, the following metadata is captured:

- **absolute_path**: Full filesystem path to the file
- **repository_root**: Root directory of the containing repository  
- **repo_name**: Name of the repository (basename of repo root)
- **repo_category**: Category based on parent directory structure
- **primary_languages**: Detected programming languages in the repository
- **last_modified_timestamp**: Unix timestamp from `git log -1 --format=%ct FILE`
- **last_modified_date**: ISO 8601 formatted date of last modification
- **filename**: Base filename (e.g., "README.md")
- **relative_path**: Path relative to repository root

## Language Detection

Scripts detect primary languages by looking for these indicators:

- **Rust**: `Cargo.toml`, `Cargo.lock`, `src/main.rs`, `src/lib.rs`
- **TypeScript/JavaScript**: `package.json`, `tsconfig.json`
- **Go**: `go.mod`, `go.sum`
- **Python**: `requirements.txt`, `setup.py`, `pyproject.toml`
- **C++**: `CMakeLists.txt`, `Makefile`
- **Java**: `pom.xml`, `build.gradle`

## Performance Considerations

- **Python version**: ~30-60 seconds for full scan, most accurate
- **Node.js version**: ~20-45 seconds, good async performance
- **Bash version**: ~15-30 seconds, fastest but basic language detection

## Cache Files

Generated cache files:
- `docs_index.json` - Python version output (default)
- `docs_index_node.json` - Node.js version output
- `docs_index_bash.json` - Bash version output

## Integration with Later Steps

The JSON cache files are designed to be consumed by subsequent steps in the documentation workflow:

```bash
# Example: Query specific repository types
jq '.documentation_files | map(select(.repo_category == "Rust Component"))' .scripts/cache/docs_index.json

# Example: Find recently modified files
jq '.documentation_files | map(select(.last_modified_timestamp > 1756220000))' .scripts/cache/docs_index.json

# Example: Get all AGENTS.md files
jq '.documentation_files | map(select(.filename == "AGENTS.md"))' .scripts/cache/docs_index.json
```

## Code Annotations

All scripts are annotated per RULE zb1YgK1oGzQCJ7qBVsLYBy:

- **Author**: Created by Agent Mode for Surrentumlabs documentation management
- **Purpose**: Inventory all documentation files and metadata across Surrentumlabs  
- **Created**: 2024-12-22
- **Target files and patterns clearly documented**
- **Metadata schema fully specified**

## Error Handling

- Git errors fall back to filesystem timestamps
- Permission errors are logged and skipped
- Malformed repositories default to "Other" category
- Missing language indicators default to "Markdown"

---

**Note**: These scripts follow RULE dqDrwrElzQfaQ6lVR1ZtY2 by prioritizing AGENTS.md files and ensuring comprehensive coverage of all documentation assets across the Surrentumlabs ecosystem.
