#!/usr/bin/env bash
set -euo pipefail

# flatten_push_dgg_services.sh
# Recursively remove nested git metadata/submodules and push as a flat repo.

TARGET_DIR="/home/cinder/Documents/repos/Surrentumlabs/Monorepos/DGG-Services"
REMOTE_URL="https://github.com/c1nderscript/DGG-Services"
DEFAULT_BRANCH="main"

CONFIRM=false
[[ "${1:-}" == "--confirm" ]] && CONFIRM=true

say(){ printf "%b\n" "$*\n"; }
run(){ if $CONFIRM; then eval "$*"; else say "DRY-RUN: $*"; fi; }

# --- preflight ---
command -v git >/dev/null || { echo "git not found"; exit 1; }
[[ -d "$TARGET_DIR" ]] || { echo "Target dir missing: $TARGET_DIR"; exit 1; }

say "Target:  $TARGET_DIR"
say "Remote:  $REMOTE_URL"
say "Branch:  $DEFAULT_BRANCH"
$CONFIRM || say "Mode:    DRY-RUN (no changes will be made)"
echo

cd "$TARGET_DIR"

# Init repo if needed
if [[ ! -d .git ]]; then
  say "Initializing git repository..."
  run "git init"
fi

# Ensure desired branch
current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
if [[ "$current_branch" != "$DEFAULT_BRANCH" ]]; then
  if git show-ref --verify --quiet "refs/heads/$DEFAULT_BRANCH"; then
    run "git switch '$DEFAULT_BRANCH'"
  else
    if [[ "$current_branch" != "HEAD" ]]; then
      run "git branch -m '$current_branch' '$DEFAULT_BRANCH' || git switch -c '$DEFAULT_BRANCH'"
    else
      run "git switch -c '$DEFAULT_BRANCH'"
    fi
  fi
fi

# Set origin
if git remote get-url origin >/dev/null 2>&1; then
  existing="$(git remote get-url origin)"
  if [[ "$existing" != "$REMOTE_URL" ]]; then
    say "Updating origin → $REMOTE_URL"
    run "git remote set-url origin '$REMOTE_URL'"
  fi
else
  say "Adding origin → $REMOTE_URL"
  run "git remote add origin '$REMOTE_URL'"
fi
echo

# Only scan index if a repo actually exists (in DRY-RUN, .git may not be created)
SUBMODULE_PATHS=()
if [[ -d .git ]]; then
  say "Scanning index for submodule gitlinks..."
  # mode 160000 indicates submodule entries in the index
  mapfile -t SUBMODULE_PATHS < <(git ls-files --stage 2>/dev/null | awk '$1 ~ /^160000/ {print $4}')
  if (( ${#SUBMODULE_PATHS[@]} > 0 )); then
    for p in "${SUBMODULE_PATHS[@]}"; do say "  gitlink: $p"; done
  else
    say "  none found"
  fi
else
  say "Skipping index scan (no .git yet in DRY-RUN)."
fi
echo

# Find nested .git dirs/files on disk (these cause submodules)
say "Scanning filesystem for nested .git metadata..."
mapfile -t NESTED_GIT_DIRS  < <(find . -mindepth 2 -type d -name '.git' -print 2>/dev/null || true)
mapfile -t NESTED_GIT_FILES < <(find . -mindepth 2 -type f -name '.git' -print 2>/dev/null || true)
if (( ${#NESTED_GIT_DIRS[@]} + ${#NESTED_GIT_FILES[@]} > 0 )); then
  for p in "${NESTED_GIT_DIRS[@]}";  do say "  DIR  $p"; done
  for p in "${NESTED_GIT_FILES[@]}"; do say "  FILE $p"; done
else
  say "  none found"
fi
echo

# Remove submodule entries from index (keep working tree files)
if (( ${#SUBMODULE_PATHS[@]} > 0 )); then
  say "Removing submodule entries from index (keeping files)..."
  run "git submodule deinit -f . || true"
  run "rm -rf .git/modules/* || true"
  for p in "${SUBMODULE_PATHS[@]}"; do
    run "git rm -f --cached -- '$p'"
  done
fi

# Remove .gitmodules if present
if [[ -f .gitmodules ]]; then
  say "Removing .gitmodules..."
  if $CONFIRM; then
    git rm -f --cached .gitmodules || true
    rm -f .gitmodules
  else
    say "DRY-RUN: git rm -f --cached .gitmodules && rm -f .gitmodules"
  fi
fi

# Delete nested .git dirs/files so they can't re-register as submodules
if (( ${#NESTED_GIT_DIRS[@]} > 0 )); then
  say "Deleting nested .git directories..."
  for p in "${NESTED_GIT_DIRS[@]}"; do run "rm -rf -- '$p'"; done
fi
if (( ${#NESTED_GIT_FILES[@]} > 0 )); then
  say "Deleting nested .git files..."
  for p in "${NESTED_GIT_FILES[@]}"; do run "rm -f -- '$p'"; done
fi
echo

# Add, commit, push
say "Re-adding all files..."
run "git add -A"

if $CONFIRM; then
  if git diff --cached --quiet; then
    say "No staged changes; nothing to commit."
  else
    say "Committing flatten changes..."
    git commit -m "chore(repo): flatten nested repos → regular directories"
  fi
  say "Pushing to origin/$DEFAULT_BRANCH..."
  git push -u origin "$DEFAULT_BRANCH" --force
else
  say "DRY-RUN complete. Re-run with --confirm to apply changes and push."
fi

say "Done."
