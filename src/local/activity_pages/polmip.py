"""PolMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchFromParentEnd
from local.forcings import (
    get_scen7_forcing_specification,
)
from local.guidance import ExperimentPage
from local.mip_co_chair_review import get_pending_review_aft_experiments

POLMIP_EXPERIMENT_SLUGS = (
    # "ssp2-com",  # not registered yet
    "vl-cf",
    "esm-vl-cf",
    "vl-cf-ext",
    "esm-vl-cf-ext",
)


def make_polmip_page(slug: str) -> ExperimentPage:
    """Create a PolMIP experiment page."""
    return ExperimentPage(
        id_esgvoc=slug,
        branch_information=BranchFromParentEnd(),
        forcings=get_scen7_forcing_specification(slug),
        mip_co_chair_review=get_pending_review_aft_experiments("polmip"),
    )


POLMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = tuple(
    make_polmip_page(slug) for slug in POLMIP_EXPERIMENT_SLUGS
)
