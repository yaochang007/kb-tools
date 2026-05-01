#!/usr/bin/env sh

set -eu

MODE="apply"

# Print help text for people and agents before they run the script.
usage() {
  cat <<'EOF'
Usage: ./scripts/check.sh [--dry-run|--apply|--help]

Runs project checks.

This template is language-neutral. The default checks only verify that the
required template files exist. Replace or extend these checks after choosing a
project stack, while preserving --dry-run, --apply, and --help.

Default: --apply
EOF
}

# Parse supported mode flags. Keep this strict so typos fail loudly.
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) MODE="dry-run" ;;
    --apply) MODE="apply" ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

REQUIRED_FILES="
AGENTS.md
README.md
docs/architecture.md
docs/decisions.md
tasks/todo.md
prompts/initial-brief.md
scripts/check.sh
scripts/dev.sh
scripts/session-start.sh
scripts/session-close.sh
.gitignore
"

# In dry-run mode, describe the checks without reading or changing state.
if [ "$MODE" = "dry-run" ]; then
  for path in $REQUIRED_FILES; do
    printf '[dry-run] check %s exists\n' "$path"
  done
  printf '[dry-run] check shell scripts are executable\n'
  exit 0
fi

# Verify that every required template file is present.
for path in $REQUIRED_FILES; do
  if [ ! -e "$path" ]; then
    printf 'ERROR: missing required file: %s\n' "$path" >&2
    exit 1
  fi
done

# Verify script executability so project commands can be run consistently.
for path in scripts/check.sh scripts/dev.sh scripts/session-start.sh scripts/session-close.sh; do
  if [ ! -x "$path" ]; then
    printf 'ERROR: script is not executable: %s\n' "$path" >&2
    exit 1
  fi
done

printf 'Template checks passed.\n'
