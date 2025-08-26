#!/usr/bin/env python3
"""
Quality Assurance Script for Warp Documentation Protocol
Step 10: Quality Assurance & Final Commit

Performs automated checks:
• All Markdown links resolve
• Coverage.md counts match actual files  
• No orphan files without backlinks
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class WarpQualityChecker:
    def __init__(self, base_path: str = "/home/cinder/Documents/repos"):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.link_cache = {}
        self.file_counts = {}
        
    def log_error(self, message: str):
        """Log an error message"""
        self.errors.append(message)
        print(f"❌ ERROR: {message}")
        
    def log_warning(self, message: str):
        """Log a warning message"""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")
        
    def log_success(self, message: str):
        """Log a success message"""
        print(f"✅ {message}")

    def find_markdown_files(self) -> List[Path]:
        """Find all Markdown files in the documentation structure"""
        markdown_files = []
        
        # Search in key directories
        search_dirs = [
            self.base_path / "Warp",
            self.base_path / "Twitch Docs", 
            self.base_path / "Repos Docs"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for md_file in search_dir.rglob("*.md"):
                    if md_file.is_file():
                        markdown_files.append(md_file)
        
        return markdown_files

    def extract_markdown_links(self, content: str) -> List[str]:
        """Extract Obsidian-style [[...]] and standard [...](...) markdown links"""
        obsidian_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        standard_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        links = []
        # Add Obsidian links
        links.extend(obsidian_links)
        
        # Add standard links (file paths only, not URLs)
        for text, url in standard_links:
            if not url.startswith(('http', 'mailto:', '#')):
                links.append(url)
        
        return links

    def resolve_link(self, link: str, source_file: Path) -> bool:
        """Check if a link resolves to an existing file"""
        # Cache links to avoid repeated file system checks
        cache_key = f"{source_file}:{link}"
        if cache_key in self.link_cache:
            return self.link_cache[cache_key]
        
        # Clean up link - remove fragments
        clean_link = link.split('#')[0]
        
        # Handle relative paths
        if clean_link.startswith('../'):
            target_path = (source_file.parent / clean_link).resolve()
        elif clean_link.startswith('./'):
            target_path = (source_file.parent / clean_link[2:]).resolve()
        elif '/' in clean_link:
            # Absolute path within documentation structure
            target_path = self.base_path / clean_link.lstrip('/')
        else:
            # Relative to current directory or search in common locations
            target_path = source_file.parent / f"{clean_link}.md"
            
            # If not found, search in common doc locations
            if not target_path.exists():
                search_locations = [
                    source_file.parent / "Components" / f"{clean_link}.md",
                    self.base_path / "Twitch Docs" / "Components" / f"{clean_link}.md",
                    self.base_path / "Repos Docs" / clean_link / "Coverage.md",
                    self.base_path / "Warp" / f"{clean_link}.md"
                ]
                
                for search_path in search_locations:
                    if search_path.exists():
                        target_path = search_path
                        break
        
        # Check if target exists
        exists = target_path.exists()
        
        # Also try with .md extension if no extension provided
        if not exists and not clean_link.endswith('.md'):
            md_path = target_path.with_suffix('.md')
            exists = md_path.exists()
        
        self.link_cache[cache_key] = exists
        return exists

    def check_markdown_links(self) -> bool:
        """Check that all Markdown links resolve to existing files"""
        print("\n🔍 Checking Markdown links...")
        
        markdown_files = self.find_markdown_files()
        all_links_valid = True
        broken_links = []
        
        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                links = self.extract_markdown_links(content)
                
                for link in links:
                    if not self.resolve_link(link, md_file):
                        broken_links.append((md_file, link))
                        all_links_valid = False
                        
            except Exception as e:
                self.log_error(f"Error reading {md_file}: {e}")
                all_links_valid = False
        
        if broken_links:
            for file_path, link in broken_links:
                self.log_error(f"Broken link '{link}' in {file_path}")
        else:
            self.log_success("All Markdown links resolve correctly")
            
        return all_links_valid

    def count_files_in_coverage(self, coverage_file: Path) -> Dict[str, int]:
        """Count components/files listed in a Coverage.md file"""
        if not coverage_file.exists():
            return {}
        
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            counts = {
                'total': 0,
                'todo': 0,
                'partial': 0,
                'done': 0,
                'disconnected': 0
            }
            
            # Look for table rows with status indicators
            # Match various table formats used in Coverage files
            table_rows = re.findall(r'\|[^|]*\|[^|]*\|[^|]*\|(todo|partial|done|disconnected)', content, re.IGNORECASE)
            
            for status in table_rows:
                status_lower = status.lower()
                if status_lower in counts:
                    counts[status_lower] += 1
                    counts['total'] += 1
            
            # Also check for checkbox lists
            checkbox_patterns = [
                r'- \[[x ]\][^|]*\|(todo|partial|done|disconnected)',
                r'- \[[x ]\].*– ([^|]*) – see',
            ]
            
            for pattern in checkbox_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        status_lower = 'todo'  # Assume these are todos
                    else:
                        status_lower = match.lower()
                    
                    if status_lower in counts:
                        counts[status_lower] += 1
                        counts['total'] += 1
            
            return counts
            
        except Exception as e:
            self.log_error(f"Error reading coverage file {coverage_file}: {e}")
            return {}

    def count_actual_files(self) -> Dict[str, int]:
        """Count actual files in the documentation structure"""
        counts = {
            'component_cards': 0,
            'coverage_files': 0,
            'repo_docs': 0,
            'twitch_docs': 0
        }
        
        # Count Component Cards
        component_dirs = [
            self.base_path / "Twitch Docs" / "Components",
            self.base_path / "Repos Docs" / "Components"
        ]
        
        for comp_dir in component_dirs:
            if comp_dir.exists():
                counts['component_cards'] += len(list(comp_dir.glob("*.md")))
        
        # Count Coverage files
        coverage_files = self.find_coverage_files()
        counts['coverage_files'] = len(coverage_files)
        
        # Count repository documentation directories
        repos_docs = self.base_path / "Repos Docs"
        if repos_docs.exists():
            for item in repos_docs.iterdir():
                if item.is_dir() and item.name not in ["Components", "Index.md"]:
                    counts['repo_docs'] += 1
        
        return counts

    def find_coverage_files(self) -> List[Path]:
        """Find all Coverage.md files"""
        coverage_files = []
        for coverage_file in self.base_path.rglob("Coverage.md"):
            if coverage_file.is_file():
                coverage_files.append(coverage_file)
        return coverage_files

    def check_coverage_counts(self) -> bool:
        """Check that Coverage.md counts match actual files"""
        print("\n🔍 Checking Coverage.md counts...")
        
        coverage_files = self.find_coverage_files()
        counts_match = True
        
        # Get main coverage files
        main_coverage_files = [
            self.base_path / "Twitch Docs" / "Coverage.md",
            self.base_path / "Warp" / "rust-components" / "Coverage.md",
            self.base_path / "Warp" / "typescript-components" / "Coverage.md"
        ]
        
        actual_counts = self.count_actual_files()
        
        for coverage_file in main_coverage_files:
            if coverage_file.exists():
                file_counts = self.count_files_in_coverage(coverage_file)
                relative_path = coverage_file.relative_to(self.base_path)
                
                if file_counts['total'] > 0:
                    self.log_success(f"{relative_path}: {file_counts['total']} components tracked")
                    self.log_success(f"  - Todo: {file_counts['todo']}, Partial: {file_counts['partial']}, Done: {file_counts['done']}")
                    if file_counts['disconnected'] > 0:
                        self.log_success(f"  - Disconnected: {file_counts['disconnected']}")
                else:
                    self.log_warning(f"{relative_path}: No components found in tracking tables")
        
        # Check overall file counts
        total_coverage_files = len(coverage_files)
        if total_coverage_files > 0:
            self.log_success(f"Found {total_coverage_files} Coverage.md files")
            self.log_success(f"Found {actual_counts['component_cards']} Component Cards")
            self.log_success(f"Found {actual_counts['repo_docs']} repository documentation directories")
        
        return counts_match

    def find_orphan_files(self) -> List[Path]:
        """Find files that don't have backlinks from other documentation"""
        print("\n🔍 Checking for orphan files...")
        
        markdown_files = self.find_markdown_files()
        all_links = set()
        
        # Collect all links from all files
        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                links = self.extract_markdown_links(content)
                for link in links:
                    # Normalize link paths
                    clean_link = link.split('#')[0]
                    if clean_link:
                        all_links.add(clean_link)
                        
            except Exception as e:
                self.log_warning(f"Error reading {md_file} for link extraction: {e}")
        
        # Find files that aren't linked to
        orphan_files = []
        
        for md_file in markdown_files:
            # Skip certain system files
            if md_file.name in ['Readme.md', 'README.md', 'Index.md', 'Changelog.md', 'Tasks.md', 'AGENTS.md']:
                continue
                
            file_referenced = False
            file_stem = md_file.stem
            relative_path = str(md_file.relative_to(self.base_path))
            
            # Check if this file is referenced by any link
            for link in all_links:
                if (link == file_stem or 
                    link == relative_path or
                    link.endswith(f"/{file_stem}") or
                    link.endswith(f"/{md_file.name}") or
                    file_stem in link):
                    file_referenced = True
                    break
            
            if not file_referenced:
                orphan_files.append(md_file)
        
        if orphan_files:
            for orphan in orphan_files:
                self.log_warning(f"Orphan file (no backlinks): {orphan.relative_to(self.base_path)}")
        else:
            self.log_success("No orphan files found - all files have backlinks")
        
        return orphan_files

    def run_all_checks(self) -> bool:
        """Run all quality assurance checks"""
        print("🚀 Starting Warp Documentation Protocol Quality Assurance Checks")
        print("=" * 70)
        
        # Check 1: Markdown links
        links_valid = self.check_markdown_links()
        
        # Check 2: Coverage counts
        counts_match = self.check_coverage_counts()
        
        # Check 3: Orphan files
        orphan_files = self.find_orphan_files()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 Quality Assurance Summary")
        print("=" * 70)
        
        if self.errors:
            print(f"❌ {len(self.errors)} errors found:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings found:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        all_checks_passed = len(self.errors) == 0
        
        if all_checks_passed:
            print("✅ All quality assurance checks PASSED!")
            print("🎉 Documentation is ready for final commit")
        else:
            print("❌ Quality assurance checks FAILED")
            print("🔧 Please fix errors before committing")
        
        return all_checks_passed

def main():
    checker = WarpQualityChecker()
    success = checker.run_all_checks()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
