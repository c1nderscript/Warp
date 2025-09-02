#!/usr/bin/env python3
"""
Documentation Inventory Script for Surrentumlabs

This script recursively scans /home/cinder/Documents/repos/Surrentumlabs/** for 
markdown documentation files and generates a JSON cache with metadata.

Author: Created by Agent Mode for Surrentumlabs documentation management
Purpose: Inventory all documentation files and metadata across Surrentumlabs
Created: 2024-12-22

Target files:
- README.md
- AGENTS.md  
- CHANGELOG.md
- plan.md
- toaster.md
- docs/README.md
- *.md inside docs/ directory

For each file captures:
- absolute path
- repository root
- repo name
- repo category (Monorepo, Rust Component, TypeScript Component, Other)
- primary language(s)
- last-modified timestamp (git log -1 --format=%ct FILE)

Outputs to: .scripts/cache/docs_index.json
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

# Base path to scan
BASE_PATH = "/home/cinder/Documents/repos/Surrentumlabs"

# Target filenames and patterns
TARGET_FILES = {
    "README.md",
    "AGENTS.md", 
    "CHANGELOG.md",
    "plan.md",
    "toaster.md"
}

# Documentation patterns
DOCS_PATTERNS = {
    "docs/README.md",
    "docs/*.md"
}

def get_git_last_modified(file_path: str) -> Optional[int]:
    """
    Get the last modified timestamp using git log -1 --format=%ct FILE
    Returns Unix timestamp or None if git command fails
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", file_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(file_path)
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        pass
    
    # Fallback to file system modification time
    try:
        stat_info = os.stat(file_path)
        return int(stat_info.st_mtime)
    except OSError:
        return None

def determine_repo_category(repo_path: str) -> str:
    """
    Determine repository category based on its parent directory
    """
    parent_dir = os.path.basename(os.path.dirname(repo_path))
    
    category_mapping = {
        "Monorepos": "Monorepo",
        "Rust Component Repos": "Rust Component", 
        "Typescript Component Repos": "TypeScript Component",
        "Other": "Other",
        "whiply_project": "Other"
    }
    
    return category_mapping.get(parent_dir, "Other")

def detect_primary_languages(repo_path: str) -> List[str]:
    """
    Detect primary programming languages in a repository
    """
    languages = []
    
    # Check for common language indicators
    language_indicators = {
        "Rust": ["Cargo.toml", "Cargo.lock", "src/main.rs", "src/lib.rs"],
        "TypeScript": ["package.json", "tsconfig.json", "*.ts", "*.tsx"],
        "JavaScript": ["package.json", "*.js", "*.jsx"],
        "Python": ["requirements.txt", "setup.py", "pyproject.toml", "*.py"],
        "Go": ["go.mod", "go.sum", "*.go"],
        "Java": ["pom.xml", "build.gradle", "*.java"],
        "C++": ["CMakeLists.txt", "Makefile", "*.cpp", "*.cc", "*.cxx"],
        "C": ["Makefile", "*.c", "*.h"]
    }
    
    for lang, indicators in language_indicators.items():
        for indicator in indicators:
            if "*" in indicator:
                # Handle glob patterns
                pattern = indicator.replace("*", "")
                if any(f.endswith(pattern) for f in os.listdir(repo_path) if os.path.isfile(os.path.join(repo_path, f))):
                    languages.append(lang)
                    break
            else:
                # Handle exact file matches
                if os.path.exists(os.path.join(repo_path, indicator)):
                    languages.append(lang)
                    break
    
    # If no languages detected, try to infer from directory structure
    if not languages:
        try:
            files = os.listdir(repo_path)
            if any(f.endswith('.md') for f in files):
                languages.append("Markdown")
        except OSError:
            pass
    
    return languages if languages else ["Unknown"]

def find_repository_root(file_path: str) -> str:
    """
    Find the repository root by looking for .git directory
    """
    current_path = os.path.dirname(file_path)
    
    while current_path != "/":
        if os.path.exists(os.path.join(current_path, ".git")):
            return current_path
        current_path = os.path.dirname(current_path)
    
    # If no .git found, assume the immediate parent of the file is repo root
    return os.path.dirname(file_path)

def get_repo_name(repo_root: str) -> str:
    """
    Extract repository name from the repository root path
    """
    return os.path.basename(repo_root)

def scan_for_docs(base_path: str) -> List[Dict]:
    """
    Recursively scan for documentation files and collect metadata
    """
    docs_inventory = []
    
    for root, dirs, files in os.walk(base_path):
        # Skip .git directories
        dirs[:] = [d for d in dirs if d != '.git']
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if file matches our target patterns
            should_include = False
            
            # Check exact filename matches
            if file in TARGET_FILES:
                should_include = True
            
            # Check docs directory patterns
            if "docs" in root.split(os.sep):
                if file == "README.md" or file.endswith(".md"):
                    should_include = True
            
            if should_include:
                try:
                    repo_root = find_repository_root(file_path)
                    repo_name = get_repo_name(repo_root)
                    repo_category = determine_repo_category(repo_root)
                    primary_languages = detect_primary_languages(repo_root)
                    last_modified = get_git_last_modified(file_path)
                    
                    doc_info = {
                        "absolute_path": file_path,
                        "repository_root": repo_root,
                        "repo_name": repo_name,
                        "repo_category": repo_category,
                        "primary_languages": primary_languages,
                        "last_modified_timestamp": last_modified,
                        "last_modified_date": datetime.fromtimestamp(last_modified).isoformat() if last_modified else None,
                        "filename": file,
                        "relative_path": os.path.relpath(file_path, repo_root)
                    }
                    
                    docs_inventory.append(doc_info)
                    print(f"Found: {file_path}")
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}", file=sys.stderr)
                    continue
    
    return docs_inventory

def main():
    """
    Main function to run the documentation inventory
    """
    print(f"Starting documentation inventory scan of: {BASE_PATH}")
    print(f"Target files: {', '.join(TARGET_FILES)}")
    print(f"Target docs patterns: docs/README.md, docs/*.md")
    print("-" * 60)
    
    if not os.path.exists(BASE_PATH):
        print(f"ERROR: Base path does not exist: {BASE_PATH}")
        sys.exit(1)
    
    # Scan for documentation files
    docs_inventory = scan_for_docs(BASE_PATH)
    
    # Sort by repository name and then by filename for consistent output
    docs_inventory.sort(key=lambda x: (x["repo_name"], x["filename"]))
    
    # Generate summary statistics
    total_files = len(docs_inventory)
    repos_found = len(set(doc["repo_name"] for doc in docs_inventory))
    categories = {}
    languages = {}
    
    for doc in docs_inventory:
        # Count by category
        category = doc["repo_category"]
        categories[category] = categories.get(category, 0) + 1
        
        # Count by languages
        for lang in doc["primary_languages"]:
            languages[lang] = languages.get(lang, 0) + 1
    
    # Create output structure
    output = {
        "metadata": {
            "scan_timestamp": datetime.now().isoformat(),
            "base_path": BASE_PATH,
            "total_files": total_files,
            "repositories_found": repos_found,
            "categories": categories,
            "languages": languages,
            "target_files": list(TARGET_FILES),
            "docs_patterns": list(DOCS_PATTERNS)
        },
        "documentation_files": docs_inventory
    }
    
    # Ensure output directory exists
    output_dir = ".scripts/cache"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write JSON output
    output_file = os.path.join(output_dir, "docs_index.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("-" * 60)
    print(f"Scan complete!")
    print(f"Total files found: {total_files}")
    print(f"Repositories scanned: {repos_found}")
    print(f"Categories: {', '.join(f'{k}({v})' for k, v in categories.items())}")
    print(f"Primary languages: {', '.join(f'{k}({v})' for k, v in languages.items())}")
    print(f"Results written to: {output_file}")

if __name__ == "__main__":
    main()
