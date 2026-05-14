"""ScenarioMIP experiment guidance pages."""

from __future__ import annotations

from local.guidance import (
    COMMON_FORCING_NOTES,
    SCEN7_VL_FORCING_VERSIONS,
    SETUP_GENERATION_TODO,
    ExperimentPage,
    branch_from,
    join_blocks,
    render_data_access_body,
    render_versions_body,
    source_ids_from_forcing_versions,
)

SCENARIOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="scen7-vl",
        title="scen7-vl Experiment Setup and Forcings Guidance",
        display_name="scen7-vl",
        responsible_activity="ScenarioMIP",
        description=(
            "PLACEHOLDER TBC. CMIP7 ScenarioMIP very low emissions future. "
            "Run with prescribed carbon dioxide concentrations "
            "(for prescribed carbon dioxide emissions, see `esm-scen7-vl`)."
        ),
        experiment_setup=join_blocks(
            "The CMIP7 very low scenario simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
            "The simulation output should start on 2022-01-01 and end on 2100-12-31.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="scen7-vl",
            parent="historical",
            parent_activity="CMIP",
            branch_instruction="Branch from `historical` at 2022-01-01.",
        ),
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
