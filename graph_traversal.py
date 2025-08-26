#!/usr/bin/env python3

import json
import os
import re
import csv
from collections import defaultdict, deque

# Define paths
ROOT_DIR = '/home/cinder/Documents/repos'
TWITCH_DOCS_DIR = os.path.join(ROOT_DIR, 'Twitch Docs')
REPOS_DOCS_DIR = os.path.join(ROOT_DIR, 'Repos Docs')
WARP_DIR = os.path.join(ROOT_DIR, 'Warp')

# Major domains as defined in Twitch Docs/Coverage.md
MAJOR_DOMAINS = [
    'chat',
    'video',
    'web',
    'commerce',
    'identity',
    'security',
    'content'
]

class GraphTraversal:
    def __init__(self):
        self.graph = defaultdict(list)
        self.components = set()
        self.major_domains = set(MAJOR_DOMAINS)
        self.core_components = set()  # On path between major domains
        self.peripheral_components = set()  # One hop from core
        self.disconnected_components = set()  # No path to core
        
    def build_graph_from_files(self):
        """Build the dependency graph from available files"""
        print("Building dependency graph...")
        
        # Try to use dependency matrix data if available
        dependency_matrix_path = os.path.join(TWITCH_DOCS_DIR, 'docs/architecture/dependency-matrix.json')
        dependencies_csv_path = os.path.join(TWITCH_DOCS_DIR, 'docs/architecture/dependencies.csv')
        
        # Add manually known connections from Changelog.md (for core domains)
        for domain in MAJOR_DOMAINS:
            self.components.add(domain)
        
        # Connect all major domains to each other (they're known to interact per documentation)
        for i, domain1 in enumerate(MAJOR_DOMAINS):
            for domain2 in MAJOR_DOMAINS[i+1:]:
                self.graph[domain1].append(domain2)
                self.graph[domain2].append(domain1)
        
        # Add subcomponents from Coverage.md
        coverage_path = os.path.join(TWITCH_DOCS_DIR, 'Coverage.md')
        if os.path.exists(coverage_path):
            self.parse_coverage_file(coverage_path)
        
        # Use Repository Coverage files
        for repo_dir in os.listdir(REPOS_DOCS_DIR):
            repo_coverage = os.path.join(REPOS_DOCS_DIR, repo_dir, 'Coverage.md')
            if os.path.exists(repo_coverage):
                self.parse_coverage_file(repo_coverage)
                
        # Parse Repos Docs/Index.md for repo connections
        index_path = os.path.join(REPOS_DOCS_DIR, 'Index.md')
        if os.path.exists(index_path):
            self.parse_index_file(index_path)
        
        print(f"Graph built with {len(self.components)} components and {sum(len(neighbors) for neighbors in self.graph.values())} connections")
    
    def parse_coverage_file(self, file_path):
        """Parse a Coverage.md file to extract components and their connections"""
        print(f"Parsing {file_path}...")
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract component table rows
        table_pattern = r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|'
        matches = re.findall(table_pattern, content)
        
        for match in matches:
            # Skip header rows
            if "Component" in match[0] or "---" in match[0]:
                continue
                
            component = match[0].strip()
            component_type = match[1].strip()
            source_path = match[2].strip()
            status = match[3].strip()
            
            # Skip noise components (dates, headers, file paths)
            if not self.is_valid_component(component):
                continue
                
            self.components.add(component)
            
            # Extract backlinks to find connections
            if len(match) >= 7 and match[6]:
                backlinks = re.findall(r'\[\[([^\]]+)\]\]', match[6])
                for backlink in backlinks:
                    # Skip non-component backlinks
                    if backlink in ['Index', 'Tasks', 'Coverage']:
                        continue
                    
                    # Clean up component names from backlinks
                    if backlink.startswith('Components/'):
                        backlink = backlink[len('Components/'):]
                        
                    if self.is_valid_component(backlink):
                        self.components.add(backlink)
                        self.graph[component].append(backlink)
                        self.graph[backlink].append(component)
            
            # Connect components to their domains based on path
            for domain in MAJOR_DOMAINS:
                if domain in source_path or (component_type == 'domain' and component == domain):
                    self.graph[component].append(domain)
                    self.graph[domain].append(component)
    
    def parse_index_file(self, file_path):
        """Parse the Index.md file to extract repository connections"""
        print(f"Parsing {file_path}...")
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Find mermaid flowchart sections
        mermaid_sections = re.findall(r'```mermaid\s*flowchart TD(.*?)```', content, re.DOTALL)
        if not mermaid_sections:
            mermaid_sections = re.findall(r'```mermaid\s*graph (.*?)```', content, re.DOTALL)
            
        for section in mermaid_sections:
            # Extract connections like "A --> B"
            connections = re.findall(r'([A-Za-z0-9_\-]+)\s*-->\s*([A-Za-z0-9_\-]+)', section)
            for source, target in connections:
                # Clean up component names
                source = self.clean_component_name(source)
                target = self.clean_component_name(target)
                
                self.components.add(source)
                self.components.add(target)
                self.graph[source].append(target)
                # Don't add reverse edge as this is a directed graph
    
    def clean_component_name(self, name):
        """Clean up component names from mermaid diagrams"""
        # Remove brackets or other special formatting
        return name.strip('[]')
    
    def is_valid_component(self, component):
        """Check if a component name is valid (not noise data)"""
        # Skip empty components
        if not component or component.isspace():
            return False
            
        # Skip date-like strings
        if re.match(r'^\d{4}-\d{2}-\d{2}', component):
            return False
            
        # Skip timestamp-like strings  
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:', component):
            return False
            
        # Skip file paths starting with src/
        if component.startswith('src/'):
            return False
            
        # Skip markdown headers
        if component.startswith('###'):
            return False
            
        # Skip obvious documentation strings
        if len(component) > 100:  # Very long strings are likely descriptions
            return False
            
        # Skip table headers
        if component in ['Component', 'Type', 'Source Path', 'Status', 'Last Scanned', 'Doc File', 'Backlinks']:
            return False
            
        # Valid component
        return True
    
    def compute_connectivity(self):
        """Compute connectivity and categorize components"""
        print("Computing connectivity...")
        
        # 1. Find paths between all major domains to identify core components
        for i, domain1 in enumerate(self.major_domains):
            for domain2 in list(self.major_domains)[i+1:]:
                paths = self.find_all_paths(domain1, domain2)
                for path in paths:
                    for component in path:
                        self.core_components.add(component)
        
        # 2. Find peripheral components (one hop from core)
        for core_component in self.core_components:
            for neighbor in self.graph[core_component]:
                if neighbor not in self.core_components:
                    self.peripheral_components.add(neighbor)
        
        # 3. Find disconnected components
        for component in self.components:
            if component not in self.core_components and component not in self.peripheral_components:
                self.disconnected_components.add(component)
        
        print(f"Core components: {len(self.core_components)}")
        print(f"Peripheral components: {len(self.peripheral_components)}")
        print(f"Disconnected components: {len(self.disconnected_components)}")
    
    def find_all_paths(self, start, end, max_paths=10):
        """Find paths between two components using BFS, limiting to max_paths"""
        visited = set()
        queue = deque([(start, [start])])
        paths = []
        
        while queue and len(paths) < max_paths:
            node, path = queue.popleft()
            
            if node == end:
                paths.append(path)
                continue
                
            if node in visited:
                continue
                
            visited.add(node)
            
            for neighbor in self.graph[node]:
                if neighbor not in path:  # Avoid cycles
                    queue.append((neighbor, path + [neighbor]))
        
        return paths
    
    def update_coverage_file(self, file_path):
        """Update Coverage.md with disconnected status"""
        print(f"Updating {file_path}...")
        
        with open(file_path, 'r') as f:
            content = f.readlines()
        
        updated_content = []
        for line in content:
            updated_line = line
            
            # Check if this is a component row in the table
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|')]
                if len(cells) >= 7 and cells[1] and cells[1] != "Component" and "---" not in cells[1]:
                    component_name = cells[1]
                    status_index = 4  # Status is in the 4th column (index 4 in split result)
                    
                    if component_name in self.disconnected_components:
                        # Replace status with "disconnected"
                        cells[status_index] = "disconnected"
                        updated_line = "|" + "|".join(cells[1:]) + "|\n"
            
            updated_content.append(updated_line)
        
        with open(file_path, 'w') as f:
            f.writelines(updated_content)
            
    def update_tasks_file(self):
        """Update Tasks.md with removal tasks for disconnected components"""
        print(f"Updating Tasks.md...")
        
        tasks_path = os.path.join(WARP_DIR, 'Tasks.md')
        
        with open(tasks_path, 'r') as f:
            content = f.readlines()
        
        # Find where to insert new tasks
        insert_index = 0
        for i, line in enumerate(content):
            if "## New Tasks" in line:
                insert_index = i + 1
                break
        
        # Create task entries for disconnected components
        new_tasks = ["## Disconnected Components for Removal\n\n"]
        for component in sorted(self.disconnected_components):
            new_tasks.append(f"- [ ] Review and remove disconnected component: {component} – see [[Coverage]]\n")
        
        new_tasks.append("\n")
        
        # Insert new tasks
        updated_content = content[:insert_index] + new_tasks + content[insert_index:]
        
        with open(tasks_path, 'w') as f:
            f.writelines(updated_content)
    
    def generate_report(self):
        """Generate a connectivity report"""
        report_path = os.path.join(WARP_DIR, 'connectivity_report.md')
        
        with open(report_path, 'w') as f:
            f.write("# Connectivity Analysis Report\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total Components: {len(self.components)}\n")
            f.write(f"- Core Components (on paths between major domains): {len(self.core_components)}\n")
            f.write(f"- Peripheral Components (one hop from core): {len(self.peripheral_components)}\n")
            f.write(f"- Disconnected Components (no path to core): {len(self.disconnected_components)}\n\n")
            
            f.write("## Major Domains\n\n")
            for domain in sorted(self.major_domains):
                f.write(f"- {domain}\n")
            f.write("\n")
            
            f.write("## Disconnected Components\n\n")
            for component in sorted(self.disconnected_components):
                f.write(f"- {component}\n")
            f.write("\n")
            
            f.write("## Core Components\n\n")
            for component in sorted(self.core_components):
                if component in self.major_domains:
                    f.write(f"- {component} (major domain)\n")
                else:
                    f.write(f"- {component}\n")
            f.write("\n")
            
            f.write("## Peripheral Components\n\n")
            for component in sorted(self.peripheral_components):
                f.write(f"- {component}\n")
            f.write("\n")
            
            f.write("## Connectivity Visualization\n\n")
            f.write("```\n")
            f.write("MAJOR DOMAINS <--> CORE COMPONENTS <--> PERIPHERAL COMPONENTS\n")
            f.write("\n")
            f.write("DISCONNECTED COMPONENTS (isolated from graph)\n")
            f.write("```\n\n")
            
            f.write("*Generated by graph_traversal.py*\n")
        
        print(f"Report generated at {report_path}")
    
    def run_analysis(self):
        """Run the complete analysis workflow"""
        self.build_graph_from_files()
        self.compute_connectivity()
        
        # Update Coverage.md
        coverage_path = os.path.join(TWITCH_DOCS_DIR, 'Coverage.md')
        self.update_coverage_file(coverage_path)
        
        # Update Tasks.md
        self.update_tasks_file()
        
        # Generate report
        self.generate_report()
        
        print("Analysis complete!")

if __name__ == "__main__":
    analyzer = GraphTraversal()
    analyzer.run_analysis()
