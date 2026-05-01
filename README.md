# Project Template

Language-neutral starter scaffold for coding projects under `~/Documents/Codex/projects`.

Use this repository as the first folder for a new project. It is intentionally
small: the goal is to provide stable operating habits before a language,
framework, package manager, or deployment target is chosen.

## Structure

- `AGENTS.md`: AI agent working instructions
- `docs/architecture.md`: system shape, boundaries, and data flow
- `docs/decisions.md`: decision log
- `tasks/todo.md`: task list
- `prompts/initial-brief.md`: project kickoff prompt for a new agent session
- `scripts/check.sh`: project validation entrypoint
- `scripts/dev.sh`: local development entrypoint
- `scripts/session-start.sh`: session startup checklist
- `scripts/session-close.sh`: session closeout checklist
- `.gitignore`: common local, cache, build, and secret patterns

## Getting Started

1. Copy this folder to a new project directory.
2. Fill in the project purpose, commands, and architecture notes.
3. Replace placeholder scripts with real commands when the stack is known.
4. Keep `--dry-run` support in project scripts.
5. Record meaningful technical choices in `docs/decisions.md`.
6. Keep `tasks/todo.md` current enough that a future session can resume work.

## Commands

```sh
./scripts/check.sh --dry-run
./scripts/dev.sh --dry-run
./scripts/session-start.sh --dry-run
./scripts/session-close.sh --dry-run
```

All scripts accept:

- `--dry-run`: print what would happen without changing project state.
- `--apply`: perform the script action.
- `--help`: show usage.

`scripts/session-close.sh` has two modes:

- Without a session name, it preserves the normal handoff checklist behavior:
  `bash scripts/session-close.sh --dry-run`
- With a tmux session name, it targets only that tmux session:
  `bash scripts/session-close.sh --dry-run test-session` prints the tmux close
  commands, and `bash scripts/session-close.sh --apply test-session` checks that
  the session exists before closing it.

## Customizing This Template

- Replace placeholder commands only after the project chooses a stack.
- Add stack-specific setup, check, and dev instructions to this README.
- Update `AGENTS.md` when the project has conventions agents must follow.
- Update `docs/architecture.md` when the system shape changes.
- Keep secrets in local environment files that are ignored by Git.

## Git

This template is intended to be tracked in Git from the beginning. After copying
it to a new project, check the initial status with:

```sh
git status --short
```
