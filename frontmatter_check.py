#!/usr/bin/env python3

import os
import re
import yaml
import sys
from pathlib import Path

def check_frontmatter(file_path):
    """Check if YAML frontmatter in a markdown file is valid"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has frontmatter
        if not content.startswith('---'):
            return True  # No frontmatter is okay
            
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"❌ ERROR: Invalid frontmatter format in {file_path}")
            return False
            
        frontmatter = parts[1].strip()
        if not frontmatter:
            return True  # Empty frontmatter is okay
            
        # Try to parse YAML
        try:
            yaml.safe_load(frontmatter)
            print(f"✅ YAML frontmatter valid in {file_path}")
            return True
        except yaml.YAMLError as e:
            print(f"❌ ERROR: Invalid YAML frontmatter in {file_path}: {e}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Could not read {file_path}: {e}")
        return False

def main():
    """Check all markdown files for valid YAML frontmatter"""
    print("🔍 Checking YAML frontmatter in markdown files...")
    
    markdown_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    
    all_valid = True
    total_files = len(markdown_files)
    
    for file_path in markdown_files:
        if not check_frontmatter(file_path):
            all_valid = False
    
    print(f"\n📊 Summary: Checked {total_files} markdown files")
    if all_valid:
        print("✅ All YAML frontmatter is valid!")
        return 0
    else:
        print("❌ Some YAML frontmatter issues found!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
