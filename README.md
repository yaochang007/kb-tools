# kb-tools

Small local Python tools for maintaining an Obsidian vault at
`~/KnowledgeBase`.

The project uses the Python standard library only. It does not require a package
manager, virtual environment, or external dependencies.

## Structure

- `AGENTS.md`: AI agent working instructions
- `kb_tools/`: Python CLI package
- `tests/`: standard-library `unittest` tests
- `docs/architecture.md`: system shape, boundaries, and data flow
- `docs/decisions.md`: decision log
- `tasks/todo.md`: task list
- `prompts/initial-brief.md`: project kickoff prompt for a new agent session
- `scripts/check.sh`: project validation entrypoint
- `scripts/dev.sh`: local development entrypoint
- `scripts/session-start.sh`: session startup checklist
- `scripts/session-close.sh`: session closeout checklist
- `.gitignore`: common local, cache, build, and secret patterns

## Usage

Run commands from the project root:

```sh
python3 -m kb_tools --help
```

Create today's daily note in `~/KnowledgeBase/10 Journal/Daily`:

```sh
python3 -m kb_tools daily
```

Preview a daily note without writing anything:

```sh
python3 -m kb_tools daily --date 2026-05-02 --dry-run
```

Create a project note in `~/KnowledgeBase/30 Projects/Active`:

```sh
python3 -m kb_tools project "Kitchen Renovation"
```

Preview a project note:

```sh
python3 -m kb_tools project "Kitchen Renovation" --dry-run
```

List unprocessed Markdown notes in `~/KnowledgeBase/00 Inbox`:

```sh
python3 -m kb_tools inbox
```

Check for broken Obsidian wikilinks:

```sh
python3 -m kb_tools links
```

Use a different vault path:

```sh
python3 -m kb_tools --vault /path/to/KnowledgeBase links
```

Write commands refuse to overwrite existing notes.

## Project Commands

```sh
./scripts/check.sh --dry-run
./scripts/check.sh --apply
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

`./scripts/check.sh --apply` runs:

```sh
python3 -m unittest discover -s tests
```

## Customizing This Project

- Keep commands standard-library only until the project deliberately adds dependencies.
- Add setup, check, and dev instructions to this README as behavior grows.
- Update `AGENTS.md` when the project has conventions agents must follow.
- Update `docs/architecture.md` when the system shape changes.
- Keep secrets in local environment files that are ignored by Git.

## Git

Check the working tree with:

```sh
git status --short
```
