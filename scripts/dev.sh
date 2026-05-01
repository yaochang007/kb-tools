#!/usr/bin/env sh

set -eu

MODE="apply"

# Print help text for this language-neutral development entrypoint.
usage() {
  cat <<'EOF'
Usage: ./scripts/dev.sh [--dry-run|--apply|--help]

Starts the local development workflow. This template is language-neutral;
replace the placeholder command after choosing a stack, while preserving
--dry-run, --apply, and --help.

Default: --apply
EOF
}

# Parse supported mode flags. Unknown arguments are treated as mistakes.
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) MODE="dry-run" ;;
    --apply) MODE="apply" ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

# In dry-run mode, show the intended behavior without starting processes.
if [ "$MODE" = "dry-run" ]; then
  printf '[dry-run] print project startup instructions\n'
  printf '[dry-run] no server or watcher would be started by this template\n'
  exit 0
fi

# In apply mode, the template gives guidance until a real stack exists.
printf 'No language stack configured yet.\n'
printf 'Update scripts/dev.sh with the project-specific development command.\n'
