"""ScenarioMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Mapping

from local.branching import BranchFromParentEnd
from local.forcing_versions import (
    SCEN7_FORCING_VERSIONS_BY_SLUG,
    ForcingValue,
)
from local.forcings import (
    get_scen7_forcing_specification,
)
from local.guidance import ExperimentPage, ExperimentPageOld


def make_scenariomip_page(
    slug: str,
    *,
    forcing_versions: Mapping[str, ForcingValue],
) -> ExperimentPageOld:
    """Create a ScenarioMIP experiment page."""
    return ExperimentPage(
        id_esgvoc=slug,
        branch_information=BranchFromParentEnd(),
        # mip_co_chair_review=PendingCoChairReview(url="url"),
        forcings=get_scen7_forcing_specification(slug),
    )


SCENARIOMIP_EXPERIMENT_PAGES: tuple[ExperimentPageOld, ...] = tuple(
    make_scenariomip_page(slug, forcing_versions=forcing_versions)
    for slug, forcing_versions in SCEN7_FORCING_VERSIONS_BY_SLUG.items()
)
