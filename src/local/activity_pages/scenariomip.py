"""ScenarioMIP experiment guidance pages."""

from __future__ import annotations

from local.forcing_references import COMMON_FORCING_NOTES
from local.forcing_versions import (
    SCEN7_VL_FORCING_VERSIONS,
    source_ids_from_forcing_versions,
)
from local.guidance import (
    SETUP_GENERATION_TODO,
    ExperimentPage,
)
from local.rendering import (
    join_blocks,
    render_data_access_body,
    render_versions_body,
)

SCENARIOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="scen7-vl",
        experiment_setup=join_blocks(
            "The CMIP7 very low scenario simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
            "The simulation output should start on 2022-01-01 and end on 2100-12-31.",
            "Only one ensemble member is required.",
        ).strip(),
        forcing_headlines="The `scen7-vl` experiment is a time-varying forcings experiment.",
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(
            SCEN7_VL_FORCING_VERSIONS,
            include_multiple_options_note=False,
        ),
        getting_the_data=render_data_access_body(
            experiment_name="scen7-vl",
            source_ids=source_ids_from_forcing_versions(SCEN7_VL_FORCING_VERSIONS),
        ),
    ),
)
