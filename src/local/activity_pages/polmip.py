"""PolMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchFromParentAtGivenYearStart, BranchFromParentEnd
from local.forcings import get_polmip_vl_cf_forcing_specification
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
    if "ext" in slug:
        branch_information = BranchFromParentEnd()
    else:
        # Funny inconsistency across things.
        # Here we say 2016-01-01.
        # Above and for ScenarioMIP we say parent end i.e. 2021-12-31.
        # Hopefully doesn't matter...
        branch_information = BranchFromParentAtGivenYearStart(2016)

    if "vl-cf" in slug:
        return ExperimentPage(
            id_esgvoc=slug,
            branch_information=branch_information,
            forcings=get_polmip_vl_cf_forcing_specification(slug),
            mip_co_chair_review=get_pending_review_aft_experiments("polmip"),
        )

    raise NotImplementedError(slug)


POLMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = tuple(
    make_polmip_page(slug) for slug in POLMIP_EXPERIMENT_SLUGS
)
