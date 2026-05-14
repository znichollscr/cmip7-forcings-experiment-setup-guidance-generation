"""AerChemMIP experiment guidance pages."""

from __future__ import annotations

from local.guidance import (
    AERCHEMMIP_UNCERTAIN_NOTE,
    EXPERIMENT_NAME_CONVENTION_TODO,
    HISTORICAL_LINK,
    PI_CLIM_CONTROL_LINK,
    PI_CONTROL_LINK,
    PICLIM_TIME_AXIS,
    SETUP_GENERATION_TODO,
    ExperimentPage,
)
from local.rendering import (
    block,
    join_blocks,
    join_lines,
)

PICLIM_PRESENT_DAY_VARIANT_SETUP = join_blocks(
    (
        "This simulation uses the same forcings as "
        "[piClim-control](./piclim-control.md), except the present-day forcing "
        "identified in the CMIP7 CV description above uses 2021 values."
    ),
    "The 2021 values should be prescribed on repeat throughout the simulation.",
    SETUP_GENERATION_TODO,
    PICLIM_TIME_AXIS,
).strip()

PICLIM_PRESENT_DAY_VARIANT_HEADLINES = (
    "See general headlines for the "
    "[`piClim-control` simulation](./piclim-control.md)."
)

PICLIM_PRESENT_DAY_VARIANT_VERSIONS = join_blocks(
    join_lines(
        "For the present-day forcing identified in the CMIP7 CV description above,",
        f"the forcing version relevant for this simulation is the same as for the {HISTORICAL_LINK}.",
    ),
    join_lines(
        "For all other forcings,",
        f"the forcing versions relevant for this simulation are the same as for the {PI_CLIM_CONTROL_LINK}.",
    ),
).strip()

AERCHEMMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="piclim-ch4",
        experiment_setup=PICLIM_PRESENT_DAY_VARIANT_SETUP,
        forcing_headlines=PICLIM_PRESENT_DAY_VARIANT_HEADLINES,
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=PICLIM_PRESENT_DAY_VARIANT_VERSIONS,
        getting_the_data=f"See instructions for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="piclim-n2o",
        experiment_setup=PICLIM_PRESENT_DAY_VARIANT_SETUP,
        forcing_headlines=PICLIM_PRESENT_DAY_VARIANT_HEADLINES,
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=PICLIM_PRESENT_DAY_VARIANT_VERSIONS,
        getting_the_data=f"See instructions for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="piclim-nox",
        experiment_setup=PICLIM_PRESENT_DAY_VARIANT_SETUP,
        forcing_headlines=PICLIM_PRESENT_DAY_VARIANT_HEADLINES,
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=PICLIM_PRESENT_DAY_VARIANT_VERSIONS,
        getting_the_data=f"See instructions for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="piclim-ods",
        experiment_setup=PICLIM_PRESENT_DAY_VARIANT_SETUP,
        forcing_headlines=PICLIM_PRESENT_DAY_VARIANT_HEADLINES,
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=PICLIM_PRESENT_DAY_VARIANT_VERSIONS,
        getting_the_data=f"See instructions for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="piclim-so2",
        experiment_setup=PICLIM_PRESENT_DAY_VARIANT_SETUP,
        forcing_headlines=PICLIM_PRESENT_DAY_VARIANT_HEADLINES,
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=PICLIM_PRESENT_DAY_VARIANT_VERSIONS,
        getting_the_data=f"See instructions for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="hist-piaer",
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
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
        ).strip(),
        parent_experiment_extra=(
            "This branch time should match the branch time used for "
            f"initialising the {HISTORICAL_LINK}."
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
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
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
        ).strip(),
        parent_experiment_extra=(
            "This branch time should match the branch time used for "
            f"initialising the {HISTORICAL_LINK}."
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
