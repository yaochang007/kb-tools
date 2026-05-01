#!/usr/bin/env sh

set -eu

MODE="apply"
TMUX_SESSION=""

# Print usage for closing a session with a clear handoff.
usage() {
  cat <<'EOF'
Usage: ./scripts/session-close.sh [--dry-run|--apply|--help] [tmux-session]

Prepares a work session handoff by showing the checks and notes to complete
before handing the project back.

When a tmux session name is provided, dry-run mode prints the tmux commands that
would close that session. Apply mode checks that the named session exists before
closing only that tmux session.

Default: --apply
EOF
}

# Parse supported mode flags plus one optional tmux session name.
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) MODE="dry-run" ;;
    --apply) MODE="apply" ;;
    -h|--help) usage; exit 0 ;;
    --*) printf 'ERROR: unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    *)
      if [ -n "$TMUX_SESSION" ]; then
        printf 'ERROR: only one tmux session name may be provided\n' >&2
        usage >&2
        exit 2
      fi
      TMUX_SESSION="$1"
      ;;
  esac
  shift
done

# If a tmux session name is supplied, handle only the targeted tmux close flow.
if [ -n "$TMUX_SESSION" ]; then
  if [ "$MODE" = "dry-run" ]; then
    printf '[dry-run] tmux has-session -t %s\n' "$TMUX_SESSION"
    printf '[dry-run] tmux kill-session -t %s\n' "$TMUX_SESSION"
    exit 0
  fi

  # Confirm tmux is installed before asking it about the named session.
  if ! command -v tmux >/dev/null 2>&1; then
    printf 'ERROR: tmux is not installed or is not on PATH\n' >&2
    exit 1
  fi

  # Check that the named session exists before closing it.
  if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    printf 'ERROR: tmux session does not exist: %s\n' "$TMUX_SESSION" >&2
    exit 1
  fi

  # Close only the requested tmux session.
  tmux kill-session -t "$TMUX_SESSION"
  printf 'Closed tmux session: %s\n' "$TMUX_SESSION"
  exit 0
fi

# In dry-run mode, describe the closeout checklist without changing state.
if [ "$MODE" = "dry-run" ]; then
  printf '[dry-run] run ./scripts/check.sh --dry-run\n'
  printf '[dry-run] review git status\n'
  printf '[dry-run] update docs when behavior or setup changed\n'
  printf '[dry-run] update tasks/todo.md with next actions\n'
  printf '[dry-run] report changes, checks, and risks\n'
  exit 0
fi

# In apply mode, print a concise checklist for a clean handoff.
printf 'Session close checklist:\n'
printf '1. Run the narrowest useful checks for the change.\n'
printf '2. Review Git status and mention any unrelated existing changes.\n'
printf '3. Update docs and tasks when project behavior or next steps changed.\n'
printf '4. Report what changed, what was checked, and any remaining risks.\n'
