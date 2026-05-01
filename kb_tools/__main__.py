"""Command line entrypoint for ``python -m kb_tools``."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
