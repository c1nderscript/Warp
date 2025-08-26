# AGENTS.md - Canonical Documentation Policy

## Warp Documentation Protocol (Local Storage Mode)

This document serves as the canonical policy for documenting `/home/cinder/Documents/Twitch` into `/home/cinder/Documents/repos/Twitch Docs`.

### Core Requirements

1. **Four File Maintenance**: Always read and update Tasks.md, Changelog.md, AGENTS.md, Readme.md in `/home/cinder/Documents/repos/Warp`

2. **Progress Tracking**: Maintain central ledger at `Twitch Docs/Coverage.md` with Dataview-friendly checklist table containing:
   - component: Name/identifier
   - type: folder|file|service|etc
   - source_path: Full path in source tree
   - status: todo|partial|done
   - last_scanned: UTC timestamp
   - doc_file: Link to Component Card
   - backlinks: Obsidian links

3. **Component Documentation**: Each item gets a Component Card at `Twitch Docs/Components/<component>.md` with:
   - YAML frontmatter (status, source_path, last_scanned, tags, links)
   - Sections: Purpose, Key Files, Interfaces, Depends On, Used By, Notes
   - Mandatory backlinks: source path, [[Coverage]], 

4. **Navigation**: `Twitch Docs/Index.md` as global map listing domains/subsystems with embedded Mermaid diagrams

5. **Backlinking**: Obsidian-native `[[...]]` links mandatory in all directions for discoverability

6. **Task Management**: New discoveries → Tasks.md with [[Coverage]] links and todo status

7. **Change Tracking**: Each action → Changelog.md entry with timestamp and relevant backlinks

8. **Documentation Gaps**: Missing info noted explicitly with matching TODOs in Tasks.md

### Success Criteria
- Coverage.md accurately reflects all known items
- Tasks.md contains actionable TODOs  
- Bidirectional backlinks exist
- Changelog.md records all updates with timestamps

## Protocol Changes (2025-01-27)

**No protocol changes in this cycle.** The Warp Documentation Protocol remains unchanged and has been successfully applied throughout the repository documentation process. All documentation follows established standards for:

- YAML frontmatter with status, source_path, last_scanned, tags, links
- Component Cards with Purpose, Key Files, Interfaces, Depends On, Used By, Notes sections
- Obsidian-style [[...]] backlinking throughout all documentation
- Coverage tracking with Dataview-compatible tables
- Tasks.md integration for TODO management
- Changelog.md timestamped entries for all updates

## Architecture Decision Policies

The following ADRs are adopted as canonical policy and must be followed in all documentation and maintenance workflows:

- [[docs/architecture/adr-0001-component-categorization]]: Establishes the three-tier categorization system (Essential, Semi-Essential, Non-Essential) and the methodology/criteria for classification. All Coverage tables and Component Cards must include and maintain the category field.
- [[docs/architecture/adr-0002-disconnected-removal]]: Defines the removal strategy for disconnected components, including automated flagging, 30-day grace period, validation, execution, and archival requirements. All removals must be logged in [[Changelog]] and tracked via [[Tasks]].

### Enforcement (Updated 2025-01-27)
- **Quarterly Reassessment**: Mandatory category review per ADR-0001 methodology using updated dependency matrix analysis
- **Removal Process**: Full ADR-0002 workflow enforcement with automated flagging, 30-day grace period, and archive creation
- **Category Validation**: All Coverage.md tables must maintain category column with Essential/Semi-Essential/Non-Essential classification
- **Component Card Enhancement**: YAML frontmatter category fields mandatory per ADR-0001 requirements
- **Index Integration**: Component Categories sections in both Twitch Docs and Repos Docs indexes must be kept current
- **Documentation Cross-Reference**: Obsidian backlinks to ADRs maintained from both index files and component cards
- **Task Generation**: Analysis-generated tasks must be systematically added to Tasks.md with proper [[Coverage]] backlinks

### Links
[[Coverage]] | [[../Twitch Docs/Index]] | [[../Repos Docs/Index]] | [[Tasks]] | [[Changelog]] | [[docs/architecture/adr-0001-component-categorization]] | [[docs/architecture/adr-0002-disconnected-removal]]
