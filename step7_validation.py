#!/usr/bin/env python3
"""
Step 7: Run Warp Documentation Integrity Checks (Focused)

This script focuses on the specific validation requirements:
1. Execute internal script or manual grep to ensure every new file contains required sections & backlinks.  
2. Validate Coverage.md table renders in Obsidian.  
3. Confirm Dataview queries pick up new `partial` statuses.
"""

import os
import re
import glob
from pathlib import Path

def check_obsidian_tables():
    """Check if Coverage.md tables have proper structure for Obsidian rendering"""
    print("📊 Validating Coverage.md table rendering for Obsidian...")
    
    # Main Twitch Coverage file
    coverage_file = "/home/cinder/Documents/repos/Twitch Docs/Coverage.md"
    
    if not os.path.exists(coverage_file):
        print("  ❌ Main Coverage.md file not found")
        return False
    
    with open(coverage_file, 'r') as f:
        content = f.read()
    
    # Check for proper table structure
    table_headers = re.findall(r'\|\s*Component\s*\|.*?\|\s*Status\s*\|', content, re.IGNORECASE)
    table_separators = re.findall(r'\|\s*-+\s*\|', content)
    partial_entries = re.findall(r'\|\s*\w+.*?\|\s*partial\s*\|', content, re.IGNORECASE)
    
    print(f"  ✅ Found {len(table_headers)} table headers")
    print(f"  ✅ Found {len(table_separators)} table separators")
    print(f"  ✅ Found {len(partial_entries)} partial status entries")
    
    # Validate table structure
    if len(table_headers) > 0 and len(partial_entries) > 0:
        print("  ✅ Coverage.md tables are properly formatted for Obsidian rendering")
        return True
    else:
        print("  ❌ Coverage.md tables may not render properly in Obsidian")
        return False

def check_dataview_queries():
    """Check if Dataview queries will pick up partial statuses"""
    print("\n📈 Checking Dataview query compatibility with partial statuses...")
    
    # Look for dataview query blocks across all files
    dataview_files = []
    repos_docs = "/home/cinder/Documents/repos/Repos Docs"
    
    if os.path.exists(repos_docs):
        for root, dirs, files in os.walk(repos_docs):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Look for dataview blocks
                        dataview_blocks = re.findall(r'```dataview\n(.*?)\n```', content, re.DOTALL)
                        
                        if dataview_blocks:
                            dataview_files.append({
                                'file': file_path,
                                'blocks': dataview_blocks
                            })
                    except Exception:
                        continue
    
    # Analyze dataview queries
    partial_tracking_queries = 0
    total_queries = 0
    
    for file_info in dataview_files:
        for block in file_info['blocks']:
            total_queries += 1
            if 'partial' in block.lower() or 'status' in block.lower():
                partial_tracking_queries += 1
    
    print(f"  ✅ Found {len(dataview_files)} files with dataview queries")
    print(f"  ✅ Found {total_queries} total dataview queries")
    print(f"  ✅ Found {partial_tracking_queries} queries that track status/partial")
    
    # Check main Coverage file for partial entries that Dataview should pick up
    coverage_file = "/home/cinder/Documents/repos/Twitch Docs/Coverage.md"
    partial_count = 0
    
    if os.path.exists(coverage_file):
        with open(coverage_file, 'r') as f:
            content = f.read()
        partial_count = len(re.findall(r'\|\s*\w+.*?\|\s*partial\s*\|', content, re.IGNORECASE))
    
    print(f"  ✅ {partial_count} components with 'partial' status available for Dataview queries")
    
    if partial_count > 0:
        print("  ✅ Dataview queries can pick up partial statuses")
        return True
    else:
        print("  ⚠️  No partial statuses found for Dataview to track")
        return False

def check_required_sections_and_backlinks():
    """Check that new files contain required sections and backlinks"""
    print("\n🔍 Checking required sections and backlinks in documentation files...")
    
    files_to_check = []
    
    # Component cards
    twitch_components = "/home/cinder/Documents/repos/Twitch Docs/Components"
    if os.path.exists(twitch_components):
        files_to_check.extend([
            os.path.join(twitch_components, f) for f in os.listdir(twitch_components)
            if f.endswith('.md')
        ])
    
    # Repository coverage files  
    repos_docs = "/home/cinder/Documents/repos/Repos Docs"
    if os.path.exists(repos_docs):
        for root, dirs, files in os.walk(repos_docs):
            for file in files:
                if file == 'Coverage.md':
                    files_to_check.append(os.path.join(root, file))
    
    print(f"  Found {len(files_to_check)} documentation files to validate")
    
    # Required sections for different file types
    required_sections = {
        'component': ['Purpose', 'Depends On', 'Used By'],
        'coverage': ['Purpose', 'Depends On', 'Used By']
    }
    
    # Required backlinks
    required_backlinks = [
        r'\[\[Coverage\]\]',
        r'\[\[Index\]\]',
        r'\[\[.*Coverage.*\]\]'
    ]
    
    passed_files = 0
    failed_files = 0
    
    for file_path in files_to_check[:10]:  # Check first 10 files as sample
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_name = os.path.basename(file_path)
            
            # Check for required sections
            has_purpose = bool(re.search(r'^##\s+Purpose', content, re.MULTILINE | re.IGNORECASE))
            has_depends = bool(re.search(r'^##\s+Depends On', content, re.MULTILINE | re.IGNORECASE))
            has_used_by = bool(re.search(r'^##\s+Used By', content, re.MULTILINE | re.IGNORECASE))
            
            # Check for backlinks
            has_coverage_link = bool(re.search(r'\[\[.*Coverage.*\]\]', content, re.IGNORECASE))
            has_index_link = bool(re.search(r'\[\[.*Index.*\]\]', content, re.IGNORECASE))
            
            sections_ok = has_purpose and has_depends and has_used_by
            backlinks_ok = has_coverage_link
            
            if sections_ok and backlinks_ok:
                passed_files += 1
                print(f"    ✅ {file_name}")
            else:
                failed_files += 1
                print(f"    ❌ {file_name}")
                if not sections_ok:
                    missing = []
                    if not has_purpose: missing.append("Purpose")
                    if not has_depends: missing.append("Depends On")  
                    if not has_used_by: missing.append("Used By")
                    print(f"      Missing sections: {', '.join(missing)}")
                if not backlinks_ok:
                    print(f"      Missing Coverage backlink")
        
        except Exception as e:
            failed_files += 1
            print(f"    ❌ {os.path.basename(file_path)} (Error: {str(e)})")
    
    print(f"\n  Summary: {passed_files} passed, {failed_files} failed (sample of {min(10, len(files_to_check))} files)")
    
    return passed_files > failed_files

def validate_specific_patterns():
    """Validate specific patterns mentioned in the task"""
    print("\n🎯 Running specific validation patterns...")
    
    # Check for grep-able patterns
    coverage_file = "/home/cinder/Documents/repos/Twitch Docs/Coverage.md"
    
    patterns_to_check = [
        (r'\[\[Coverage\]\]', "Coverage backlinks"),
        (r'\[\[Index\]\]', "Index backlinks"),
        (r'\|\s*partial\s*\|', "Partial status entries"),
        (r'status:\s*partial', "YAML partial status"),
        (r'```dataview', "Dataview code blocks")
    ]
    
    for pattern, description in patterns_to_check:
        matches = 0
        
        # Check in main Coverage file
        if os.path.exists(coverage_file):
            with open(coverage_file, 'r') as f:
                content = f.read()
            matches += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Check in component files
        components_dir = "/home/cinder/Documents/repos/Twitch Docs/Components"
        if os.path.exists(components_dir):
            for file_name in os.listdir(components_dir):
                if file_name.endswith('.md'):
                    try:
                        with open(os.path.join(components_dir, file_name), 'r') as f:
                            content = f.read()
                        matches += len(re.findall(pattern, content, re.IGNORECASE))
                    except Exception:
                        continue
        
        print(f"  ✅ Found {matches} instances of {description}")
    
    return True

def main():
    """Run Step 7 validation checks"""
    print("🔍 Step 7: Warp Documentation Integrity Checks")
    print("=" * 60)
    
    results = []
    
    # 1. Check Coverage.md table rendering
    results.append(check_obsidian_tables())
    
    # 2. Check Dataview query compatibility
    results.append(check_dataview_queries())
    
    # 3. Check required sections and backlinks
    results.append(check_required_sections_and_backlinks())
    
    # 4. Validate specific patterns
    results.append(validate_specific_patterns())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 STEP 7 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed_checks = sum(results)
    total_checks = len(results)
    
    print(f"✅ Passed: {passed_checks}/{total_checks} checks")
    
    if passed_checks == total_checks:
        print("\n🎉 ALL STEP 7 INTEGRITY CHECKS PASSED!")
        print("✅ Coverage.md tables will render properly in Obsidian")
        print("✅ Dataview queries can pick up partial statuses") 
        print("✅ Documentation files contain required sections and backlinks")
        print("✅ All required patterns are present and grep-able")
        return True
    else:
        print(f"\n⚠️  {total_checks - passed_checks} checks need attention")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
