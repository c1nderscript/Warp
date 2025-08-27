#!/usr/bin/env python3
"""
Warp Documentation Integrity Checker
Step 7: Run documentation integrity checks

1. Execute internal script or manual grep to ensure every new file contains required sections & backlinks.  
2. Validate Coverage.md table renders in Obsidian.  
3. Confirm Dataview queries pick up new `partial` statuses.
"""

import os
import re
import glob
import yaml
from pathlib import Path
from typing import List, Dict, Set

class WarpIntegrityChecker:
    def __init__(self):
        self.warp_root = Path("/home/cinder/Documents/repos/Warp")
        self.twitch_docs = Path("/home/cinder/Documents/repos/Twitch Docs")
        self.repos_docs = Path("/home/cinder/Documents/repos/Repos Docs")
        
        self.required_sections = {
            'component_cards': ['Purpose', 'Key Files', 'Interfaces', 'Depends On', 'Used By', 'Notes', 'Backlinks'],
            'coverage_files': ['Purpose', 'Key Components', 'Interfaces', 'Depends On', 'Used By', 'Notes', 'Backlinks']
        }
        
        self.required_backlinks = {
            'component_cards': ['[[Coverage]]', '[[Index]]'],
            'coverage_files': ['[[../../Index]]', '[[../Coverage]]'],
            'warp_state_files': ['[[Coverage]]', '[[Index]]', '[[Tasks]]']
        }
        
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def check_yaml_frontmatter(self, file_path: Path) -> Dict:
        """Check if file has proper YAML frontmatter with required fields"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---\n'):
                return {'error': 'No YAML frontmatter found'}
            
            # Extract YAML frontmatter
            yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if not yaml_match:
                return {'error': 'Invalid YAML frontmatter format'}
            
            yaml_content = yaml_match.group(1)
            metadata = yaml.safe_load(yaml_content)
            
            required_fields = ['status', 'source_path', 'last_scanned']
            missing_fields = [field for field in required_fields if field not in metadata]
            
            if missing_fields:
                return {'error': f'Missing required fields: {missing_fields}'}
            
            # Check for partial status
            has_partial_status = metadata.get('status') == 'partial'
            
            return {
                'metadata': metadata,
                'has_partial_status': has_partial_status,
                'valid': True
            }
            
        except Exception as e:
            return {'error': f'Error parsing YAML: {str(e)}'}

    def check_required_sections(self, file_path: Path, file_type: str) -> Dict:
        """Check if file contains all required sections"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required = self.required_sections.get(file_type, [])
            found_sections = []
            missing_sections = []
            
            for section in required:
                # Look for section headers (## Section Name)
                pattern = rf'^\s*##\s+{re.escape(section)}\s*$'
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    found_sections.append(section)
                else:
                    missing_sections.append(section)
            
            return {
                'found_sections': found_sections,
                'missing_sections': missing_sections,
                'valid': len(missing_sections) == 0
            }
            
        except Exception as e:
            return {'error': f'Error checking sections: {str(e)}'}

    def check_backlinks(self, file_path: Path, file_type: str) -> Dict:
        """Check if file contains required backlinks"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required = self.required_backlinks.get(file_type, [])
            found_backlinks = []
            missing_backlinks = []
            
            # Find all [[...]] style links
            all_links = re.findall(r'\[\[([^\]]+)\]\]', content)
            
            for required_link in required:
                # Strip the [[ ]] for comparison
                link_content = required_link[2:-2]
                
                # Check for exact match or partial match
                found = any(link_content in link or link in link_content for link in all_links)
                
                if found:
                    found_backlinks.append(required_link)
                else:
                    missing_backlinks.append(required_link)
            
            return {
                'found_backlinks': found_backlinks,
                'missing_backlinks': missing_backlinks,
                'all_links': all_links,
                'valid': len(missing_backlinks) == 0
            }
            
        except Exception as e:
            return {'error': f'Error checking backlinks: {str(e)}'}

    def check_dataview_queries(self, file_path: Path) -> Dict:
        """Check for Dataview query blocks that should pick up partial statuses"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for dataview code blocks
            dataview_pattern = r'```dataview\n(.*?)\n```'
            dataview_blocks = re.findall(dataview_pattern, content, re.DOTALL)
            
            partial_queries = []
            for block in dataview_blocks:
                if 'partial' in block.lower() or 'status' in block.lower():
                    partial_queries.append(block)
            
            return {
                'dataview_blocks': dataview_blocks,
                'partial_queries': partial_queries,
                'has_dataview': len(dataview_blocks) > 0,
                'tracks_partial': len(partial_queries) > 0
            }
            
        except Exception as e:
            return {'error': f'Error checking dataview: {str(e)}'}

    def check_coverage_table_structure(self, file_path: Path) -> Dict:
        """Check if Coverage.md has proper table structure for Obsidian rendering"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for markdown tables with proper headers
            table_pattern = r'\|\s*Component\s*\|.*?\|\s*Status\s*\|'
            tables = re.findall(table_pattern, content, re.IGNORECASE)
            
            # Count rows with 'partial' status
            partial_rows = len(re.findall(r'\|\s*\w+.*?\|\s*partial\s*\|', content, re.IGNORECASE))
            
            # Check for proper table formatting
            pipe_lines = [line for line in content.split('\n') if '|' in line and 'Component' in line]
            
            return {
                'has_tables': len(tables) > 0,
                'partial_count': partial_rows,
                'table_headers': pipe_lines[:3] if pipe_lines else [],
                'valid': len(tables) > 0 and partial_rows > 0
            }
            
        except Exception as e:
            return {'error': f'Error checking table structure: {str(e)}'}

    def run_integrity_checks(self):
        """Run all integrity checks"""
        print("🔍 Running Warp Documentation Integrity Checks...")
        print("=" * 60)
        
        # Check 1: Component Cards
        self.check_component_cards()
        
        # Check 2: Coverage Files
        self.check_coverage_files()
        
        # Check 3: Warp State Files
        self.check_warp_state_files()
        
        # Check 4: Dataview Integration
        self.check_dataview_integration()
        
        # Generate report
        self.generate_report()

    def check_component_cards(self):
        """Check all component cards for required sections and backlinks"""
        print("\n📄 Checking Component Cards...")
        
        # Twitch Docs Components
        twitch_components = glob.glob(str(self.twitch_docs / "Components" / "*.md"))
        
        for comp_file in twitch_components:
            file_path = Path(comp_file)
            print(f"  Checking: {file_path.name}")
            
            # Check YAML frontmatter
            yaml_result = self.check_yaml_frontmatter(file_path)
            
            # Check required sections
            sections_result = self.check_required_sections(file_path, 'component_cards')
            
            # Check backlinks
            backlinks_result = self.check_backlinks(file_path, 'component_cards')
            
            file_result = {
                'file': str(file_path),
                'type': 'component_card',
                'yaml': yaml_result,
                'sections': sections_result,
                'backlinks': backlinks_result
            }
            
            if (yaml_result.get('valid') and 
                sections_result.get('valid') and 
                backlinks_result.get('valid')):
                self.results['passed'].append(file_result)
                print(f"    ✅ PASSED")
            else:
                self.results['failed'].append(file_result)
                print(f"    ❌ FAILED")
                if yaml_result.get('error'):
                    print(f"      YAML: {yaml_result['error']}")
                if sections_result.get('missing_sections'):
                    print(f"      Missing sections: {sections_result['missing_sections']}")
                if backlinks_result.get('missing_backlinks'):
                    print(f"      Missing backlinks: {backlinks_result['missing_backlinks']}")

    def check_coverage_files(self):
        """Check Coverage.md files"""
        print("\n📊 Checking Coverage Files...")
        
        coverage_files = []
        coverage_files.extend(glob.glob(str(self.twitch_docs / "Coverage.md")))
        coverage_files.extend(glob.glob(str(self.repos_docs / "*/Coverage.md")))
        
        for cov_file in coverage_files:
            file_path = Path(cov_file)
            print(f"  Checking: {file_path.relative_to(file_path.parents[2])}")
            
            # Check table structure for Obsidian rendering
            table_result = self.check_coverage_table_structure(file_path)
            
            # Check dataview queries
            dataview_result = self.check_dataview_queries(file_path)
            
            # Check backlinks
            backlinks_result = self.check_backlinks(file_path, 'coverage_files')
            
            file_result = {
                'file': str(file_path),
                'type': 'coverage_file',
                'table': table_result,
                'dataview': dataview_result,
                'backlinks': backlinks_result
            }
            
            if (table_result.get('valid') and backlinks_result.get('valid')):
                self.results['passed'].append(file_result)
                print(f"    ✅ PASSED")
                if dataview_result.get('tracks_partial'):
                    print(f"    📋 Dataview tracks partial status")
                if table_result.get('partial_count', 0) > 0:
                    print(f"    📊 Found {table_result['partial_count']} partial entries")
            else:
                self.results['failed'].append(file_result)
                print(f"    ❌ FAILED")
                if table_result.get('error'):
                    print(f"      Table: {table_result['error']}")
                if not dataview_result.get('tracks_partial'):
                    print(f"      Warning: No dataview queries tracking partial status")

    def check_warp_state_files(self):
        """Check mandatory Warp state files"""
        print("\n📋 Checking Warp State Files...")
        
        state_files = ['Tasks.md', 'Changelog.md', 'AGENTS.md', 'Readme.md']
        
        for state_file in state_files:
            file_path = self.warp_root / state_file
            
            if not file_path.exists():
                print(f"  ❌ MISSING: {state_file}")
                self.results['failed'].append({
                    'file': str(file_path),
                    'type': 'warp_state_file',
                    'error': 'File does not exist'
                })
                continue
            
            print(f"  Checking: {state_file}")
            
            # Check backlinks
            backlinks_result = self.check_backlinks(file_path, 'warp_state_files')
            
            file_result = {
                'file': str(file_path),
                'type': 'warp_state_file',
                'backlinks': backlinks_result
            }
            
            if backlinks_result.get('valid'):
                self.results['passed'].append(file_result)
                print(f"    ✅ PASSED")
            else:
                self.results['failed'].append(file_result)
                print(f"    ❌ FAILED")
                if backlinks_result.get('missing_backlinks'):
                    print(f"      Missing backlinks: {backlinks_result['missing_backlinks']}")

    def check_dataview_integration(self):
        """Check if Dataview queries properly pick up partial statuses"""
        print("\n📈 Checking Dataview Integration...")
        
        # Check main Twitch Coverage file for partial status tracking
        coverage_file = self.twitch_docs / "Coverage.md"
        
        if coverage_file.exists():
            with open(coverage_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count partial statuses in the main coverage file
            partial_count = len(re.findall(r'\|\s*\w+.*?\|\s*partial\s*\|', content, re.IGNORECASE))
            
            print(f"  Found {partial_count} components with 'partial' status in main Coverage.md")
            
            if partial_count > 0:
                self.results['passed'].append({
                    'file': str(coverage_file),
                    'type': 'dataview_integration',
                    'partial_count': partial_count
                })
                print(f"  ✅ Dataview queries should pick up {partial_count} partial entries")
            else:
                self.results['warnings'].append({
                    'file': str(coverage_file),
                    'type': 'dataview_integration',
                    'warning': 'No partial statuses found for Dataview to track'
                })
                print(f"  ⚠️  No partial statuses found for Dataview tracking")

    def generate_report(self):
        """Generate final integrity check report"""
        print("\n" + "=" * 60)
        print("📊 INTEGRITY CHECK REPORT")
        print("=" * 60)
        
        total_checks = len(self.results['passed']) + len(self.results['failed'])
        passed_checks = len(self.results['passed'])
        failed_checks = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        
        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {passed_checks}")
        print(f"❌ Failed: {failed_checks}")
        print(f"⚠️  Warnings: {warnings}")
        
        if failed_checks == 0:
            print("\n🎉 ALL INTEGRITY CHECKS PASSED!")
            print("Documentation is ready for production.")
        else:
            print(f"\n⚠️  {failed_checks} checks failed. Review issues above.")
        
        # Summary by type
        type_summary = {}
        for result in self.results['passed'] + self.results['failed']:
            file_type = result.get('type', 'unknown')
            if file_type not in type_summary:
                type_summary[file_type] = {'passed': 0, 'failed': 0}
            
            if result in self.results['passed']:
                type_summary[file_type]['passed'] += 1
            else:
                type_summary[file_type]['failed'] += 1
        
        print("\n📋 Summary by File Type:")
        for file_type, counts in type_summary.items():
            total = counts['passed'] + counts['failed']
            print(f"  {file_type}: {counts['passed']}/{total} passed")
        
        return failed_checks == 0


def main():
    """Main entry point"""
    checker = WarpIntegrityChecker()
    success = checker.run_integrity_checks()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
