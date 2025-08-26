use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};
use serde_json;
use toml;

#[derive(Debug, Serialize, Deserialize)]
struct CargoPackage {
    name: String,
    version: String,
    edition: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct CargoToml {
    package: Option<CargoPackage>,
    dependencies: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Debug, Serialize, Deserialize)]
struct PackageJson {
    name: Option<String>,
    version: Option<String>,
    dependencies: Option<HashMap<String, String>>,
    #[serde(rename = "devDependencies")]
    dev_dependencies: Option<HashMap<String, String>>,
}

#[derive(Debug, Serialize)]
struct RepoMetadata {
    name: String,
    repo_type: String,
    path: String,
    package_name: Option<String>,
    version: Option<String>,
    edition: Option<String>,
    dependencies: Option<HashMap<String, serde_json::Value>>,
    dev_dependencies: Option<HashMap<String, String>>,
    parse_error: Option<String>,
}

#[derive(Debug, Serialize)]
struct InventoryReport {
    timestamp: String,
    rust_repos: Vec<RepoMetadata>,
    typescript_repos: Vec<RepoMetadata>,
    summary: HashMap<String, usize>,
    errors: Vec<String>,
}

fn main() {
    let mut inventory = InventoryReport {
        timestamp: chrono::Utc::now().to_rfc3339(),
        rust_repos: Vec::new(),
        typescript_repos: Vec::new(),
        summary: HashMap::new(),
        errors: Vec::new(),
    };

    let rust_base_path = "/home/cinder/Documents/repos/Surrentumlabs/Rust Component Repos";
    let ts_base_path = "/home/cinder/Documents/repos/Surrentumlabs/Typescript Component Repos";

    // Process Rust repositories
    println!("Processing Rust repositories...");
    if let Ok(entries) = fs::read_dir(rust_base_path) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    process_rust_repo(&path, &mut inventory);
                }
            }
        }
    } else {
        inventory.errors.push(format!("Failed to read Rust repos directory: {}", rust_base_path));
    }

    // Process TypeScript repositories
    println!("Processing TypeScript repositories...");
    if let Ok(entries) = fs::read_dir(ts_base_path) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    process_typescript_repo(&path, &mut inventory);
                }
            }
        }
    } else {
        inventory.errors.push(format!("Failed to read TypeScript repos directory: {}", ts_base_path));
    }

    // Generate summary
    inventory.summary.insert("total_rust_repos".to_string(), inventory.rust_repos.len());
    inventory.summary.insert("total_typescript_repos".to_string(), inventory.typescript_repos.len());
    inventory.summary.insert("successful_rust_parses".to_string(), 
        inventory.rust_repos.iter().filter(|r| r.parse_error.is_none()).count());
    inventory.summary.insert("successful_typescript_parses".to_string(), 
        inventory.typescript_repos.iter().filter(|r| r.parse_error.is_none()).count());
    inventory.summary.insert("failed_parses".to_string(), 
        inventory.rust_repos.iter().filter(|r| r.parse_error.is_some()).count() +
        inventory.typescript_repos.iter().filter(|r| r.parse_error.is_some()).count());

    // Write to JSON file
    let output_path = "/tmp/repo_inventory.json";
    match serde_json::to_string_pretty(&inventory) {
        Ok(json_output) => {
            if let Err(e) = fs::write(output_path, json_output) {
                eprintln!("Failed to write inventory to {}: {}", output_path, e);
            } else {
                println!("Inventory written to: {}", output_path);
            }
        }
        Err(e) => eprintln!("Failed to serialize inventory: {}", e),
    }

    // Write to YAML file as well
    let yaml_path = "/tmp/repo_inventory.yaml";
    match serde_yaml::to_string(&inventory) {
        Ok(yaml_output) => {
            if let Err(e) = fs::write(yaml_path, yaml_output) {
                eprintln!("Failed to write YAML inventory to {}: {}", yaml_path, e);
            } else {
                println!("YAML inventory written to: {}", yaml_path);
            }
        }
        Err(e) => eprintln!("Failed to serialize YAML inventory: {}", e),
    }

    // Print summary
    println!("\n=== INVENTORY SUMMARY ===");
    println!("Rust repositories processed: {}", inventory.rust_repos.len());
    println!("TypeScript repositories processed: {}", inventory.typescript_repos.len());
    println!("Total successful parses: {}", 
        inventory.rust_repos.iter().filter(|r| r.parse_error.is_none()).count() +
        inventory.typescript_repos.iter().filter(|r| r.parse_error.is_none()).count());
    println!("Total failed parses: {}", 
        inventory.rust_repos.iter().filter(|r| r.parse_error.is_some()).count() +
        inventory.typescript_repos.iter().filter(|r| r.parse_error.is_some()).count());

    if !inventory.errors.is_empty() {
        println!("\n=== ERRORS ===");
        for error in &inventory.errors {
            println!("❌ {}", error);
        }
    }

    // Check for failures and update Tasks.md if needed
    let failed_repos: Vec<&RepoMetadata> = inventory.rust_repos.iter()
        .chain(inventory.typescript_repos.iter())
        .filter(|r| r.parse_error.is_some())
        .collect();

    if !failed_repos.is_empty() {
        println!("\n⚠️ Found {} repositories with parse errors. Adding TODO to Tasks.md...", failed_repos.len());
        update_tasks_md(&failed_repos);
    }
}

fn process_rust_repo(repo_path: &Path, inventory: &mut InventoryReport) {
    let repo_name = repo_path.file_name().unwrap().to_string_lossy().to_string();
    let cargo_toml_path = repo_path.join("Cargo.toml");
    
    println!("Processing Rust repo: {}", repo_name);
    
    let mut metadata = RepoMetadata {
        name: repo_name.clone(),
        repo_type: "rust".to_string(),
        path: repo_path.to_string_lossy().to_string(),
        package_name: None,
        version: None,
        edition: None,
        dependencies: None,
        dev_dependencies: None,
        parse_error: None,
    };

    if !cargo_toml_path.exists() {
        metadata.parse_error = Some("Cargo.toml not found".to_string());
        inventory.rust_repos.push(metadata);
        return;
    }

    match fs::read_to_string(&cargo_toml_path) {
        Ok(content) => {
            match toml::from_str::<CargoToml>(&content) {
                Ok(cargo_data) => {
                    if let Some(package) = cargo_data.package {
                        metadata.package_name = Some(package.name);
                        metadata.version = Some(package.version);
                        metadata.edition = package.edition;
                    }
                    metadata.dependencies = cargo_data.dependencies;
                }
                Err(e) => {
                    metadata.parse_error = Some(format!("Failed to parse Cargo.toml: {}", e));
                }
            }
        }
        Err(e) => {
            metadata.parse_error = Some(format!("Failed to read Cargo.toml: {}", e));
        }
    }

    inventory.rust_repos.push(metadata);
}

fn process_typescript_repo(repo_path: &Path, inventory: &mut InventoryReport) {
    let repo_name = repo_path.file_name().unwrap().to_string_lossy().to_string();
    let package_json_path = repo_path.join("package.json");
    
    println!("Processing TypeScript repo: {}", repo_name);
    
    let mut metadata = RepoMetadata {
        name: repo_name.clone(),
        repo_type: "typescript".to_string(),
        path: repo_path.to_string_lossy().to_string(),
        package_name: None,
        version: None,
        edition: None,
        dependencies: None,
        dev_dependencies: None,
        parse_error: None,
    };

    if !package_json_path.exists() {
        metadata.parse_error = Some("package.json not found".to_string());
        inventory.typescript_repos.push(metadata);
        return;
    }

    match fs::read_to_string(&package_json_path) {
        Ok(content) => {
            match serde_json::from_str::<PackageJson>(&content) {
                Ok(package_data) => {
                    metadata.package_name = package_data.name;
                    metadata.version = package_data.version;
                    
                    // Convert dependencies to the same format
                    if let Some(deps) = package_data.dependencies {
                        let mut converted_deps = HashMap::new();
                        for (k, v) in deps {
                            converted_deps.insert(k, serde_json::Value::String(v));
                        }
                        metadata.dependencies = Some(converted_deps);
                    }
                    
                    metadata.dev_dependencies = package_data.dev_dependencies;
                }
                Err(e) => {
                    metadata.parse_error = Some(format!("Failed to parse package.json: {}", e));
                }
            }
        }
        Err(e) => {
            metadata.parse_error = Some(format!("Failed to read package.json: {}", e));
        }
    }

    inventory.typescript_repos.push(metadata);
}

fn update_tasks_md(failed_repos: &[&RepoMetadata]) {
    let tasks_path = "/home/cinder/Documents/repos/Warp/Tasks.md";
    
    match fs::read_to_string(tasks_path) {
        Ok(mut content) => {
            let todo_entry = format!("\n## Repository Inventory Issues\n- [ ] **REPO INVENTORY**: Fix parsing errors in {} repositories - see /tmp/repo_inventory.json\n  Failed repos: {}\n", 
                failed_repos.len(), 
                failed_repos.iter().map(|r| r.name.as_str()).collect::<Vec<_>>().join(", "));
            
            // Find a good place to insert the TODO - after the Active Tasks section
            if let Some(pos) = content.find("## New Tasks") {
                content.insert_str(pos, &todo_entry);
            } else if let Some(pos) = content.find("## Undocumented Components") {
                content.insert_str(pos, &todo_entry);
            } else {
                // Fallback: append to end
                content.push_str(&todo_entry);
            }
            
            if let Err(e) = fs::write(tasks_path, content) {
                eprintln!("Failed to update Tasks.md: {}", e);
            } else {
                println!("✅ Updated Tasks.md with repository parsing issues");
            }
        }
        Err(e) => eprintln!("Failed to read Tasks.md: {}", e),
    }
}
