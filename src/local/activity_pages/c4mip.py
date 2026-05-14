"""C4MIP experiment guidance pages."""

from __future__ import annotations

from local.guidance import (
    EXPERIMENT_NAME_CONVENTION_TODO,
    ONEPCTCO2_LINK,
    SETUP_GENERATION_TODO,
    TIME_AXIS_CAN_BE_ARBITRARY,
    ExperimentPage,
    block,
    branch_from,
    join_blocks,
    same_as_versions,
    see_instructions,
)

C4MIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="1pctco2-bgc",
        title="1pctCO2-bgc Experiment Setup and Forcings Guidance",
        display_name="1pctCO2-bgc",
        responsible_activity="C4MIP",
        description=(
            "Biogeochemically coupled simulation (i.e. the carbon cycle only "
            "'sees' the increase in atmospheric carbon dioxide, not any change "
            "in temperature) of a 1% per year increase in atmospheric carbon "
            "dioxide levels. All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The 1pctCO2-bgc simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in atmospheric CO<sub>2</sub> concentrations
                and does not see any other changes (e.g. changes in atmospheric temperatures).
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 150 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="1pctCO2-bgc",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ONEPCTCO2_LINK}.",
        notes=f"See notes for the {ONEPCTCO2_LINK}.",
        versions_to_use=same_as_versions("1pctCO2 simulation", "1pctco2"),
        getting_the_data=see_instructions("1pctCO2 simulation", "1pctco2"),
    ),
    ExperimentPage(
        slug="1pctco2-rad",
        title="1pctCO2-rad Experiment Setup and Forcings Guidance",
        display_name="1pctCO2-rad",
        responsible_activity="C4MIP",
        description=(
            "Radiatively coupled simulation (i.e. the carbon cycle only 'sees' "
            "the increase in temperature, not any change in atmospheric carbon "
            "dioxide) of a 1% per year increase in atmospheric carbon dioxide "
            "levels. All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The 1pctCO2-rad simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in radiation
                and does not see any other changes (e.g. changes in atmospheric CO<sub>2</sub> concentrations).
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 150 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="1pctCO2-rad",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ONEPCTCO2_LINK}.",
        notes=f"See notes for the {ONEPCTCO2_LINK}.",
        versions_to_use=same_as_versions("1pctCO2 simulation", "1pctco2"),
        getting_the_data=see_instructions("1pctCO2 simulation", "1pctco2"),
    ),
)
