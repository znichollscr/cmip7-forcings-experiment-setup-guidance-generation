"""ScenarioMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchFromParentEnd
from local.forcings import (
    get_scen7_forcing_specification,
)
from local.guidance import ExperimentPage
from local.mip_co_chair_review import get_pending_review_aft_experiments
from local.tags import AFT, Tag

SCENARIOMIP_EXPERIMENTS: tuple[tuple[str, tuple[Tag, ...]], ...] = (
    ("scen7-h", (AFT,)),
    ("esm-scen7-h", (AFT,)),
    ("scen7-h-ext", (AFT,)),
    ("esm-scen7-h-ext", (AFT,)),
    ("scen7-hl", (AFT,)),
    ("esm-scen7-hl", (AFT,)),
    ("scen7-hl-ext", (AFT,)),
    ("esm-scen7-hl-ext", (AFT,)),
    ("scen7-l", (AFT,)),
    ("esm-scen7-l", (AFT,)),
    ("scen7-l-ext", (AFT,)),
    ("esm-scen7-l-ext", (AFT,)),
    ("scen7-ln", (AFT,)),
    ("esm-scen7-ln", (AFT,)),
    ("scen7-ln-ext", (AFT,)),
    ("esm-scen7-ln-ext", (AFT,)),
    ("scen7-m", (AFT,)),
    ("esm-scen7-m", (AFT,)),
    ("scen7-m-ext", (AFT,)),
    ("esm-scen7-m-ext", (AFT,)),
    ("scen7-ml", (AFT,)),
    ("esm-scen7-ml", (AFT,)),
    ("scen7-ml-ext", (AFT,)),
    ("esm-scen7-ml-ext", (AFT,)),
    ("scen7-vl", (AFT,)),
    ("esm-scen7-vl", (AFT,)),
    ("scen7-vl-ext", (AFT,)),
    ("esm-scen7-vl-ext", (AFT,)),
)


def make_scenariomip_page(slug: str, *, tags: tuple[Tag, ...]) -> ExperimentPage:
    """Create a ScenarioMIP experiment page."""
    return ExperimentPage(
        id_esgvoc=slug,
        branch_information=BranchFromParentEnd(),
        forcings=get_scen7_forcing_specification(slug),
        mip_co_chair_review=get_pending_review_aft_experiments("scenariomip"),
        tags=tags,
    )


SCENARIOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = tuple(
    make_scenariomip_page(slug, tags=tags) for slug, tags in SCENARIOMIP_EXPERIMENTS
)
