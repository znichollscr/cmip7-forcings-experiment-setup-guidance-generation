"""Output time axis text helpers for experiment guidance pages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from local.guidance import ExperimentPage


@dataclass(frozen=True)
class NoCoChairReview:
    """
    No co-chair review
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the MIP co-chair information as a string"""
        return "No review initiated yet"
