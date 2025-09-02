#!/usr/bin/env node
/**
 * Documentation Inventory Script for Surrentumlabs (Node.js Version)
 * 
 * This script recursively scans /home/cinder/Documents/repos/Surrentumlabs/** 
 * for markdown documentation files and generates a JSON cache with metadata.
 * 
 * Author: Created by Agent Mode for Surrentumlabs documentation management
 * Purpose: Inventory all documentation files and metadata across Surrentumlabs
 * Created: 2024-12-22
 * 
 * Target files:
 * - README.md, AGENTS.md, CHANGELOG.md, plan.md, toaster.md
 * - docs/README.md, *.md inside docs/ directory
 * 
 * For each file captures:
 * - absolute path, repository root, repo name, repo category,
 * - primary language(s), last-modified timestamp (git log -1 --format=%ct FILE)
 * 
 * Outputs to: .scripts/cache/docs_index.json
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync, spawn } = require('child_process');
const { promisify } = require('util');

// Configuration
const BASE_PATH = '/home/cinder/Documents/repos/Surrentumlabs';
const OUTPUT_DIR = '.scripts/cache';
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'docs_index_node.json');

const TARGET_FILES = new Set([
    'README.md',
    'AGENTS.md', 
    'CHANGELOG.md',
    'plan.md',
    'toaster.md'
]);

const DOCS_PATTERNS = [
    'docs/README.md',
    'docs/*.md'
];

/**
 * Get git last modified timestamp for a file
 */
async function getGitLastModified(filePath) {
    try {
        const repoDir = path.dirname(filePath);
        const timestamp = execSync(
            `git log -1 --format=%ct "${filePath}"`,
            { cwd: repoDir, encoding: 'utf8' }
        ).trim();
        return parseInt(timestamp) || null;
    } catch (error) {
        // Fallback to file system timestamp
        try {
            const stats = await fs.stat(filePath);
            return Math.floor(stats.mtime.getTime() / 1000);
        } catch (fallbackError) {
            return null;
        }
    }
}

/**
 * Determine repository category based on parent directory
 */
function determineRepoCategory(repoPath) {
    const parentDir = path.basename(path.dirname(repoPath));
    
    const categoryMapping = {
        'Monorepos': 'Monorepo',
        'Rust Component Repos': 'Rust Component',
        'Typescript Component Repos': 'TypeScript Component',
        'Other': 'Other',
        'whiply_project': 'Other'
    };
    
    return categoryMapping[parentDir] || 'Other';
}

/**
 * Detect primary programming languages in a repository
 */
async function detectPrimaryLanguages(repoPath) {
    const languages = new Set();
    
    const languageIndicators = {
        'Rust': ['Cargo.toml', 'Cargo.lock', 'src/main.rs', 'src/lib.rs'],
        'TypeScript': ['package.json', 'tsconfig.json'],
        'JavaScript': ['package.json'],
        'Python': ['requirements.txt', 'setup.py', 'pyproject.toml'],
        'Go': ['go.mod', 'go.sum'],
        'Java': ['pom.xml', 'build.gradle'],
        'C++': ['CMakeLists.txt', 'Makefile'],
        'C': ['Makefile']
    };
    
    for (const [lang, indicators] of Object.entries(languageIndicators)) {
        for (const indicator of indicators) {
            if (indicator.includes('*')) {
                // Handle glob patterns
                const extension = indicator.replace('*', '');
                try {
                    const files = await fs.readdir(repoPath);
                    if (files.some(file => file.endsWith(extension))) {
                        languages.add(lang);
                        break;
                    }
                } catch (error) {
                    // Ignore read errors
                }
            } else {
                // Handle exact file matches
                try {
                    await fs.access(path.join(repoPath, indicator));
                    languages.add(lang);
                    break;
                } catch (error) {
                    // File doesn't exist, continue
                }
            }
        }
    }
    
    // Special handling for TypeScript/JavaScript
    if (languages.has('TypeScript')) {
        languages.add('JavaScript');
    }
    
    // If no languages detected, default to Markdown
    if (languages.size === 0) {
        languages.add('Markdown');
    }
    
    return Array.from(languages);
}

/**
 * Find repository root by looking for .git directory
 */
async function findRepositoryRoot(filePath) {
    let currentPath = path.dirname(filePath);
    
    while (currentPath !== '/') {
        try {
            await fs.access(path.join(currentPath, '.git'));
            return currentPath;
        } catch (error) {
            currentPath = path.dirname(currentPath);
        }
    }
    
    // If no .git found, assume the directory of the file is repo root
    return path.dirname(filePath);
}

/**
 * Recursively walk directory and find matching files
 */
async function* walkDirectory(dir) {
    try {
        const entries = await fs.readdir(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory()) {
                // Skip .git directories
                if (entry.name !== '.git') {
                    yield* walkDirectory(fullPath);
                }
            } else if (entry.isFile() && entry.name.endsWith('.md')) {
                yield fullPath;
            }
        }
    } catch (error) {
        // Ignore permission errors and continue
        console.error(`Error accessing ${dir}: ${error.message}`);
    }
}

/**
 * Check if file should be included based on target patterns
 */
function shouldIncludeFile(filePath) {
    const filename = path.basename(filePath);
    
    // Check exact filename matches
    if (TARGET_FILES.has(filename)) {
        return true;
    }
    
    // Check docs directory patterns
    if (filePath.includes('/docs/') && filename.endsWith('.md')) {
        return true;
    }
    
    return false;
}

/**
 * Process a single file and extract metadata
 */
async function processFile(filePath) {
    try {
        const repoRoot = await findRepositoryRoot(filePath);
        const repoName = path.basename(repoRoot);
        const repoCategory = determineRepoCategory(repoRoot);
        const primaryLanguages = await detectPrimaryLanguages(repoRoot);
        const lastModified = await getGitLastModified(filePath);
        const relativePath = path.relative(repoRoot, filePath);
        
        const docInfo = {
            absolute_path: filePath,
            repository_root: repoRoot,
            repo_name: repoName,
            repo_category: repoCategory,
            primary_languages: primaryLanguages,
            last_modified_timestamp: lastModified,
            last_modified_date: lastModified ? new Date(lastModified * 1000).toISOString() : null,
            filename: path.basename(filePath),
            relative_path: relativePath
        };
        
        console.log(`Found: ${filePath}`);
        return docInfo;
    } catch (error) {
        console.error(`Error processing ${filePath}: ${error.message}`);
        return null;
    }
}

/**
 * Generate summary statistics
 */
function generateStatistics(docsInventory) {
    const totalFiles = docsInventory.length;
    const repositoriesFound = new Set(docsInventory.map(doc => doc.repo_name)).size;
    
    const categories = {};
    const languages = {};
    
    for (const doc of docsInventory) {
        // Count by category
        categories[doc.repo_category] = (categories[doc.repo_category] || 0) + 1;
        
        // Count by languages
        for (const lang of doc.primary_languages) {
            languages[lang] = (languages[lang] || 0) + 1;
        }
    }
    
    return {
        totalFiles,
        repositoriesFound,
        categories,
        languages
    };
}

/**
 * Main function
 */
async function main() {
    console.log('Starting documentation inventory scan (Node.js version)');
    console.log(`Base path: ${BASE_PATH}`);
    console.log(`Target files: ${Array.from(TARGET_FILES).join(', ')}`);
    console.log('Target docs patterns: docs/README.md, docs/*.md');
    console.log('-'.repeat(60));
    
    // Check if base path exists
    try {
        await fs.access(BASE_PATH);
    } catch (error) {
        console.error(`ERROR: Base path does not exist: ${BASE_PATH}`);
        process.exit(1);
    }
    
    // Ensure output directory exists
    await fs.mkdir(OUTPUT_DIR, { recursive: true });
    
    const docsInventory = [];
    
    // Process all markdown files
    for await (const filePath of walkDirectory(BASE_PATH)) {
        if (shouldIncludeFile(filePath)) {
            const docInfo = await processFile(filePath);
            if (docInfo) {
                docsInventory.push(docInfo);
            }
        }
    }
    
    // Sort by repository name and filename
    docsInventory.sort((a, b) => {
        const repoCompare = a.repo_name.localeCompare(b.repo_name);
        return repoCompare !== 0 ? repoCompare : a.filename.localeCompare(b.filename);
    });
    
    // Generate statistics
    const stats = generateStatistics(docsInventory);
    
    // Create output structure
    const output = {
        metadata: {
            scan_timestamp: new Date().toISOString(),
            base_path: BASE_PATH,
            total_files: stats.totalFiles,
            repositories_found: stats.repositoriesFound,
            categories: stats.categories,
            languages: stats.languages,
            target_files: Array.from(TARGET_FILES),
            docs_patterns: DOCS_PATTERNS
        },
        documentation_files: docsInventory
    };
    
    // Write JSON output
    await fs.writeFile(OUTPUT_FILE, JSON.stringify(output, null, 2), 'utf8');
    
    console.log('-'.repeat(60));
    console.log('Scan complete (Node.js version)!');
    console.log(`Total files found: ${stats.totalFiles}`);
    console.log(`Repositories scanned: ${stats.repositoriesFound}`);
    console.log(`Categories: ${Object.entries(stats.categories).map(([k, v]) => `${k}(${v})`).join(', ')}`);
    console.log(`Primary languages: ${Object.entries(stats.languages).map(([k, v]) => `${k}(${v})`).join(', ')}`);
    console.log(`Results written to: ${OUTPUT_FILE}`);
}

// Run the main function
if (require.main === module) {
    main().catch(error => {
        console.error('Error:', error);
        process.exit(1);
    });
}

module.exports = {
    main,
    processFile,
    detectPrimaryLanguages,
    findRepositoryRoot,
    determineRepoCategory
};
