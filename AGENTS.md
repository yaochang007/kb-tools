# Agent Instructions

Use this file to guide AI coding agents working in this project.

## Operating Rules

- Read the relevant code and docs before making changes.
- Keep edits scoped to the requested task.
- Do not use `sudo`.
- Do not delete files unless explicitly asked.
- Do not overwrite existing user work.
- Prefer clear, reviewable changes over broad rewrites.
- Keep secrets out of code, logs, prompts, and docs.
- Keep the template language-neutral until the project deliberately chooses a stack.
- Preserve existing content when expanding docs, prompts, scripts, or configuration.

## Workflow

- Start by checking `README.md`, `docs/architecture.md`, `docs/decisions.md`, and `tasks/todo.md`.
- If starting a new work session, run `./scripts/session-start.sh --dry-run` to preview the context checklist.
- Update docs when a change affects architecture, setup, or expected behavior.
- Run the narrowest useful checks before handing work back.
- If closing a work session, run `./scripts/session-close.sh --dry-run` to preview the handoff checklist.
- Report what changed, what was checked, and any remaining risks.

## Project Commands

```sh
./scripts/check.sh --dry-run
./scripts/dev.sh --dry-run
./scripts/session-start.sh --dry-run
./scripts/session-close.sh --dry-run
```

Replace these placeholder scripts with project-specific commands when the technology stack is chosen.
Every script must continue to support `--dry-run`, `--apply`, and `--help`.

## Documentation Map

- `README.md`: project purpose, setup, command index, and customization notes.
- `docs/architecture.md`: system shape, boundaries, data flow, and operational notes.
- `docs/decisions.md`: dated decision log.
- `tasks/todo.md`: active project task list.
- `prompts/initial-brief.md`: reusable project kickoff prompt.
