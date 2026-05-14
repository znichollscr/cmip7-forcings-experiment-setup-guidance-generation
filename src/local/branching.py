"""Branching text helpers for experiment guidance pages."""

from __future__ import annotations

from local.rendering import join_blocks


def branch_from(
    *,
    experiment: str,
    parent: str,
    parent_activity: str,
    branch_instruction: str,
    extra: str = "",
) -> str:
    """Render parent-experiment branch information."""
    return join_blocks(
        (
            f"`{experiment}` branches from the `{parent}` simulation "
            f"(part of `{parent_activity}`)."
        ),
        branch_instruction,
        extra,
    ).strip()
