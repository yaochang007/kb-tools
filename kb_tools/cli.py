"""Small standard-library tools for an Obsidian vault."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


DEFAULT_VAULT = Path("~/KnowledgeBase").expanduser()
DAILY_DIR = Path("10 Journal") / "Daily"
PROJECTS_DIR = Path("30 Projects") / "Active"
SOURCES_DIR = Path("20 Notes") / "Literature"
INBOX_DIR = Path("00 Inbox")


@dataclass(frozen=True)
class NoteResult:
    path: Path
    created: bool
    dry_run: bool


@dataclass(frozen=True)
class BrokenLink:
    source: Path
    target: str


@dataclass(frozen=True)
class SearchMatch:
    path: Path
    line_number: int
    line: str


def parse_note_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def parse_positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be an integer") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return number


def slugify_title(title: str) -> str:
    slug = title.strip().lower()
    slug = re.sub(r"[^\w.-]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        raise ValueError("title must contain at least one letter or number")
    return slug


def markdown_filename(name: str) -> str:
    while name.lower().endswith(".md"):
        name = name[:-3]
    return f"{name}.md"


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


def source_note_body(
    title: str,
    url: str,
    author: str,
    date_added: date,
) -> str:
    return (
        f"# {title.strip()}\n\n"
        "## Source\n"
        f"- URL: {url}\n"
        f"- Author: {author}\n"
        f"- Date added: {date_added.isoformat()}\n\n"
        "## Summary\n\n"
        "## Key Ideas\n\n"
        "## Quotes / Notes\n\n"
        "## Links\n"
    )


def create_daily_note(vault: Path, note_date: date, dry_run: bool) -> NoteResult:
    path = vault / DAILY_DIR / f"{note_date.isoformat()}.md"
    return write_new_note(path, daily_note_body(note_date), dry_run)


def create_project_note(vault: Path, title: str, dry_run: bool) -> NoteResult:
    path = vault / PROJECTS_DIR / markdown_filename(slugify_title(title))
    return write_new_note(path, project_note_body(title), dry_run)


def create_source_note(
    vault: Path,
    title: str,
    url: str,
    author: str,
    date_added: date,
    dry_run: bool,
) -> NoteResult:
    path = vault / SOURCES_DIR / markdown_filename(slugify_title(title))
    return write_new_note(
        path,
        source_note_body(title, url, author, date_added),
        dry_run,
    )


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


def markdown_files(vault: Path) -> list[Path]:
    if not vault.is_dir():
        return []
    return sorted(
        (path for path in vault.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(vault).as_posix().lower(),
    )


def note_index(vault: Path) -> set[str]:
    index: set[str] = set()
    for path in markdown_files(vault):
        relative_note = path.relative_to(vault).with_suffix("").as_posix()
        index.add(path.stem)
        index.add(relative_note)
    return index


WIKILINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")


def wikilink_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in WIKILINK_RE.finditer(text):
        target = match.group(1).split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            targets.append(target)
    return targets


def find_broken_wikilinks(vault: Path) -> list[BrokenLink]:
    index = note_index(vault)
    broken: list[BrokenLink] = []

    for path in markdown_files(vault):
        text = path.read_text(encoding="utf-8")
        for target in wikilink_targets(text):
            if target not in index:
                broken.append(BrokenLink(source=path, target=target))

    return broken


IGNORED_SEARCH_DIRS = {".git", ".obsidian", "Attachments"}


def has_ignored_search_dir(path: Path, vault: Path) -> bool:
    try:
        parts = path.relative_to(vault).parts
    except ValueError:
        parts = path.parts
    return any(part in IGNORED_SEARCH_DIRS for part in parts)


def search_markdown_files(vault: Path, folder: str | None = None) -> list[Path]:
    vault_root = vault.resolve()
    if folder is None:
        root = vault
    else:
        folder_path = Path(folder)
        if folder_path.is_absolute():
            raise ValueError("--folder must be relative to the vault")
        root = vault / folder_path
        try:
            root.resolve().relative_to(vault_root)
        except ValueError as exc:
            raise ValueError("--folder must stay inside the vault") from exc

    if not root.is_dir():
        return []

    return sorted(
        (
            path
            for path in root.rglob("*.md")
            if path.is_file() and not has_ignored_search_dir(path, vault)
        ),
        key=lambda path: path.relative_to(vault).as_posix().lower(),
    )


def search_vault(
    vault: Path,
    keyword: str,
    case_sensitive: bool = False,
    folder: str | None = None,
    max_results: int = 50,
) -> list[SearchMatch]:
    if keyword == "":
        raise ValueError("keyword must not be empty")

    needle = keyword if case_sensitive else keyword.casefold()
    matches: list[SearchMatch] = []

    for path in search_markdown_files(vault, folder):
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            haystack = line if case_sensitive else line.casefold()
            if needle in haystack:
                matches.append(SearchMatch(path=path, line_number=line_number, line=line))
                if len(matches) >= max_results:
                    return matches

    return matches


def search_vault_paths(
    vault: Path,
    keyword: str,
    case_sensitive: bool = False,
    folder: str | None = None,
    max_results: int = 50,
) -> list[Path]:
    if keyword == "":
        raise ValueError("keyword must not be empty")

    needle = keyword if case_sensitive else keyword.casefold()
    paths: list[Path] = []

    for path in search_markdown_files(vault, folder):
        for line in path.read_text(encoding="utf-8").splitlines():
            haystack = line if case_sensitive else line.casefold()
            if needle in haystack:
                paths.append(path)
                if len(paths) >= max_results:
                    return paths
                break

    return paths


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

    source = subparsers.add_parser("source", help="Create a literature/source note")
    source.add_argument("title", help="Source note title")
    source.add_argument("--url", default="", help="Source URL")
    source.add_argument("--author", default="", help="Source author")
    source.add_argument(
        "--date",
        type=parse_note_date,
        default=date.today(),
        help="Date added in YYYY-MM-DD format (default: today)",
    )
    source.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the note path without creating the file",
    )

    subparsers.add_parser("inbox", help="List Markdown notes in 00 Inbox")
    subparsers.add_parser("links", help="Report broken Obsidian wikilinks")

    search = subparsers.add_parser("search", help="Search Markdown files")
    search.add_argument("keyword", help="Keyword to search for")
    search.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive matching",
    )
    search.add_argument(
        "--folder",
        help="Limit search to a vault-relative folder path",
    )
    search.add_argument(
        "--max-results",
        type=parse_positive_int,
        default=50,
        help="Maximum results to print (default: 50)",
    )
    search.add_argument(
        "--content-only",
        action="store_true",
        help="Print only matching note paths",
    )

    return parser


def format_path(path: Path) -> str:
    return str(path.expanduser())


def format_inbox_path(path: Path) -> str:
    return format_path(path.with_name(markdown_filename(path.name)))


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

        if args.command == "source":
            result = create_source_note(
                vault,
                args.title,
                args.url,
                args.author,
                args.date,
                args.dry_run,
            )
            verb = "Would create" if result.dry_run else "Created"
            print(f"{verb} source note: {format_path(result.path)}")
            return 0

        if args.command == "inbox":
            notes = list_unprocessed_inbox(vault)
            for path in notes:
                print(format_inbox_path(path))
            if not notes:
                print(f"No unprocessed notes found in {format_path(vault / INBOX_DIR)}")
            return 0

        if args.command == "links":
            broken_links = find_broken_wikilinks(vault)
            for broken_link in broken_links:
                print(f"{format_path(broken_link.source)}: {broken_link.target}")
            if not broken_links:
                print(f"No broken wikilinks found in {format_path(vault)}")
            return 0

        if args.command == "search":
            if args.content_only:
                paths = search_vault_paths(
                    vault,
                    args.keyword,
                    args.case_sensitive,
                    args.folder,
                    args.max_results,
                )
                for path in paths:
                    print(format_path(path))
                if not paths:
                    print(f"No matches found for {args.keyword!r} in {format_path(vault)}")
                return 0

            matches = search_vault(
                vault,
                args.keyword,
                args.case_sensitive,
                args.folder,
                args.max_results,
            )
            for match in matches:
                print(f"{format_path(match.path)}:{match.line_number}: {match.line}")
            if not matches:
                print(f"No matches found for {args.keyword!r} in {format_path(vault)}")
            return 0
    except (FileExistsError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2
