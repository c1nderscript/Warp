# In Progress Pull Requests

This document tracks pull requests currently being worked on.

## Format
Each entry should include:
- PR title/description
- Link to PR
- Current status/progress
- Next steps
- Any blockers or dependencies

## Currently In Progress

### Infrastructure Foundation (Group 1)

1. [#113] Fix CI failures after #71
   - Branch: fix/post-71-ci-issues
   - Status: Ready for review
   - Changes made:
     - ✅ Removed strims-typescript references from frontend-core-migration-table.json
     - ✅ Updated package.json test path to fix npm test
     - ✅ Cleaned up protobuf-rust workspace member references
   - Next:
     - [ ] Get PR review and approval
     - [ ] Merge PR
   - Dependencies: #71 (merged)
   - Blocks: All subsequent PRs failing CI

2. [#77] chore: remove pubsub-control-edge from e2e compose
   - Branch: cinder/verify-build/config-files-for-dependencies
   - Status: Pending merge of #71
   - Dependencies: #71
   - Next: Update e2e configuration after #71 merges

3. [#95] [pubsub-edge-rs] Add retryable broker connection
   - Branch: cinder/merge-legacy-chat-connection-logic
   - Status: Ready for review
   - Dependencies: ✅ #71, ✅ #77
   - Changes made:
     - ✅ Implemented connection.rs module
     - ✅ Added exponential backoff with jitter
     - ✅ Implemented state management
     - ✅ Added comprehensive error handling
     - ✅ Full test coverage with unit and integration tests
   - Next: Code review and integration testing

### Priority Order
1. Fix CI for PR #71 and merge
2. Update PR #77 with e2e config changes
3. Implement PR #95's broker connection features

### Testing Strategy
- ✅ Legacy code backup created
- ✅ No remaining references to old code
- ⚠️ Need to verify CI fixes after workspace cleanup
- ⚠️ Need to run full integration tests
- ✅ Documentation updated with new migration guide
- ⏳ Need final review of migration docs

### Repository Standards Status
- ✅ Root CHANGELOG.md following semantic versioning
- ✅ Latest version: [0.3.1] with proper documentation
- ✅ Workspace root properly configured
- ✅ All workspace dependencies specified
