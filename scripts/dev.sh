#!/usr/bin/env sh

set -eu

MODE="apply"

# Print help text for this language-neutral development entrypoint.
usage() {
  cat <<'EOF'
Usage: ./scripts/dev.sh [--dry-run|--apply|--help]

Shows the local CLI help for this Python standard-library project.

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
  printf '[dry-run] run python3 -m kb_tools --help\n'
  exit 0
fi

python3 -m kb_tools --help
