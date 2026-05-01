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


if __name__ == "__main__":
    unittest.main()
