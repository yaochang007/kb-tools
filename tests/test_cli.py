from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from kb_tools import cli


class KbToolsTests(unittest.TestCase):
    def test_daily_dry_run_does_not_create_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            result = cli.create_daily_note(vault, date(2026, 5, 2), dry_run=True)

            self.assertFalse(result.created)
            self.assertFalse(result.path.exists())
            self.assertEqual(
                vault / "10 Journal" / "Daily" / "2026-05-02.md",
                result.path,
            )

    def test_daily_note_refuses_to_overwrite_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            path = vault / "10 Journal" / "Daily" / "2026-05-02.md"
            path.parent.mkdir(parents=True)
            path.write_text("existing\n", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                cli.create_daily_note(vault, date(2026, 5, 2), dry_run=False)

            self.assertEqual("existing\n", path.read_text(encoding="utf-8"))

    def test_project_note_uses_slugified_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            result = cli.create_project_note(vault, "My New Project!", dry_run=False)

            self.assertTrue(result.path.exists())
            self.assertEqual(
                vault / "30 Projects" / "Active" / "my-new-project.md",
                result.path,
            )
            self.assertIn("# My New Project!", result.path.read_text(encoding="utf-8"))

    def test_project_note_slug_keeps_unicode_words(self) -> None:
        self.assertEqual("知识库-project", cli.slugify_title("知识库 Project"))

    def test_source_dry_run_does_not_create_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            result = cli.create_source_note(
                vault,
                "A Useful Article",
                "",
                "",
                date(2026, 5, 5),
                dry_run=True,
            )

            self.assertFalse(result.created)
            self.assertFalse(result.path.exists())
            self.assertEqual(
                vault / "20 Notes" / "Literature" / "a-useful-article.md",
                result.path,
            )

    def test_source_note_uses_template_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            result = cli.create_source_note(
                vault,
                "A Useful Article",
                "https://example.com/article",
                "Ada Lovelace",
                date(2026, 5, 5),
                dry_run=False,
            )

            self.assertTrue(result.path.exists())
            self.assertEqual(
                (
                    "# A Useful Article\n\n"
                    "## Source\n"
                    "- URL: https://example.com/article\n"
                    "- Author: Ada Lovelace\n"
                    "- Date added: 2026-05-05\n\n"
                    "## Summary\n\n"
                    "## Key Ideas\n\n"
                    "## Quotes / Notes\n\n"
                    "## Links\n"
                ),
                result.path.read_text(encoding="utf-8"),
            )

    def test_source_note_refuses_to_overwrite_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            path = vault / "20 Notes" / "Literature" / "a-useful-article.md"
            path.parent.mkdir(parents=True)
            path.write_text("existing\n", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                cli.create_source_note(
                    vault,
                    "A Useful Article",
                    "",
                    "",
                    date(2026, 5, 5),
                    dry_run=False,
                )

            self.assertEqual("existing\n", path.read_text(encoding="utf-8"))

    def test_main_source_dry_run_prints_target_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(
                    [
                        "--vault",
                        tmp,
                        "source",
                        "A Useful Article",
                        "--url",
                        "https://example.com/article",
                        "--author",
                        "Ada Lovelace",
                        "--date",
                        "2026-05-05",
                        "--dry-run",
                    ]
                )

            self.assertEqual(0, code)
            self.assertEqual(
                (
                    "Would create source note: "
                    f"{vault / '20 Notes' / 'Literature' / 'a-useful-article.md'}\n"
                ),
                stdout.getvalue(),
            )

    def test_markdown_filename_does_not_double_append_extension(self) -> None:
        self.assertEqual("Inbox.md", cli.markdown_filename("Inbox.md"))
        self.assertEqual("Inbox.md", cli.markdown_filename("Inbox.md.md"))
        self.assertEqual("Inbox.md", cli.markdown_filename("Inbox"))

    def test_inbox_lists_only_markdown_files_sorted_by_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            inbox = vault / "00 Inbox"
            inbox.mkdir()
            (inbox / "zeta.md").write_text("", encoding="utf-8")
            (inbox / "alpha.md").write_text("", encoding="utf-8")
            (inbox / "ignore.txt").write_text("", encoding="utf-8")
            (inbox / "folder.md").mkdir()

            self.assertEqual(
                [inbox / "alpha.md", inbox / "zeta.md"],
                cli.list_unprocessed_inbox(vault),
            )

    def test_main_inbox_prints_existing_md_filename_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            inbox = vault / "00 Inbox"
            inbox.mkdir()
            note = inbox / "Inbox.md"
            note.write_text("", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "inbox"])

            self.assertEqual(0, code)
            self.assertEqual(f"{note}\n", stdout.getvalue())
            self.assertNotIn("Inbox.md.md", stdout.getvalue())

    def test_main_inbox_prints_double_md_filename_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            inbox = vault / "00 Inbox"
            inbox.mkdir()
            (inbox / "Inbox.md.md").write_text("", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "inbox"])

            self.assertEqual(0, code)
            self.assertEqual(f"{inbox / 'Inbox.md'}\n", stdout.getvalue())

    def test_main_inbox_prints_empty_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "inbox"])

            self.assertEqual(0, code)
            self.assertIn("No unprocessed notes found", stdout.getvalue())

    def test_wikilink_targets_strip_aliases_and_headings(self) -> None:
        text = (
            "[[Note Name]]\n"
            "[[Folder/Note Name]]\n"
            "[[Note Name|Alias]]\n"
            "[[Note Name#Heading]]\n"
            "[[Folder/Note Name#Heading|Alias]]\n"
        )

        self.assertEqual(
            [
                "Note Name",
                "Folder/Note Name",
                "Note Name",
                "Note Name",
                "Folder/Note Name",
            ],
            cli.wikilink_targets(text),
        )

    def test_note_index_includes_filename_and_relative_path_without_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            folder = vault / "Folder"
            folder.mkdir()
            (folder / "Note Name.md").write_text("", encoding="utf-8")

            self.assertEqual(
                {"Note Name", "Folder/Note Name"},
                cli.note_index(vault),
            )

    def test_find_broken_wikilinks_reports_missing_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            folder = vault / "Folder"
            folder.mkdir()
            source = vault / "Source.md"
            (vault / "Existing.md").write_text("", encoding="utf-8")
            (folder / "Nested.md").write_text("", encoding="utf-8")
            source.write_text(
                "\n".join(
                    [
                        "[[Existing]]",
                        "[[Folder/Nested#Heading|Alias]]",
                        "[[Missing Note|Alias]]",
                        "[[Folder/Missing#Heading]]",
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(
                [
                    cli.BrokenLink(source=source, target="Missing Note"),
                    cli.BrokenLink(source=source, target="Folder/Missing"),
                ],
                cli.find_broken_wikilinks(vault),
            )

    def test_main_links_prints_broken_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            source = vault / "Source.md"
            source.write_text("[[Missing#Heading|Alias]]", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "links"])

            self.assertEqual(0, code)
            self.assertEqual(f"{source}: Missing\n", stdout.getvalue())

    def test_main_links_prints_success_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            (vault / "Source.md").write_text("[[Source]]", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "links"])

            self.assertEqual(0, code)
            self.assertIn("No broken wikilinks found", stdout.getvalue())

    def test_search_vault_matches_case_insensitively_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            note = vault / "Note.md"
            note.write_text("Codex is here\nsecond line\n", encoding="utf-8")

            self.assertEqual(
                [cli.SearchMatch(path=note, line_number=1, line="Codex is here")],
                cli.search_vault(vault, "codex"),
            )

    def test_search_vault_can_match_case_sensitively(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            note = vault / "Note.md"
            note.write_text("Codex\ncodex\n", encoding="utf-8")

            self.assertEqual(
                [cli.SearchMatch(path=note, line_number=2, line="codex")],
                cli.search_vault(vault, "codex", case_sensitive=True),
            )

    def test_search_vault_can_limit_to_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            active = vault / "30 Projects" / "Active"
            archive = vault / "30 Projects" / "Archive"
            active.mkdir(parents=True)
            archive.mkdir(parents=True)
            active_note = active / "Graphify.md"
            active_note.write_text("Graphify roadmap\n", encoding="utf-8")
            (archive / "Old.md").write_text("Graphify archive\n", encoding="utf-8")

            self.assertEqual(
                [
                    cli.SearchMatch(
                        path=active_note,
                        line_number=1,
                        line="Graphify roadmap",
                    )
                ],
                cli.search_vault(vault, "Graphify", folder="30 Projects/Active"),
            )

    def test_search_vault_rejects_folder_outside_vault(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            vault.mkdir()

            with self.assertRaises(ValueError):
                cli.search_vault(vault, "Codex", folder="../outside")

    def test_search_vault_ignores_metadata_and_attachments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            note = vault / "Note.md"
            note.write_text("Codex visible\n", encoding="utf-8")
            for folder in [".git", ".obsidian", "Attachments"]:
                ignored = vault / folder
                ignored.mkdir()
                (ignored / "Ignored.md").write_text("Codex hidden\n", encoding="utf-8")

            self.assertEqual(
                [cli.SearchMatch(path=note, line_number=1, line="Codex visible")],
                cli.search_vault(vault, "Codex"),
            )

    def test_search_vault_respects_max_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            note = vault / "Note.md"
            note.write_text("AI one\nAI two\nAI three\n", encoding="utf-8")

            self.assertEqual(
                [
                    cli.SearchMatch(path=note, line_number=1, line="AI one"),
                    cli.SearchMatch(path=note, line_number=2, line="AI two"),
                ],
                cli.search_vault(vault, "AI", max_results=2),
            )

    def test_search_vault_paths_returns_matching_notes_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            first = vault / "First.md"
            second = vault / "Second.md"
            first.write_text("Codex one\nCodex two\n", encoding="utf-8")
            second.write_text("Codex three\n", encoding="utf-8")

            self.assertEqual(
                [first, second],
                cli.search_vault_paths(vault, "Codex", max_results=2),
            )

    def test_main_search_prints_matching_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            note = vault / "Note.md"
            note.write_text("intro\nCodex line\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "search", "codex"])

            self.assertEqual(0, code)
            self.assertEqual(f"{note}:2: Codex line\n", stdout.getvalue())

    def test_main_search_content_only_prints_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            note = vault / "Note.md"
            note.write_text("Codex line\nCodex again\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "search", "Codex", "--content-only"])

            self.assertEqual(0, code)
            self.assertEqual(f"{note}\n", stdout.getvalue())

    def test_main_search_prints_no_results_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            (vault / "Note.md").write_text("nothing here\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["--vault", tmp, "search", "Codex"])

            self.assertEqual(0, code)
            self.assertIn("No matches found for 'Codex'", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
