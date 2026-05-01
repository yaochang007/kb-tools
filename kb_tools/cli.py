"""Small standard-library tools for an Obsidian vault."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


DEFAULT_VAULT = Path("~/KnowledgeBase").expanduser()
DAILY_DIR = Path("10 Journal") / "Daily"
PROJECTS_DIR = Path("30 Projects") / "Active"
INBOX_DIR = Path("00 Inbox")


@dataclass(frozen=True)
class NoteResult:
    path: Path
    created: bool
    dry_run: bool


def parse_note_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def slugify_title(title: str) -> str:
    slug = title.strip().lower()
    slug = re.sub(r"[^\w.-]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        raise ValueError("project title must contain at least one letter or number")
    return slug


def write_new_note(path: Path, body: str, dry_run: bool) -> NoteResult:
    if path.exists():
        raise FileExistsError(f"note already exists: {path}")

    if dry_run:
        return NoteResult(path=path, created=False, dry_run=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as note:
        note.write(body)
    return NoteResult(path=path, created=True, dry_run=False)


def daily_note_body(note_date: date) -> str:
    stamp = note_date.isoformat()
    return f"# {stamp}\n\n## Notes\n\n## Tasks\n"


def project_note_body(title: str) -> str:
    today = date.today().isoformat()
    return (
        f"# {title.strip()}\n\n"
        "Status: Active\n"
        f"Created: {today}\n\n"
        "## Purpose\n\n"
        "## Notes\n\n"
        "## Next Actions\n"
    )


def create_daily_note(vault: Path, note_date: date, dry_run: bool) -> NoteResult:
    path = vault / DAILY_DIR / f"{note_date.isoformat()}.md"
    return write_new_note(path, daily_note_body(note_date), dry_run)


def create_project_note(vault: Path, title: str, dry_run: bool) -> NoteResult:
    path = vault / PROJECTS_DIR / f"{slugify_title(title)}.md"
    return write_new_note(path, project_note_body(title), dry_run)


def list_unprocessed_inbox(vault: Path) -> list[Path]:
    inbox = vault / INBOX_DIR
    if not inbox.is_dir():
        return []

    notes = [
        path
        for path in inbox.iterdir()
        if path.is_file() and path.suffix.lower() == ".md"
    ]
    return sorted(notes, key=lambda path: path.name.lower())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kb-tools",
        description="Local standard-library tools for an Obsidian vault.",
    )
    parser.add_argument(
        "--vault",
        type=Path,
        default=DEFAULT_VAULT,
        help="Obsidian vault path (default: ~/KnowledgeBase)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    daily = subparsers.add_parser("daily", help="Create a daily note")
    daily.add_argument(
        "--date",
        type=parse_note_date,
        default=date.today(),
        help="Daily note date in YYYY-MM-DD format (default: today)",
    )
    daily.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the note path without creating the file",
    )

    project = subparsers.add_parser("project", help="Create a project note")
    project.add_argument("title", help="Project note title")
    project.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the note path without creating the file",
    )

    subparsers.add_parser("inbox", help="List Markdown notes in 00 Inbox")

    return parser


def format_path(path: Path) -> str:
    return str(path.expanduser())


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    vault = args.vault.expanduser()

    try:
        if args.command == "daily":
            result = create_daily_note(vault, args.date, args.dry_run)
            verb = "Would create" if result.dry_run else "Created"
            print(f"{verb} daily note: {format_path(result.path)}")
            return 0

        if args.command == "project":
            result = create_project_note(vault, args.title, args.dry_run)
            verb = "Would create" if result.dry_run else "Created"
            print(f"{verb} project note: {format_path(result.path)}")
            return 0

        if args.command == "inbox":
            notes = list_unprocessed_inbox(vault)
            for path in notes:
                print(format_path(path))
            if not notes:
                print(f"No unprocessed notes found in {format_path(vault / INBOX_DIR)}")
            return 0
    except (FileExistsError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2
