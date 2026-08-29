#!/usr/bin/env bash
# Install the global Claude Code setup into ~/.claude.
#
# Safe to run more than once. Anything it would overwrite is backed up first
# to ~/.claude/backup-<timestamp>/ — nothing is destroyed.
#
#   bash setup/install.sh

set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")/claude" && pwd)"
dest="$HOME/.claude"
stamp="$(date +%Y%m%d-%H%M%S)-$$"
backup="$dest/backup-$stamp"
backed_up=0

mkdir -p "$dest"

save() {
  # Back up a path if it already exists and differs from what we are installing.
  local existing="$1" incoming="$2" rel="$3"
  [ -e "$existing" ] || return 0
  # Unchanged? Then there is nothing worth keeping a copy of.
  if [ -f "$existing" ] && [ -f "$incoming" ] && cmp -s "$existing" "$incoming"; then
    return 0
  fi
  if [ -d "$existing" ] && [ -d "$incoming" ] && diff -rq "$existing" "$incoming" >/dev/null 2>&1; then
    return 0
  fi
  mkdir -p "$backup/$(dirname "$rel")"
  cp -R "$existing" "$backup/$rel"
  backed_up=1
  echo "  backed up existing $rel"
}

echo "Installing Claude Code setup into $dest"

# --- settings.json -----------------------------------------------------------
# Never merged automatically: if one already exists it is preserved and the new
# one is written alongside for you to reconcile by hand.
if [ -f "$dest/settings.json" ] && ! cmp -s "$dest/settings.json" "$src/settings.json"; then
  save "$dest/settings.json" "$src/settings.json" "settings.json"
  cp "$src/settings.json" "$dest/settings.json.new"
  echo "  ! you already have a settings.json — kept it, wrote settings.json.new beside it"
  echo "    merge the two by hand, then delete settings.json.new"
else
  cp "$src/settings.json" "$dest/settings.json"
  echo "  installed settings.json"
fi

# --- CLAUDE.md ---------------------------------------------------------------
save "$dest/CLAUDE.md" "$src/CLAUDE.md" "CLAUDE.md"
cp "$src/CLAUDE.md" "$dest/CLAUDE.md"
echo "  installed CLAUDE.md"

# --- statusline --------------------------------------------------------------
save "$dest/statusline.sh" "$src/statusline.sh" "statusline.sh"
cp "$src/statusline.sh" "$dest/statusline.sh"
chmod +x "$dest/statusline.sh"
echo "  installed statusline.sh"

# --- skills ------------------------------------------------------------------
mkdir -p "$dest/skills"
for skill in "$src"/skills/*/; do
  name="$(basename "$skill")"
  save "$dest/skills/$name" "$skill" "skills/$name"
  rm -rf "${dest:?}/skills/$name"
  cp -R "$skill" "$dest/skills/$name"
  echo "  installed skill: $name"
done

echo
if [ "$backed_up" -eq 1 ]; then
  echo "Previous files backed up to $backup"
fi
echo "Done. Start a new Claude Code session to pick these up."
echo "Check it worked with:  claude doctor"
