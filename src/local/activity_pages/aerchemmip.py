"""AerChemMIP experiment guidance pages."""

from __future__ import annotations

from local.forcing_versions import (
    cmip_forcing_ids_except,
    source_ids_for_cmip_forcing_combination,
)
from local.guidance import (
    AERCHEMMIP_UNCERTAIN_NOTE,
    HISTORICAL_LINK,
    PI_CONTROL_LINK,
    SETUP_GENERATION_TODO,
    ExperimentPage,
)
from local.piclim_variants import (
    HistoricalForcing,
    make_piclim_historical_forcing_variant_page,
)
from local.rendering import (
    block,
    join_blocks,
    join_lines,
    render_data_access_body,
)

AERCHEMMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_piclim_historical_forcing_variant_page(
        slug="piclim-ch4",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="greenhouse-gas-concentrations",
                label="methane concentrations or emissions (as appropriate for the model)",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-n2o",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="greenhouse-gas-concentrations",
                label="nitrous oxide concentrations or emissions (as appropriate for the model)",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-nox",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="anthropogenic-emissions",
                label="nitrogen oxides (NOx) emissions",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-ods",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="greenhouse-gas-concentrations",
                label="ozone-depleting substance concentrations",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-so2",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="anthropogenic-emissions",
                label="sulfur dioxide (SO<sub>2</sub>) emissions",
            ),
        ),
    ),
    ExperimentPage(
        slug="hist-piaer",
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
        experiment_setup=join_blocks(
            # TODO: remove this
            "<!-- TODO: check this with someone who knows what they're reading -->",
            # TODO: Get this from esgvoc instead
            block(
                """
                The `hist-piAer` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAer` is for models that do not include interactive chemistry.
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
        getting_the_data=render_data_access_body(
            experiment_name="hist-piAer",
            source_ids=source_ids_for_cmip_forcing_combination(
                fixed_forcing_ids=("anthropogenic-emissions",),
                transient_forcing_ids=cmip_forcing_ids_except(
                    "anthropogenic-emissions",
                    "aerosol-optical-properties",
                ),
            ),
        ),
    ),
    ExperimentPage(
        slug="hist-piaq",
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
        experiment_setup=join_blocks(
            # TODO: remove this
            "<!-- TODO: check this with someone who knows what they're reading -->",
            # TODO: Get this from esgvoc instead
            block(
                """
                The `hist-piAQ` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAQ` is for models that include interactive chemistry.
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
        getting_the_data=render_data_access_body(
            experiment_name="hist-piAQ",
            source_ids=source_ids_for_cmip_forcing_combination(
                fixed_forcing_ids=("anthropogenic-emissions",),
                transient_forcing_ids=cmip_forcing_ids_except(
                    "anthropogenic-emissions",
                    "aerosol-optical-properties",
                ),
            ),
        ),
    ),
)
