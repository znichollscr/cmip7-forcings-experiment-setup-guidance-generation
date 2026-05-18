"""Output time axis text helpers for experiment guidance pages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from local.rendering import render_external_link

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


@dataclass(frozen=True)
class PendingCoChairReview:
    """
    Pending co-chair review
    """

    url: str
    """
    URL to the review
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the MIP co-chair information as a string"""
        rendered_url = render_external_link(
            self.url.replace("https://", "").replace("http://", ""), self.url
        )
        return f"pending, see {rendered_url}"


@dataclass(frozen=True)
class CompleteCoChairReview:
    """
    Complete co-chair review
    """

    url: str
    """
    URL to the review
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the MIP co-chair information as a string"""
        rendered_url = render_external_link(
            self.url.replace("https://", "").replace("http://", ""), self.url
        )
        return f"complete, see {rendered_url}"
