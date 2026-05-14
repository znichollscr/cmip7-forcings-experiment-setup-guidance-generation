"""CFMIP experiment guidance pages."""

from __future__ import annotations

from local.guidance import (
    ABRUPT_4XCO2_LINK,
    EXPERIMENT_NAME_CONVENTION_TODO,
    PI_CONTROL_LINK,
    SETUP_GENERATION_TODO,
    TIME_AXIS_CAN_BE_ARBITRARY,
    ExperimentPage,
    block,
    branch_from,
    join_blocks,
    same_as_versions,
    see_instructions,
)

CFMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="abrupt-2xco2",
        title="abrupt-2xCO2 Experiment Setup and Forcings Guidance",
        display_name="abrupt-2xCO2",
        responsible_activity="CFMIP",
        description=(
            "Abrupt doubling of atmospheric carbon dioxide levels. "
            "All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The abrupt CO<sub>2</sub> doubling simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to two times
                the concentrations used in the `piControl` simulation.
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 300 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="abrupt-2xCO2",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=join_blocks(
            see_instructions("piControl simulation", "picontrol"),
            "You have to double the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
    ),
    ExperimentPage(
        slug="abrupt-0p5xco2",
        title="abrupt-0p5xCO2 Experiment Setup and Forcings Guidance",
        display_name="abrupt-0p5xCO2",
        responsible_activity="CFMIP",
        description=(
            "Abrupt halving of atmospheric carbon dioxide levels. "
            "All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The abrupt CO<sub>2</sub> halving simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to half
                the concentrations used in the `piControl` simulation.
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 300 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="abrupt-0p5xCO2",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=join_blocks(
            see_instructions("piControl simulation", "picontrol"),
            "You have to halve the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
    ),
)
