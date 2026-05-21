"""ScenarioMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchFromParentEnd
from local.forcings import (
    get_scen7_forcing_specification,
)
from local.guidance import ExperimentPage

SCENARIOMIP_EXPERIMENT_SLUGS = (
    "scen7-h",
    "esm-scen7-h",
    "scen7-h-ext",
    "esm-scen7-h-ext",
    "scen7-hl",
    "esm-scen7-hl",
    "scen7-hl-ext",
    "esm-scen7-hl-ext",
    "scen7-l",
    "esm-scen7-l",
    "scen7-l-ext",
    "esm-scen7-l-ext",
    "scen7-ln",
    "esm-scen7-ln",
    "scen7-ln-ext",
    "esm-scen7-ln-ext",
    "scen7-m",
    "esm-scen7-m",
    "scen7-m-ext",
    "esm-scen7-m-ext",
    "scen7-ml",
    "esm-scen7-ml",
    "scen7-ml-ext",
    "esm-scen7-ml-ext",
    "scen7-vl",
    "esm-scen7-vl",
    "scen7-vl-ext",
    "esm-scen7-vl-ext",
)


def make_scenariomip_page(slug: str) -> ExperimentPage:
    """Create a ScenarioMIP experiment page."""
    return ExperimentPage(
        id_esgvoc=slug,
        branch_information=BranchFromParentEnd(),
        forcings=get_scen7_forcing_specification(slug),
    )


SCENARIOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = tuple(
    make_scenariomip_page(slug) for slug in SCENARIOMIP_EXPERIMENT_SLUGS
)
