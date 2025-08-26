#!/usr/bin/env python3
"""
Generate comprehensive Coverage.md files for all repositories
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def get_repo_list():
    """Get list of all repositories"""
    repos = []
    
    # Rust repositories
    rust_base = "/home/cinder/Documents/repos/Surrentumlabs/Rust Component Repos"
    for item in os.listdir(rust_base):
        repo_path = os.path.join(rust_base, item)
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, ".git")):
            repos.append({
                'name': item,
                'path': repo_path,
                'language': 'rust',
                'type': 'rust-repo'
            })
    
    # TypeScript repositories  
    ts_base = "/home/cinder/Documents/repos/Surrentumlabs/Typescript Component Repos"
    for item in os.listdir(ts_base):
        repo_path = os.path.join(ts_base, item)
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, ".git")):
            repos.append({
                'name': item,
                'path': repo_path,
                'language': 'typescript',
                'type': 'ts-repo'
            })
    
    return repos

def get_repo_metadata(repo_info):
    """Extract metadata from repository"""
    repo_path = repo_info['path']
    metadata = {
        'name': repo_info['name'],
        'language': repo_info['language'],
        'version': '0.0.0',
        'description': '',
        'dependencies': [],
        'components': []
    }
    
    if repo_info['language'] == 'rust':
        cargo_toml = os.path.join(repo_path, 'Cargo.toml')
        if os.path.exists(cargo_toml):
            try:
                with open(cargo_toml, 'r') as f:
                    content = f.read()
                    # Simple parsing for key fields
                    for line in content.split('\n'):
                        if line.startswith('name = '):
                            metadata['name'] = line.split('=')[1].strip().strip('"')
                        elif line.startswith('version = '):
                            metadata['version'] = line.split('=')[1].strip().strip('"')
                        elif line.startswith('description = '):
                            metadata['description'] = line.split('=')[1].strip().strip('"')
            except:
                pass
        
        # Find Rust source files
        src_dir = os.path.join(repo_path, 'src')
        if os.path.exists(src_dir):
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.rs'):
                        rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                        metadata['components'].append({
                            'name': file.replace('.rs', ''),
                            'type': 'module' if file != 'main.rs' and not root.endswith('/bin') else 'binary',
                            'path': rel_path
                        })
    
    elif repo_info['language'] == 'typescript':
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    metadata['name'] = data.get('name', repo_info['name'])
                    metadata['version'] = data.get('version', '0.0.0')
                    metadata['description'] = data.get('description', '')
            except:
                pass
        
        # Find JavaScript/TypeScript source files
        src_dir = os.path.join(repo_path, 'src')
        if os.path.exists(src_dir):
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file.endswith(('.js', '.ts', '.jsx', '.tsx')):
                        rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                        metadata['components'].append({
                            'name': file.split('.')[0],
                            'type': 'module',
                            'path': rel_path
                        })
    
    return metadata

def generate_coverage_md(repo_info, metadata):
    """Generate comprehensive Coverage.md content"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Determine tags based on language and repo characteristics
    tags = [repo_info['language']]
    if repo_info['language'] == 'rust':
        tags.extend(['crate'])
        if any('bin' in c['path'] for c in metadata['components']):
            tags.append('binary')
        if 'lib' in [c['name'] for c in metadata['components']]:
            tags.append('library')
    else:
        tags.extend(['package'])
    
    # Add domain-specific tags based on repo name
    if 'chat' in repo_info['name'].lower():
        tags.append('chat')
    if 'pubsub' in repo_info['name'].lower():
        tags.append('pubsub')
    if 'gui' in repo_info['name'].lower():
        tags.append('gui')
    if 'bot' in repo_info['name'].lower():
        tags.append('bot')
    if 'parser' in repo_info['name'].lower():
        tags.append('parser')
    
    # Generate YAML header
    yaml_header = f"""---
status: todo
source_path: {repo_info['path']}
last_scanned: {timestamp}
tags: 
{chr(10).join(f'  - {tag}' for tag in tags)}
repository_name: {repo_info['name']}
language: {repo_info['language']}
package_manager: {'cargo' if repo_info['language'] == 'rust' else 'npm'}
version: {metadata['version']}
---"""

    # Generate purpose section
    purpose = f"{metadata['description'] or 'Repository for ' + repo_info['name'].replace('-', ' ').title()}"
    
    # Generate components table
    components_table = """| Component | Type | Source Path | Status | Last Scanned | Description |
|-----------|------|-------------|--------|--------------|-------------|"""
    
    for comp in metadata['components'][:10]:  # Limit to first 10 components
        components_table += f"\n| {comp['name']} | {comp['type']} | {comp['path']} | todo | {timestamp[:10]} | TODO: Add description |"
    
    if len(metadata['components']) > 10:
        components_table += f"\n| ... | ... | ... | todo | {timestamp[:10]} | Additional {len(metadata['components']) - 10} components |"

    # Generate full Coverage.md
    content = f"""{yaml_header}

# {repo_info['name'].replace('-', ' ').title()} - Repository Coverage

## Purpose

{purpose}

## Key Components

### Core Components

{components_table}

```dataview
task
where contains(file.path, "{repo_info['name']}") and status != "done"
```

## Interfaces

### Public API
- TODO: Document public interfaces and APIs

### External Dependencies
- TODO: Document external dependencies

## Depends On

### Runtime Dependencies
- TODO: Document runtime dependencies

### Development Tools
- TODO: Document development dependencies

## Used By

- TODO: Document downstream consumers and users

## Notes

### Architecture Highlights
- TODO: Document key architectural decisions

### Development Workflow
- TODO: Document development and build processes

### Quality Assurance
- TODO: Document testing and quality measures

## Backlinks

- [[Index]] - Repository documentation index
- [[../{repo_info['language']}-components/Coverage]] - {repo_info['language'].title()} components category coverage
- [[../Warp/Tasks]] - Related documentation tasks

---

*Last updated: {timestamp}*  
*Repository: {repo_info['path']}*"""

    return content

def create_coverage_file(repo_info, content):
    """Create or update Coverage.md file"""
    docs_path = f"/home/cinder/Documents/repos/Repos Docs/{repo_info['name']}"
    os.makedirs(docs_path, exist_ok=True)
    
    coverage_file = os.path.join(docs_path, "Coverage.md")
    
    with open(coverage_file, 'w') as f:
        f.write(content)
    
    return coverage_file

def main():
    """Main execution"""
    repos = get_repo_list()
    created_files = []
    
    print(f"Processing {len(repos)} repositories...")
    
    for repo_info in repos:
        print(f"Processing {repo_info['name']}...")
        
        # Skip already detailed repositories
        if repo_info['name'] in ['chat-parser-rust', 'pubsub-typescript-client', 'pubsub-rust']:
            print(f"  Skipping {repo_info['name']} - already detailed")
            continue
            
        try:
            metadata = get_repo_metadata(repo_info)
            content = generate_coverage_md(repo_info, metadata)
            coverage_file = create_coverage_file(repo_info, content)
            created_files.append(coverage_file)
            print(f"  Created: {coverage_file}")
        except Exception as e:
            print(f"  Error processing {repo_info['name']}: {e}")
    
    print(f"\nGenerated {len(created_files)} Coverage.md files")
    return created_files

if __name__ == '__main__':
    main()
