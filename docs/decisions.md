# Decisions

Record important project decisions here. Keep entries short, dated, and reversible when possible.

## Template

```md
## YYYY-MM-DD: Decision Title

Status: proposed | accepted | superseded

Context:

Decision:

Consequences:
```

## Log

## 2026-05-02: Use Python Standard Library for Vault Tools

Status: accepted

Context:
The first project features are local filesystem operations for an Obsidian
vault.

Decision:
Implement the CLI with Python standard-library modules only and run tests with
`unittest`.

Consequences:
The project can run with `python3 -m kb_tools` and does not require dependency
installation. Future dependencies should be added deliberately when they solve a
clear problem.

## 2026-05-02: Keep Template Language-Neutral

Status: superseded

Context:
This repository is a reusable starting point for projects that may use different
languages, frameworks, and deployment models.

Decision:
Keep scripts, documentation, and prompts stack-agnostic until a project chooses
its technology stack.

Consequences:
The initial commands validate structure and print guidance rather than invoking
language-specific tooling.

## 2026-05-02: Require Script Modes

Status: accepted

Context:
Reusable automation should be safe to inspect before it changes project state.

Decision:
Every shell script supports `--dry-run`, `--apply`, and `--help`.

Consequences:
Future project-specific scripts must preserve those options when replacing
placeholder behavior.
