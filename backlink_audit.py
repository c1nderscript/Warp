#!/usr/bin/env python3
"""
Backlink Audit Script for Warp Documentation System
Step 9: Validation & backlink audit

This script validates:
1. Every Coverage.md appears in at least one backlink from Index.md
2. Every Component Card links back to its Coverage.md
3. Identifies broken links and suggests fixes
4. Updates status from todo → done where appropriate
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LinkIssue:
    """Represents a link issue found during audit"""
    file_path: str
    issue_type: str
    description: str
    suggested_fix: str = ""

@dataclass
class AuditResults:
    """Container for audit results"""
    coverage_files: List[str]
    component_cards: List[str]
    index_files: List[str]
    issues: List[LinkIssue]
    valid_backlinks: List[Tuple[str, str]]
    missing_backlinks: List[str]

class BacklinkAuditor:
    def __init__(self, base_path: str = "/home/cinder/Documents"):
        self.base_path = Path(base_path)
        self.results = AuditResults([], [], [], [], [], [])
        
    def find_documentation_files(self) -> None:
        """Find all Coverage.md, Index.md, and Component Card files"""
        print("🔍 Discovering documentation files...")
        
        # Find all Coverage.md files
        self.results.coverage_files = list(glob.glob(str(self.base_path / "**" / "Coverage.md"), recursive=True))
        print(f"   Found {len(self.results.coverage_files)} Coverage.md files")
        
        # Find all Index.md files
        self.results.index_files = list(glob.glob(str(self.base_path / "**" / "Index.md"), recursive=True))
        print(f"   Found {len(self.results.index_files)} Index.md files")
        
        # Find all Component Cards (Components/*.md files)
        component_pattern = str(self.base_path / "**" / "Components" / "*.md")
        self.results.component_cards = list(glob.glob(component_pattern, recursive=True))
        print(f"   Found {len(self.results.component_cards)} Component Card files")
    
    def extract_obsidian_links(self, content: str) -> Set[str]:
        """Extract all Obsidian-style [[...]] links from content"""
        # Pattern to match [[link]] or [[link|display text]]
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]'
        matches = re.findall(pattern, content)
        return set(matches)
    
    def read_file_content(self, file_path: str) -> str:
        """Read file content with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return ""
    
    def check_coverage_in_index_backlinks(self) -> None:
        """Verify every Coverage.md appears in at least one backlink from Index.md"""
        print("\n📋 Checking Coverage.md backlinks from Index.md files...")
        
        # Collect all links from all Index.md files
        index_links = set()
        for index_file in self.results.index_files:
            content = self.read_file_content(index_file)
            links = self.extract_obsidian_links(content)
            index_links.update(links)
            print(f"   📄 {index_file}: {len(links)} links found")
        
        # Check each Coverage.md file
        for coverage_file in self.results.coverage_files:
            coverage_path = Path(coverage_file)
            
            # Generate expected link patterns for this Coverage file
            expected_patterns = [
                "Coverage",  # Direct link
                f"{coverage_path.parent.name}/Coverage",  # With parent directory
            ]
            
            # Check if any pattern appears in index links
            found_backlink = False
            for pattern in expected_patterns:
                if any(pattern in link or link in pattern for link in index_links):
                    found_backlink = True
                    self.results.valid_backlinks.append((coverage_file, pattern))
                    break
            
            if not found_backlink:
                self.results.missing_backlinks.append(coverage_file)
                relative_path = str(coverage_path.relative_to(self.base_path))
                self.results.issues.append(LinkIssue(
                    file_path=coverage_file,
                    issue_type="Missing Index Backlink",
                    description=f"Coverage file {relative_path} not referenced in any Index.md",
                    suggested_fix=f"Add [[{coverage_path.parent.name}/Coverage]] to appropriate Index.md"
                ))
    
    def check_component_card_backlinks(self) -> None:
        """Verify every Component Card links back to its Coverage.md"""
        print("\n🗂️  Checking Component Card backlinks to Coverage.md...")
        
        for card_file in self.results.component_cards:
            card_path = Path(card_file)
            content = self.read_file_content(card_file)
            links = self.extract_obsidian_links(content)
            
            # Find the expected Coverage.md path for this component
            # Component cards should be in: .../repo-name/Components/card.md
            # Coverage should be in: .../repo-name/Coverage.md
            expected_coverage_dir = card_path.parent.parent
            expected_coverage_file = expected_coverage_dir / "Coverage.md"
            
            # Check if Coverage link exists in the component card
            coverage_patterns = [
                "Coverage",
                "../Coverage",
                f"{expected_coverage_dir.name}/Coverage"
            ]
            
            found_coverage_link = False
            for pattern in coverage_patterns:
                if any(pattern in link or link.endswith('Coverage') for link in links):
                    found_coverage_link = True
                    self.results.valid_backlinks.append((card_file, pattern))
                    break
            
            if not found_coverage_link:
                relative_card = str(card_path.relative_to(self.base_path))
                self.results.issues.append(LinkIssue(
                    file_path=card_file,
                    issue_type="Missing Coverage Backlink",
                    description=f"Component card {relative_card} does not link to Coverage.md",
                    suggested_fix="Add [[Coverage]] or [[../Coverage]] to the component card"
                ))
            
            # Check if it also links to Index
            index_patterns = ["Index", "../Index", "Index.md"]
            found_index_link = any(
                any(pattern in link or link.endswith('Index') for pattern in index_patterns)
                for link in links
            )
            
            if not found_index_link:
                relative_card = str(card_path.relative_to(self.base_path))
                self.results.issues.append(LinkIssue(
                    file_path=card_file,
                    issue_type="Missing Index Backlink",
                    description=f"Component card {relative_card} does not link to Index.md",
                    suggested_fix="Add [[Index]] or [[../Index]] to the component card"
                ))
    
    def check_status_updates_needed(self) -> None:
        """Check for status updates from todo → done where appropriate"""
        print("\n📊 Checking for status updates (todo → done)...")
        
        for coverage_file in self.results.coverage_files:
            content = self.read_file_content(coverage_file)
            
            # Look for todo items that might be done
            # This is a heuristic check - look for patterns that suggest completion
            todo_pattern = r'- \[ \].*?status.*?todo'
            done_pattern = r'- \[x\].*?status.*?done'
            
            todo_matches = re.findall(todo_pattern, content, re.IGNORECASE)
            done_matches = re.findall(done_pattern, content, re.IGNORECASE)
            
            # Check if component cards exist for todo items
            coverage_path = Path(coverage_file)
            components_dir = coverage_path.parent / "Components"
            
            if components_dir.exists():
                existing_components = list(components_dir.glob("*.md"))
                if todo_matches and existing_components:
                    relative_coverage = str(coverage_path.relative_to(self.base_path))
                    self.results.issues.append(LinkIssue(
                        file_path=coverage_file,
                        issue_type="Status Update Needed",
                        description=f"{relative_coverage} has todo items but {len(existing_components)} component cards exist",
                        suggested_fix="Review and update status from todo → done for completed components"
                    ))
    
    def generate_report(self) -> str:
        """Generate comprehensive audit report"""
        report = []
        report.append("# Backlink Audit Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- **Coverage Files**: {len(self.results.coverage_files)}")
        report.append(f"- **Component Cards**: {len(self.results.component_cards)}")
        report.append(f"- **Index Files**: {len(self.results.index_files)}")
        report.append(f"- **Valid Backlinks**: {len(self.results.valid_backlinks)}")
        report.append(f"- **Issues Found**: {len(self.results.issues)}")
        report.append("")
        
        # Issues by type
        if self.results.issues:
            issue_types = {}
            for issue in self.results.issues:
                issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
            
            report.append("## Issues by Type")
            for issue_type, count in issue_types.items():
                report.append(f"- **{issue_type}**: {count}")
            report.append("")
        
        # Missing backlinks
        if self.results.missing_backlinks:
            report.append("## Coverage Files Missing Index Backlinks")
            for coverage_file in self.results.missing_backlinks:
                relative_path = str(Path(coverage_file).relative_to(self.base_path))
                report.append(f"- `{relative_path}`")
            report.append("")
        
        # Detailed issues
        if self.results.issues:
            report.append("## Detailed Issues")
            for i, issue in enumerate(self.results.issues, 1):
                relative_path = str(Path(issue.file_path).relative_to(self.base_path))
                report.append(f"### {i}. {issue.issue_type}")
                report.append(f"**File**: `{relative_path}`")
                report.append(f"**Issue**: {issue.description}")
                if issue.suggested_fix:
                    report.append(f"**Suggested Fix**: {issue.suggested_fix}")
                report.append("")
        
        # Valid backlinks (sample)
        if self.results.valid_backlinks:
            report.append("## Valid Backlinks (Sample)")
            for i, (file_path, link) in enumerate(self.results.valid_backlinks[:10], 1):
                relative_path = str(Path(file_path).relative_to(self.base_path))
                report.append(f"{i}. `{relative_path}` ← `{link}`")
            if len(self.results.valid_backlinks) > 10:
                report.append(f"... and {len(self.results.valid_backlinks) - 10} more")
            report.append("")
        
        return "\n".join(report)
    
    def run_audit(self) -> AuditResults:
        """Run the complete backlink audit"""
        print("🔍 Starting Backlink Audit for Warp Documentation System")
        print("=" * 60)
        
        self.find_documentation_files()
        self.check_coverage_in_index_backlinks()
        self.check_component_card_backlinks()
        self.check_status_updates_needed()
        
        print("\n" + "=" * 60)
        print("✅ Audit Complete!")
        print(f"📊 Found {len(self.results.issues)} issues to address")
        
        return self.results

def main():
    """Main execution function"""
    auditor = BacklinkAuditor()
    results = auditor.run_audit()
    
    # Generate and save report
    report = auditor.generate_report()
    report_file = "/home/cinder/Documents/repos/Warp/backlink_audit_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📝 Report saved to: {report_file}")
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    print(f"Coverage Files: {len(results.coverage_files)}")
    print(f"Component Cards: {len(results.component_cards)}")
    print(f"Valid Backlinks: {len(results.valid_backlinks)}")
    print(f"Issues Found: {len(results.issues)}")
    
    if results.issues:
        print("\nISSUES TO ADDRESS:")
        issue_types = {}
        for issue in results.issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        for issue_type, count in issue_types.items():
            print(f"  {issue_type}: {count}")

if __name__ == "__main__":
    main()
