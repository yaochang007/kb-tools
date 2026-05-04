# Architecture

## Purpose

`kb-tools` provides small local command line utilities for maintaining an
Obsidian vault at `~/KnowledgeBase`.

## Principles

- Use the Python standard library only until a dependency is deliberately added.
- Prefer simple project boundaries that are easy to explain and test.
- Keep configuration explicit and avoid committing secrets.
- Document behavior changes close to the code or workflow they affect.
- Never overwrite existing notes.
- Do not modify or delete existing vault content unless explicitly requested.

## System Overview

- Entry points: `python3 -m kb_tools`, `scripts/check.sh`, `scripts/dev.sh`
- Core modules: `kb_tools.cli`
- External dependencies: none
- Data stores: local Markdown files in the configured Obsidian vault
- Background jobs: none

## Boundaries

- In scope: daily note creation, active project note creation, literature/source
  note creation, inbox note listing, broken wikilink reporting, and read-only
  Markdown search.
- Out of scope: syncing, remote APIs, external package integrations, destructive
  cleanup, or automatic edits to existing notes.

## Data Flow

```text
CLI arguments -> Path resolution -> Safety checks -> Note creation, listing, or validation -> Console output
```

Write commands resolve a target path under the vault, check that the note does
not already exist, and then create the file with exclusive creation. With
`--dry-run`, they print the intended target path without writing. The inbox
command reads direct Markdown files from `00 Inbox` and prints them sorted by
filename. The links command recursively reads Markdown files, builds an index by
note filename and vault-relative note path without `.md`, and reports wikilinks
whose stripped target does not match that index.

## Operational Notes

- Configuration: `--vault` overrides the default `~/KnowledgeBase`.
- Local development: run `python3 -m kb_tools --help`.
- Testing: run `python3 -m unittest discover -s tests` or
  `./scripts/check.sh --apply`.
- Deployment: local-only scripts; no deployment target.
- Observability: command output and process exit codes.

## Repository Conventions

- `scripts/` contains human-readable entrypoints with `--dry-run`, `--apply`, and `--help`.
- `docs/` contains durable project knowledge.
- `tasks/` contains working notes that help future sessions resume.
- `prompts/` contains reusable prompts for project kickoff or agent workflows.

## Risks

- Note templates are intentionally minimal and may need to evolve with real
  vault conventions.
- Wikilink validation currently checks note targets only; it strips headings but
  does not verify whether a heading exists inside the resolved note.
