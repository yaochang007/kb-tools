# Architecture

## Purpose

Describe what the project does and who it serves.

## Principles

- Stay language-neutral until a stack is chosen.
- Prefer simple project boundaries that are easy to explain and test.
- Keep configuration explicit and avoid committing secrets.
- Document behavior changes close to the code or workflow they affect.

## System Overview

- Entry points:
- Core modules:
- External dependencies:
- Data stores:
- Background jobs:

## Boundaries

- In scope:
- Out of scope:

## Data Flow

Describe how data enters, moves through, and leaves the system.

```text
Input -> Validation -> Core behavior -> Output
```

Replace this sketch with the real flow when the project has one.

## Operational Notes

- Configuration:
- Local development:
- Testing:
- Deployment:
- Observability:

## Repository Conventions

- `scripts/` contains human-readable entrypoints with `--dry-run`, `--apply`, and `--help`.
- `docs/` contains durable project knowledge.
- `tasks/` contains working notes that help future sessions resume.
- `prompts/` contains reusable prompts for project kickoff or agent workflows.

## Risks

- Stack-specific commands are not configured yet.
- Architecture and operational details are placeholders until the project is defined.
