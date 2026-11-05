"""PolMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchFromParentAtGivenYearStart, BranchFromParentEnd
from local.forcings import (
    get_polmip_scenario_forcing_specification,
    get_polmip_vl_cf_forcing_specification,
)
from local.guidance import ExperimentPage
from local.mip_co_chair_review import get_pending_review_aft_experiments

POLMIP_EXPERIMENT_SLUGS = (
    # "ssp2-com",  # not registered yet
    "vl-cf",
    "esm-vl-cf",
    "vl-cf-ext",
    "esm-vl-cf-ext",
    "ssp2-com-cmip7",
    "esm-ssp2-com-cmip7",
    "ssp2-com-cmip7-ext",
    "esm-ssp2-com-cmip7-ext",
)


def make_polmip_page(slug: str) -> ExperimentPage:
    """Create a PolMIP experiment page."""
    if "ext" in slug:
        branch_information = BranchFromParentEnd()
    elif "vl-cf" in slug:
        # Funny inconsistency across things.
        # Here we say 2016-01-01.
        # Above and for ScenarioMIP we say parent end i.e. 2021-12-31.
        # Hopefully doesn't matter...
        branch_information = BranchFromParentAtGivenYearStart(2016)
    else:
        branch_information = BranchFromParentEnd()

    if "vl-cf" in slug:
        return ExperimentPage(
            id_esgvoc=slug,
            branch_information=branch_information,
            forcings=get_polmip_vl_cf_forcing_specification(slug),
            mip_co_chair_review=get_pending_review_aft_experiments("polmip"),
        )

    if any(v in slug for v in ("ssp2-com-cmip7",)):
        return ExperimentPage(
            id_esgvoc=slug,
            branch_information=branch_information,
            forcings=get_polmip_scenario_forcing_specification(
                slug, base_scenario_experiment_id="scen7-vl"
            ),
            mip_co_chair_review=get_pending_review_aft_experiments("polmip"),
        )

    raise NotImplementedError(slug)


POLMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = tuple(
    make_polmip_page(slug) for slug in POLMIP_EXPERIMENT_SLUGS
)
