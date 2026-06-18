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


@dataclass(frozen=True)
class PendingReview:
    """
    Pending review
    """

    url: str
    """URL to the pending review"""

    def render(self, experiment: ExperimentPage) -> str:
        """Render the MIP co-chair information as a string"""
        return f"**In progress** see [{self.url}]({self.url})"


@dataclass(frozen=True)
class CompleteReview:
    """
    Complete (i.e. finished) review
    """

    url: str
    """URL to the complete review"""

    def render(self, experiment: ExperimentPage) -> str:
        """Render the MIP co-chair information as a string"""
        return f"**Complete** see [{self.url}]({self.url})"


def get_pending_review_aft_experiments(activity: str) -> PendingReview:
    """
    Get pending review based on activity
    """
    review_lookup = {
        "aerchemmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/184",
        "c4mip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/186",
        "cfmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/185",
        "cmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/183",
        "damip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/188",
        "dcpp": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/207",
        "geomip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/189",
        "lmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/190",
        "pmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/191",
        "rfmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/192",
        "scenariomip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/187",
    }

    return PendingReview(review_lookup[activity])


def get_complete_review_aft_experiments(activity: str) -> CompleteReview:
    """
    Get complete review based on activity
    """
    review_lookup = {
        "aerchemmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/184",
        # "c4mip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/186",
        # "cfmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/185",
        # "cmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/183",
        # "damip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/188",
        "dcpp": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/207",
        # "geomip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/189",
        # "lmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/190",
        # "pmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/191",
        # "rfmip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/192",
        # "scenariomip": "https://github.com/WCRP-CMIP/cmip7-guidance/issues/187",
    }

    return CompleteReview(review_lookup[activity])
