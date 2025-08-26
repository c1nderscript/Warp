#!/usr/bin/env python3

"""
Script to complete the categorization of all Twitch components in Coverage.md
Based on traffic volume, production usage, infrastructure tags, and dependency matrix analysis.
"""

# Complete categorization mapping based on analysis
categorization = {
    # Essential: Core domains, high-connectivity services, revenue-critical, user-facing
    'Essential': {
        'chat', 'commerce', 'identity', 'security', 'video', 'web',
        'common', 'core-ui', 'eventbus', 'spade', 'hygienic', 'twilight',
        'edge', 'stats', 'subs', 'player-core', 'transcoder', 'websocket-edge',
        'security-cop', 'video-coreservices', 'video-monitoring'
    },
    
    # Semi-Essential: DevOps, CI/CD, monitoring, developer tools, supporting infrastructure
    'Semi-Essential': {
        'content', 'admin-services', 'devtools', 'devinfra-chef', 'qa', 'qe',
        'release', 'systems', 'systems-terraform', 'terraform-modules',
        'puppet-modules', 'core-config-packages', 'twitch-cdk', 'Xarth-Grafana',
        'neteng', 'nre', 'dcops', 'vidops', 'infosec', 'privacy', 'slackbots',
        'devhub', 'devrel', 'sdk', 'video-puppet', 'video-puppet-thirdparty',
        'video-tools', 'abuse', 'safety', 'safety-ml', 'ads', 'archive',
        'availability', 'desktop', 'extensions', 'growth', 'i18n', 'insights',
        'marketing', 'ml', 'mods', 'modtools', 'points', 'revenue', 'awsi',
        'beefcake', 'businessviewcount', 'cb', 'ce-analytics', 'cplat',
        'creative', 'creative-services', 'creator-collab', 'cs', 'd8a',
        'discover-watch', 'discovery', 'dp', 'dta', 'dumbo', 'dxdata', 'ear',
        'elixir', 'esports', 'esports-exp', 'event-engineering', 'feeds',
        'flexo', 'foundation', 'gds', 'gidev', 'hedgehog', 'host', 'ids',
        'igdb', 'lifecycle', 'live', 'liverecs', 'mdas', 'music', 'octarine',
        'samus', 'spotlight', 'sse', 'twig', 'twitch', 'twitch-apps',
        'twitch-events', 'vapour', 'viridian', 'vod', 'vodsvc', 'amzn'
    },
    
    # Non-Essential: Individual contributor dirs, team dirs, legacy, experiments
    'Non-Essential': {
        '3rdparty', 'CPE-Chef', 'CPE-Dev', 'CPE-Ops', 'Design', 'JChang',
        'Twitch-IT', 'andaries', 'astith', 'benherr', 'bobbcarp', 'bryachar',
        'danielnf', 'itsupport', 'jukenned', 'kdkly', 'kerbin', 'kevinbacon',
        'kevipike', 'kkona', 'marqshee', 'mmdixon', 'mpaldhe', 'mponorof',
        'ncaspar', 'product', 'rhys', 'royberg', 'rps', 'rrieblin', 'rwjblue',
        'sean', 'timotyenorg', 'vidhurv', 'yilenpan', 'CurseBackend',
        'FETakehome', 'bootcamp', 'graveyard', 'gsoc', 'blade-legacy',
        'stats-deprecated', 'flexotest'
    }
}

def get_category(component_name):
    """Get the category for a component based on our analysis"""
    for category, components in categorization.items():
        if component_name in components:
            return category
    # Default to Semi-Essential for unclassified services
    return 'Semi-Essential'

def main():
    """Read the Coverage.md file and add categories to all components"""
    
    coverage_path = '/home/cinder/Documents/repos/Twitch Docs/Coverage.md'
    
    with open(coverage_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        # Check if this is a component line in the table that needs a category
        if (line.startswith('|') and '|service|' in line or 
            line.startswith('|') and '|infra|' in line or
            line.startswith('|') and '|team|' in line or
            line.startswith('|') and '|folder|' in line or
            line.startswith('| ') and ' | domain |' in line or
            line.startswith('| ') and ' | component |' in line):
            
            # Skip lines that already have categories (end with a category)
            if (line.endswith('|Essential|') or 
                line.endswith('|Semi-Essential|') or 
                line.endswith('|Non-Essential|') or
                line.endswith('| Essential |') or
                line.endswith('| Semi-Essential |') or
                line.endswith('| Non-Essential |')):
                updated_lines.append(line)
                continue
                
            # Skip lines that end with empty category column
            if line.endswith('|||') or line.endswith('||'):
                # Extract component name
                parts = line.split('|')
                if len(parts) >= 2:
                    component_name = parts[1].strip() if not line.startswith('| ') else parts[1].strip()
                    category = get_category(component_name)
                    
                    # Replace the empty category with the determined category
                    if line.endswith('|||'):
                        updated_line = line[:-2] + f'{category}|'
                    elif line.endswith('||'):
                        updated_line = line[:-1] + f'{category}|'
                    else:
                        updated_line = line + f'|{category}|'
                    
                    updated_lines.append(updated_line)
                    continue
            
            # Handle lines without category column at all
            parts = line.split('|')
            if len(parts) >= 2:
                component_name = parts[1].strip() if not line.startswith('| ') else parts[1].strip()
                category = get_category(component_name)
                
                # Add category column
                updated_line = line.rstrip('|') + f'|{category}|'
                updated_lines.append(updated_line)
                continue
        
        updated_lines.append(line)
    
    # Write back the updated content
    updated_content = '\n'.join(updated_lines)
    
    with open(coverage_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Successfully updated Coverage.md with component categories")
    
    # Print summary statistics
    essential_count = len(categorization['Essential'])
    semi_essential_count = len(categorization['Semi-Essential'])
    non_essential_count = len(categorization['Non-Essential'])
    total_count = essential_count + semi_essential_count + non_essential_count
    
    print(f"\nCategorization Summary:")
    print(f"🔴 Essential: {essential_count} components ({essential_count/total_count*100:.1f}%)")
    print(f"🟡 Semi-Essential: {semi_essential_count} components ({semi_essential_count/total_count*100:.1f}%)")
    print(f"🟢 Non-Essential: {non_essential_count} components ({non_essential_count/total_count*100:.1f}%)")
    print(f"📊 Total: {total_count} components categorized")

if __name__ == '__main__':
    main()
