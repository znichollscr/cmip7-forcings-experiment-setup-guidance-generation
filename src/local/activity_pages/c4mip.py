"""C4MIP experiment guidance pages."""

from __future__ import annotations

from local.forcing_versions import (
    PI_CONTROL_FORCING_VERSIONS,
    source_ids_from_forcing_versions,
)
from local.guidance import (
    ONEPCTCO2_LINK,
    TIME_AXIS_CAN_BE_ARBITRARY,
    ExperimentPage,
)
from local.rendering import (
    block,
    join_blocks,
    render_data_access_body,
    same_as_versions,
)

C4MIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="1pctco2-bgc",
        experiment_setup=join_blocks(
            f"The 1pctCO2-bgc simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in atmospheric CO<sub>2</sub> concentrations
                and does not see any other changes (e.g. changes in atmospheric temperatures).
                """
            ),
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=f"See general headlines for the {ONEPCTCO2_LINK}.",
        notes=f"See notes for the {ONEPCTCO2_LINK}.",
        versions_to_use=same_as_versions("1pctCO2 simulation", "1pctco2"),
        getting_the_data=render_data_access_body(
            experiment_name="1pctCO2-bgc",
            source_ids=source_ids_from_forcing_versions(PI_CONTROL_FORCING_VERSIONS),
        ),
    ),
    ExperimentPage(
        slug="1pctco2-rad",
        experiment_setup=join_blocks(
            f"The 1pctCO2-rad simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in radiation
                and does not see any other changes (e.g. changes in atmospheric CO<sub>2</sub> concentrations).
                """
            ),
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=f"See general headlines for the {ONEPCTCO2_LINK}.",
        notes=f"See notes for the {ONEPCTCO2_LINK}.",
        versions_to_use=same_as_versions("1pctCO2 simulation", "1pctco2"),
        getting_the_data=render_data_access_body(
            experiment_name="1pctCO2-rad",
            source_ids=source_ids_from_forcing_versions(PI_CONTROL_FORCING_VERSIONS),
        ),
    ),
)
