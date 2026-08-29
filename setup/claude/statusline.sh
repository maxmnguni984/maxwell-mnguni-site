#!/usr/bin/env bash
# Claude Code status line: directory, git branch and dirty state, model.
# Claude Code pipes a JSON blob on stdin; everything below reads from it.

input=$(cat)

dir=$(printf '%s' "$input" | sed -n 's/.*"current_dir"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
model=$(printf '%s' "$input" | sed -n 's/.*"display_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ -z "$dir" ] && dir="$PWD"

branch=""
if git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
  branch=$(git -C "$dir" branch --show-current 2>/dev/null)
  [ -z "$branch" ] && branch=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
  if [ -n "$(git -C "$dir" status --porcelain 2>/dev/null)" ]; then
    branch="${branch}*"
  fi
fi

printf '\033[2m%s\033[0m' "$(basename "$dir")"
[ -n "$branch" ] && printf '  \033[36m%s\033[0m' "$branch"
[ -n "$model" ] && printf '  \033[2m%s\033[0m' "$model"
