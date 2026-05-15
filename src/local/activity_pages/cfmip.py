"""CFMIP experiment guidance pages."""

from __future__ import annotations

from local.forcing_versions import (
    PI_CONTROL_FORCING_VERSIONS,
    source_ids_from_forcing_versions,
)
from local.guidance import (
    ABRUPT_4XCO2_LINK,
    PI_CONTROL_LINK,
    TIME_AXIS_CAN_BE_ARBITRARY,
    ExperimentPage,
)
from local.rendering import (
    block,
    join_blocks,
    render_data_access_body,
    same_as_versions,
)

CFMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="abrupt-2xco2",
        experiment_setup=join_blocks(
            f"The abrupt CO<sub>2</sub> doubling simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to two times
                the concentrations used in the `piControl` simulation.
                """
            ),
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            "You have to double the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=render_data_access_body(
            experiment_name="abrupt-2xCO2",
            source_ids=source_ids_from_forcing_versions(PI_CONTROL_FORCING_VERSIONS),
        ),
    ),
    ExperimentPage(
        slug="abrupt-0p5xco2",
        experiment_setup=join_blocks(
            f"The abrupt CO<sub>2</sub> halving simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to half
                the concentrations used in the `piControl` simulation.
                """
            ),
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            "You have to halve the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=render_data_access_body(
            experiment_name="abrupt-0p5xCO2",
            source_ids=source_ids_from_forcing_versions(PI_CONTROL_FORCING_VERSIONS),
        ),
    ),
)
