#!/usr/bin/env python3
"""Generate the CMIP7 guidance markdown files."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import typer

from local.guidance import DEFAULT_OUTPUT_DIR, check_pages, render_pages, write_pages


def main(
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help=(
                "Directory to write/check. Defaults to the sibling "
                "cmip7-guidance documentation directory."
            ),
        ),
    ] = DEFAULT_OUTPUT_DIR,
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            help=(
                "Check whether the output directory already matches the "
                "generated files."
            ),
        ),
    ] = False,
    list_files: Annotated[
        bool,
        typer.Option(
            "--list",
            help="List generated filenames without writing files.",
        ),
    ] = False,
) -> None:
    """Generate CMIP7 experiment setup and forcings guidance pages."""
    rendered_pages = render_pages()

    if list_files:
        for filename in rendered_pages:
            typer.echo(filename)
        return

    if check:
        result = check_pages(output_dir)
        if result.ok:
            typer.echo(f"OK: {output_dir} matches generated guidance files")
            return

        for path in result.missing:
            typer.echo(f"missing: {path}")
        for path in result.changed:
            typer.echo(f"changed: {path}")
        for path in result.extra:
            typer.echo(f"extra: {path}")

        raise typer.Exit(1)

    written = write_pages(output_dir)
    typer.echo(f"Wrote {len(written)} guidance files to {output_dir}")


if __name__ == "__main__":
    typer.run(main)
