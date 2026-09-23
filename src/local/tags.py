"""Tags used to label experiment guidance pages."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Tag:
    """A label applied to an experiment guidance page"""

    label: str
    """
    Label to display on the page
    """


AFT = Tag(label="AFT (Assessment Fast Track)")
"""Experiments which are part of the Assessment Fast Track"""


def render_tags(tags: Sequence[Tag]) -> str:
    """
    Render the tags applied to an experiment guidance page
    """
    return ", ".join(tag.label for tag in tags)
