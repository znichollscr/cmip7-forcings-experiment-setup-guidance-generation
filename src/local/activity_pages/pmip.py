"""PMIP experiment guidance pages."""

from __future__ import annotations

from local.activity_pages.cmip import (
    picontrol_cmip_data_access_body,
)
from local.guidance import (
    PI_CONTROL_LINK,
    ExperimentPage,
)
from local.rendering import (
    block,
    join_blocks,
)
from local.vocab import get_experiment

PMIP_EXPERIMENT_PAGES = (
    ExperimentPage(
        slug="abrupt-127k",
        experiment_setup=join_blocks(
            f"The `{get_experiment('abrupt-127k').drs_name}` simulation is a branch from the {PI_CONTROL_LINK}. ",
            (
                f"It is recommended that you continue the time axis from the {PI_CONTROL_LINK} to make life easy for analysts "
                f"(rather than e.g. branching from the {PI_CONTROL_LINK} in year 100 "
                "and starting the time axis of `abrupt-127k` in year 1)."
            ),
        ),
        forcing_headlines=(
            f"The `{get_experiment('abrupt-127k').drs_name}` experiment is a fixed forcings experiment."
        ),
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            block(
                "After the branching point, the boundary conditions should be adjusted according to Table 1 of "
                "[Sime et al., 2025](https://egusphere.copernicus.org/preprints/2025/egusphere-2025-3531/). "
                "(Note that this paper is still under review, when it is published or there is an update, "
                "we will copy the table in here.) "
                "You have to make these adjustments yourself, there are no specific forcing files provided."
            ),
        ).strip(),
        versions_to_use=join_blocks(
            (
                "For all forcings, the "
                f"forcing versions relevant for this simulation are the same as "
                f"for the {PI_CONTROL_LINK}."
            ),
        ).strip(),
        getting_the_data=picontrol_cmip_data_access_body("abrupt-127k"),
    ),
)
