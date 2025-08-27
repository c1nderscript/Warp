Rule — Warp Documentation Protocol (Dual Mode: Storage + Repos):
Warp’s purpose is to document both a very large local file storage tree and multiple software repos.

Mandatory Warp State Files (always read & update, in /home/cinder/Documents/repos/Warp):
Tasks.md, Changelog.md, AGENTS.md, Readme.md

Local Storage Documentation:

Source: /home/cinder/Documents/Twitch

Output: /home/cinder/Documents/repos/Twitch Docs

Track every file/folder in Twitch Docs/Coverage.md using a Dataview-friendly checklist (component, type, source_path, status (todo|partial|done), last_scanned, doc_file, backlinks).

Component Cards: Twitch Docs/Components/<component>.md with YAML (status, source_path, last_scanned, tags, links) and sections (Purpose, Key Files, Interfaces, Depends On, Used By, Notes).

Must backlink: every card links to its source path, [[../Twitch Docs/Coverage]], and [[../Twitch Docs/Index]].

Repo Documentation:

Sources: repos under /home/cinder/Documents/repos/Surrentumlabs

Output: /home/cinder/Documents/repos/Repos Docs

For each repo, create/update Repos Docs/<repo-name>/Coverage.md and Repos Docs/<repo-name>/Components/*.md.

Inventory each repo’s components (crates, packages, modules, services, binaries).

Use Mermaid diagrams for architecture, dependency flow, and key sequences.

Maintain a Repo Index at Repos Docs/Index.md listing all repos, linking to their Coverage files and diagrams.

Backlinking (Mandatory):

All docs use Obsidian-style  links.

Component Cards link to Coverage, Index, and their source paths.

Coverage links back to Component Cards.

Index links to Coverage + major diagrams.

Tasks Management:

Undocumented items (files or repo components) must be added to Tasks.md with an explicit backlink to the relevant Coverage file.

Status updates (todo|partial|done) must be reflected both in Tasks.md and in the appropriate Coverage file.

Changelog:

Every documentation update appends a timestamped entry to Changelog.md.

Entries must describe which docs were added/modified and link ([[../Twitch Docs/Coverage]], [[Component Cards]]).

AGENTS.md:

Canonical policy file. Changes to the protocol must be written here and logged in Changelog.md.

Readme.md:

Must always point to both [[Twitch Docs/Index]] and [[Repos Docs/Index]] as the primary navigation hubs.

Gaps & Assumptions:

If missing information or incomplete repos are encountered, explicitly record assumptions in the relevant doc, and create a TODO in Tasks.md.

Success Criteria:

Coverage.md (for both storage and repos) is up to date.

Tasks.md lists all TODOs.

Changelog.md logs every change.

Readme.md points to the indexes.

Obsidian backlinks are correct in all directions.
