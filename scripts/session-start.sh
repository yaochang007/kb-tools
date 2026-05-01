#!/usr/bin/env sh

set -eu

MODE="apply"

# Print usage for starting a safe, repeatable work session.
usage() {
  cat <<'EOF'
Usage: ./scripts/session-start.sh [--dry-run|--apply|--help]

Prepares a new project work session by showing the files and commands an agent
or developer should review before making changes.

Default: --apply
EOF
}

# Parse supported mode flags and reject unknown arguments.
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) MODE="dry-run" ;;
    --apply) MODE="apply" ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

# In dry-run mode, describe the startup checklist without inspecting files.
if [ "$MODE" = "dry-run" ]; then
  printf '[dry-run] review AGENTS.md\n'
  printf '[dry-run] review README.md\n'
  printf '[dry-run] review docs/architecture.md\n'
  printf '[dry-run] review docs/decisions.md\n'
  printf '[dry-run] review tasks/todo.md\n'
  printf '[dry-run] run ./scripts/check.sh --dry-run\n'
  exit 0
fi

# In apply mode, print a concise checklist for the current session.
printf 'Session start checklist:\n'
printf '1. Read AGENTS.md, README.md, docs/architecture.md, docs/decisions.md, and tasks/todo.md.\n'
printf '2. Check current Git status before editing.\n'
printf '3. Run ./scripts/check.sh --dry-run before making broad changes.\n'
printf '4. Keep changes scoped and preserve existing work.\n'
