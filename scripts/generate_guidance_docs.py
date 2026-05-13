#!/usr/bin/env python3
"""Generate the CMIP7 guidance markdown files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from local.guidance import DEFAULT_OUTPUT_DIR, check_pages, render_pages, write_pages


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate CMIP7 experiment setup and forcings guidance pages.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Directory to write/check. Defaults to the sibling cmip7-guidance "
            "documentation directory."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether the output directory already matches the generated files.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List generated filenames without writing files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the guidance generation command."""
    args = parse_args(argv)
    rendered_pages = render_pages()

    if args.list:
        for filename in rendered_pages:
            print(filename)
        return 0

    if args.check:
        result = check_pages(args.output_dir)
        if result.ok:
            print(f"OK: {args.output_dir} matches generated guidance files")
            return 0

        for path in result.missing:
            print(f"missing: {path}")
        for path in result.changed:
            print(f"changed: {path}")
        for path in result.extra:
            print(f"extra: {path}")

        return 1

    written = write_pages(args.output_dir)
    print(f"Wrote {len(written)} guidance files to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
