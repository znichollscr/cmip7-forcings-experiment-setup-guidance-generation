"""ScenarioMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Mapping

from local.forcing_references import COMMON_FORCING_NOTES
from local.forcing_versions import (
    SCEN7_FORCING_VERSIONS_BY_SLUG,
    ForcingValue,
    source_ids_from_forcing_versions,
)
from local.guidance import ExperimentPage
from local.rendering import (
    join_blocks,
    render_data_access_body,
    render_versions_body,
)
from local.vocab import get_experiment


def make_scenariomip_page(
    slug: str,
    *,
    forcing_versions: Mapping[str, ForcingValue],
) -> ExperimentPage:
    """Create a ScenarioMIP experiment page."""
    experiment_name = get_experiment(slug).drs_name

    return ExperimentPage(
        slug=slug,
        experiment_setup=join_blocks(
            f"The `{experiment_name}` simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
        ).strip(),
        forcing_headlines=(
            f"The `{experiment_name}` experiment is a time-varying forcings experiment."
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(
            forcing_versions,
            include_multiple_options_note=False,
        ),
        getting_the_data=render_data_access_body(
            experiment_name=experiment_name,
            source_ids=source_ids_from_forcing_versions(forcing_versions),
        ),
    )


SCENARIOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = tuple(
    make_scenariomip_page(slug, forcing_versions=forcing_versions)
    for slug, forcing_versions in SCEN7_FORCING_VERSIONS_BY_SLUG.items()
)
