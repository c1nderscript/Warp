#!/usr/bin/env node
/**
 * DataviewJS Query Validation Script
 * 
 * This script tests the basic functionality that would be used by Obsidian DataviewJS queries
 * to ensure the JSON cache loads correctly and queries work without errors.
 * 
 * Author: AI Agent (Step 6 validation)
 * Purpose: Validate DataviewJS query logic before committing
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Testing DataviewJS query compatibility...');

try {
    // Test 1: Load documentation cache
    const docsPath = '.scripts/cache/docs_index.json';
    console.log(`📁 Loading documentation cache: ${docsPath}`);
    
    if (!fs.existsSync(docsPath)) {
        throw new Error(`Documentation cache not found at ${docsPath}`);
    }
    
    const jsonData = JSON.parse(fs.readFileSync(docsPath, 'utf8'));
    console.log(`✅ Loaded ${jsonData.documentation_files?.length || 0} documentation files`);
    
    // Test 2: Test basic filtering (Monorepo files)
    const monorepoFiles = jsonData.documentation_files?.filter(file => 
        file.repo_category === 'Monorepo'
    ) || [];
    console.log(`📊 Found ${monorepoFiles.length} Monorepo files`);
    
    // Test 3: Test language filtering (Rust files)  
    const rustFiles = jsonData.documentation_files?.filter(file => 
        file.primary_languages?.includes('Rust')
    ) || [];
    console.log(`🦀 Found ${rustFiles.length} Rust-related files`);
    
    // Test 4: Test date parsing and sorting
    const recentFiles = jsonData.documentation_files
        ?.sort((a, b) => (b.last_modified_timestamp || 0) - (a.last_modified_timestamp || 0))
        ?.slice(0, 5) || [];
    
    console.log('\n📅 5 Most recently modified files:');
    recentFiles.forEach((file, index) => {
        const date = file.last_modified_timestamp 
            ? new Date(file.last_modified_timestamp * 1000).toLocaleDateString()
            : 'Unknown';
        console.log(`  ${index + 1}. ${file.filename} in ${file.repo_name} (${date})`);
    });
    
    // Test 5: Test repository inventory (if exists)
    const inventoryPath = 'surrentumlabs_repo_inventory.json';
    if (fs.existsSync(inventoryPath)) {
        const inventoryData = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));
        console.log(`\n📋 Repository inventory loaded with ${inventoryData.repositories?.length || 0} repositories`);
    } else {
        console.log(`\n⚠️  Repository inventory not found at ${inventoryPath} (optional)`);
    }
    
    // Test 6: Simulate table data creation
    const testTableData = monorepoFiles.slice(0, 3).map(file => [
        file.filename,
        file.repo_name,
        file.relative_path,
        file.last_modified_timestamp 
            ? new Date(file.last_modified_timestamp * 1000).toLocaleDateString()
            : 'Unknown'
    ]);
    
    console.log('\n🔬 Sample table data structure:');
    console.log('Headers: ["File", "Repo", "Path", "Last Modified"]');
    testTableData.forEach((row, index) => {
        console.log(`Row ${index + 1}: [${row.map(cell => `"${cell}"`).join(', ')}]`);
    });
    
    console.log('\n✅ All DataviewJS compatibility tests passed!');
    console.log('🎉 Documentation-Homepage.md queries should render without errors.');
    
} catch (error) {
    console.error('\n❌ DataviewJS compatibility test failed:');
    console.error(error.message);
    
    if (error.name === 'SyntaxError') {
        console.error('💡 This indicates a JSON parsing error. Check the cache file format.');
    }
    
    process.exit(1);
}
