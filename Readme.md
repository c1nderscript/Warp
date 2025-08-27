# Warp Documentation Control

This repository contains the control files for documenting both the Twitch file storage tree and multiple software repositories under Surrentumlabs.

## Navigation Entry Points

- **[[../Twitch Docs/Index]]** - Global map and navigation for all Twitch storage documentation
  - ⭐ **New Feature**: See **Component Categories** section with 4-tier classification (🔴Essential, 🟡Semi-Essential, 🟢Non-Essential, ⚫Disconnected)
- **[[../Repos Docs/Index]]** - Repository documentation index for all Surrentumlabs repos  
- **[[../Twitch Docs/Coverage]]** - Comprehensive tracking ledger with category classifications for all documented components

## Control Files

- **[[Tasks]]** - Active documentation tasks and backlog
- **[[Changelog]]** - Timestamped record of all documentation updates  
- **[[AGENTS]]** - Canonical policy and protocol documentation

## Documentation Locations

- **Storage Documentation**: `/home/cinder/Documents/repos/Twitch Docs/` (for `/home/cinder/Documents/Twitch`)
- **Repository Documentation**: `/home/cinder/Documents/repos/Repos Docs/` (for repos under `/home/cinder/Documents/repos/Surrentumlabs`)

## Component Categorization System (New)

The documentation now includes systematic component categorization following ADR-0001:

- **🔴 Essential Components** (21): Core platform domains, critical infrastructure, revenue-critical services
- **🟡 Semi-Essential Components** (93): Developer tooling, monitoring, supporting services, business features  
- **🟢 Non-Essential Components** (43): Team directories, legacy systems, experimental projects
- **⚫ Disconnected Components** (43): Utility files, configuration, standalone resources

See the **Component Categories** sections in both [[../Twitch Docs/Index]] and [[../Twitch Docs/Coverage]] for detailed breakdowns and component lists.

## Architecture Decisions

The following architectural decisions guide the categorization and documentation process:

- **[[docs/architecture/adr-0001-component-categorization]]** - Methodology and criteria for component classification
- **[[docs/architecture/adr-0002-disconnected-removal]]** - Strategy for removing disconnected components

## Quick Start

1. Check [[../Twitch Docs/Coverage]] for current documentation status and category classifications of both storage and repository components
2. Review [[Tasks]] for active work items across both documentation modes
3. Navigate via [[../Twitch Docs/Index]] Component Categories section for prioritized component access
4. Use [[../Repos Docs/Index]] for repository-specific documentation
5. All updates tracked in [[Changelog]]

---

*Follow the Warp Documentation Protocol as defined in [[AGENTS]] for consistent documentation practices.*
