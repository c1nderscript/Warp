#!/usr/bin/env python3
"""
Link Repair Script for Warp Documentation Protocol
Fixes common broken link patterns identified in QA validation
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

class LinkRepairer:
    def __init__(self, base_path: str = "/home/cinder/Documents/repos"):
        self.base_path = Path(base_path)
        self.repairs_made = []
        self.files_modified = []
        
    def log_repair(self, file_path: Path, old_link: str, new_link: str):
        """Log a link repair"""
        repair = f"{file_path.relative_to(self.base_path)}: '{old_link}' -> '{new_link}'"
        self.repairs_made.append(repair)
        print(f"🔧 FIXED: {repair}")
        
    def backup_file(self, file_path: Path):
        """Create a backup of the file before modification"""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup-linkfix")
        shutil.copy2(file_path, backup_path)
        print(f"💾 BACKUP: {backup_path}")
        
    def fix_coverage_links(self, content: str, source_file: Path) -> str:
        """Fix [[Coverage]] links to point to correct location"""
        # Pattern: [[Coverage]] -> [[../Twitch Docs/Coverage]]
        if "Warp" in str(source_file):
            content = re.sub(r'\[\[Coverage\]\]', r'[[../Twitch Docs/Coverage]]', content)
        return content
    
    def fix_component_links(self, content: str, source_file: Path) -> str:
        """Fix [[Components/xyz]] links to point to correct location"""
        # Pattern: [[Components/xyz]] -> [[../Twitch Docs/Components/xyz]]
        def replace_component_link(match):
            component_name = match.group(1)
            if "Warp" in str(source_file):
                return f"[[../Twitch Docs/Components/{component_name}]]"
            return match.group(0)
        
        content = re.sub(r'\[\[Components/([^]]+)\]\]', replace_component_link, content)
        return content
    
    def fix_task_backlinks(self, content: str, source_file: Path) -> str:
        """Fix task backlinks to proper relative paths"""
        # Common patterns in Tasks.md and Changelog.md
        if "Warp" in str(source_file):
            # Fix self-referential links
            content = re.sub(r'\[\[\.\.\/\.\.\/Warp\/Tasks\]\]', r'[[Tasks]]', content)
            content = re.sub(r'\[\[\.\.\/\.\.\/Warp\/Changelog\]\]', r'[[Changelog]]', content)
            # Fix simple self-references
            content = re.sub(r'\[\[Tasks\.md\]\]', r'[[Tasks]]', content)
            content = re.sub(r'\[\[Changelog\.md\]\]', r'[[Changelog]]', content)
            content = re.sub(r'\[\[Coverage\.md\]\]', r'[[../Twitch Docs/Coverage]]', content)
        
        return content
    
    def fix_index_links(self, content: str, source_file: Path) -> str:
        """Fix Index links that are missing proper paths"""
        # [[Index]] -> [[../Twitch Docs/Index]] when in Warp directory
        if "Warp" in str(source_file):
            # Be careful not to replace [[../Twitch Docs/Index]] that are already correct
            content = re.sub(r'\[\[Index\]\](?!\s)', r'[[../Twitch Docs/Index]]', content)
        
        return content
    
    def fix_ellipsis_links(self, content: str, source_file: Path) -> str:
        """Fix malformed ellipsis links like [[...]]"""
        # Remove or replace [[...]] links as they're typically placeholders
        content = re.sub(r'\[\[\.\.\.+\]\]', '', content)
        return content
    
    def fix_architecture_docs_links(self, content: str, source_file: Path) -> str:
        """Fix links to missing architecture documents"""
        # Handle cases where docs/architecture paths are referenced
        return content
    
    def fix_empty_component_links(self, content: str, source_file: Path) -> str:
        """Fix empty component references like [[Components/]]"""
        content = re.sub(r'\[\[Components/\]\]', '[[../Twitch Docs/Components]]', content)
        return content
    
    def repair_file(self, file_path: Path) -> bool:
        """Repair broken links in a single file"""
        if not file_path.exists() or not file_path.name.endswith('.md'):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            
            # Apply all repair functions
            repair_functions = [
                self.fix_coverage_links,
                self.fix_component_links,
                self.fix_task_backlinks,
                self.fix_index_links,
                self.fix_ellipsis_links,
                self.fix_empty_component_links,
                self.fix_architecture_docs_links
            ]
            
            for repair_func in repair_functions:
                new_content = repair_func(content, file_path)
                if new_content != content:
                    # Count the changes made by this function
                    changes = len(re.findall(r'\[\[[^]]+\]\]', content)) - len(re.findall(r'\[\[[^]]+\]\]', new_content))
                    if changes != 0:
                        print(f"📝 {repair_func.__name__}: {abs(changes)} changes in {file_path.name}")
                    content = new_content
            
            # If changes were made, write the file
            if content != original_content:
                # Create backup
                self.backup_file(file_path)
                
                # Write repaired content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_modified.append(file_path)
                return True
                
        except Exception as e:
            print(f"❌ ERROR: Failed to repair {file_path}: {e}")
            return False
        
        return False
    
    def repair_directory(self, directory: Path) -> int:
        """Repair all markdown files in a directory"""
        if not directory.exists():
            print(f"⚠️  Directory not found: {directory}")
            return 0
        
        repaired_count = 0
        for md_file in directory.rglob("*.md"):
            if md_file.is_file():
                if self.repair_file(md_file):
                    repaired_count += 1
        
        return repaired_count
    
    def run_comprehensive_repair(self) -> bool:
        """Run comprehensive link repair across all documentation"""
        print("🔧 Starting Comprehensive Link Repair")
        print("=" * 50)
        
        # Repair key directories
        directories_to_repair = [
            self.base_path / "Warp",
            self.base_path / "Twitch Docs",
            self.base_path / "Repos Docs"
        ]
        
        total_repaired = 0
        for directory in directories_to_repair:
            if directory.exists():
                print(f"\n📁 Repairing: {directory}")
                count = self.repair_directory(directory)
                total_repaired += count
                print(f"✅ Repaired {count} files in {directory.name}")
        
        print("\n" + "=" * 50)
        print(f"🎉 REPAIR SUMMARY")
        print("=" * 50)
        print(f"📊 Total files repaired: {total_repaired}")
        print(f"📝 Files modified: {len(self.files_modified)}")
        
        if self.files_modified:
            print("\n📋 Modified files:")
            for file_path in self.files_modified:
                print(f"   • {file_path.relative_to(self.base_path)}")
        
        return total_repaired > 0

def main():
    print("🚀 Warp Documentation Link Repair Tool")
    print("=" * 50)
    
    repairer = LinkRepairer()
    success = repairer.run_comprehensive_repair()
    
    if success:
        print("\n✅ Link repair completed successfully!")
        print("🔍 Run qa_checks.py again to validate repairs")
    else:
        print("\n⚠️  No repairs needed or repair failed")
    
    return 0

if __name__ == "__main__":
    exit(main())
