"""AerChemMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import branch_from
from local.guidance import (
    AERCHEMMIP_UNCERTAIN_NOTE,
    EXPERIMENT_NAME_CONVENTION_TODO,
    HISTORICAL_LINK,
    PI_CONTROL_LINK,
    SETUP_GENERATION_TODO,
    ExperimentPage,
    make_piclim_variant_page,
)
from local.rendering import (
    block,
    join_blocks,
    join_lines,
)

AERCHEMMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_piclim_variant_page(
        slug="piclim-ch4",
        title="piClim-CH4 Experiment Setup and Forcings Guidance",
        display_name="piClim-CH4",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day methane effective radiative forcing (ERF).
            Same as `piClim-control`, except methane concentrations or emissions (as appropriate for the model) use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=(
            "except the atmospheric methane concentration forcing uses 2021 values."
        ),
        version_forcing_label="methane forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-n2o",
        title="piClim-N2O Experiment Setup and Forcings Guidance",
        display_name="piClim-N2O",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day nitrous oxide effective radiative forcing (ERF).
            Same as `piClim-control`, except nitrous oxide concentrations or emissions (as appropriate for the model) use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=(
            "except the atmospheric nitrous oxide concentration forcing uses 2021 values."
        ),
        version_forcing_label="nitrous oxide forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-nox",
        title="piClim-NOx Experiment Setup and Forcings Guidance",
        display_name="piClim-NOx",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day nitrogen oxides (NOx) effective radiative forcing (ERF).
            Same as `piClim-control`, except nitrogen oxides (NOx) emissions use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change="except the NOx emissions forcing uses 2021 values.",
        version_forcing_label="nitrogen oxides (NOx) forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-ods",
        title="piClim-ODS Experiment Setup and Forcings Guidance",
        display_name="piClim-ODS",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day ozone-depleting substances' effective radiative forcing (ERF).
            Same as `piClim-control`, except ozone-depleting substances concentrations use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=join_blocks(
            "except emissions of ozone-depleting substances use 2021 values.",
            "<!-- TODO: check the above, I don't think this is correct... -->",
        ).strip(),
        version_forcing_label="ozone-depleting substance forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-so2",
        title="piClim-SO2 Experiment Setup and Forcings Guidance",
        display_name="piClim-SO2",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day sulfur (dioxide) effective radiative forcing (ERF).
            Same as `piClim-control`, except sulfur emissions use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=(
            "except emissions of sulfur dioxide (SO<sub>2</sub>) use 2021 values."
        ),
        version_forcing_label="sulfur dioxide (SO2) emissions",
    ),
    ExperimentPage(
        slug="hist-piaer",
        title="hist-piAer Experiment Setup and Forcings Guidance",
        display_name="hist-piAer",
        responsible_activity="AerChemMIP",
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
        description=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            (
                "In combination with `historical`, allows for evaluation of "
                "the air quality and climate effect of historical aerosol and "
                "tropospheric non-methane ozone precursor emissions in models "
                "without interactive chemistry (for models with interactive "
                "chemistry, see `hist-piAQ`)."
            ),
        ).strip(),
        experiment_setup=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            EXPERIMENT_NAME_CONVENTION_TODO,
            block(
                """
                The `hist-piAer` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAer` is for models that do not include interactive chemistry.
                For models with interactive chemistry, please see [hist-piAQ](./hist-piaq.md) instead.
                """
            ),
            SETUP_GENERATION_TODO,
            "The simulation output should start on 1850-01-01 and end on 2021-12-31.",
            "<!-- TODO: double check, dunne et al. says 6?! -->",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="hist-piAer",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
            extra=(
                "This branch time should match the branch time used for "
                f"initialising the {HISTORICAL_LINK}."
            ),
        ),
        forcing_headlines=block(
            """
            The `hist-piAer` experiment is a time-varying forcings experiment,
            except for aerosol and tropospheric non-methane ozone precursor emissions which should be fixed.
            """
        ),
        notes=f"See notes for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
        versions_to_use=join_blocks(
            join_lines(
                "For aerosol and tropospheric non-methane ozone precursor emissions",
                f"the relevant forcing is the same as for the {PI_CONTROL_LINK}.",
            ),
            join_lines(
                "For all other forcings,",
                f"the forcing versions relevant for this simulation are the same as for the {HISTORICAL_LINK}.",
            ),
        ).strip(),
        getting_the_data=f"See instructions for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="hist-piaq",
        title="hist-piAQ Experiment Setup and Forcings Guidance",
        display_name="hist-piAQ",
        responsible_activity="AerChemMIP",
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
        description=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            (
                "In combination with `historical`, allows for evaluation of "
                "the air quality and climate effect of historical aerosol and "
                "tropospheric non-methane ozone precursor emissions in models "
                "with interactive chemistry (for models without interactive "
                "chemistry, see `hist-piAer`)."
            ),
        ).strip(),
        experiment_setup=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            EXPERIMENT_NAME_CONVENTION_TODO,
            block(
                """
                The `hist-piAQ` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAQ` is for models that include interactive chemistry.
                For models without interactive chemistry, please see [hist-piAer](./hist-piaer.md) instead.
                """
            ),
            SETUP_GENERATION_TODO,
            "The simulation output should start on 1850-01-01 and end on 2021-12-31.",
            "<!-- TODO: double check, dunne et al. says 6?! -->",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="hist-piAQ",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
            extra=(
                "This branch time should match the branch time used for "
                f"initialising the {HISTORICAL_LINK}."
            ),
        ),
        forcing_headlines=block(
            """
            The `hist-piAQ` experiment is a time-varying forcings experiment,
            except for aerosol and tropospheric non-methane ozone precursor emissions which should be fixed.
            """
        ),
        notes=f"See notes for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
        versions_to_use=join_blocks(
            join_lines(
                "For aerosol and tropospheric non-methane ozone precursor emissions",
                f"the relevant forcing is the same as for the {PI_CONTROL_LINK}.",
            ),
            join_lines(
                "For all other forcings,",
                f"the forcing versions relevant for this simulation are the same as for the {HISTORICAL_LINK}.",
            ),
        ).strip(),
        getting_the_data=f"See instructions for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
)
