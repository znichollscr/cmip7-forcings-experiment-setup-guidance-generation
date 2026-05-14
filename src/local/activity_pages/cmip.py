"""CMIP experiment guidance pages."""

from __future__ import annotations

from local.forcing_references import AMIP_FORCING_REFERENCES, COMMON_FORCING_NOTES
from local.forcing_versions import (
    AMIP_FORCING_VERSIONS,
    CMIP_FIXED_SOURCE_ID_INDEXES,
    CMIP_FORCING_VERSIONS,
    CMIP_TRANSIENT_SOURCE_ID_INDEXES,
    source_ids_from_forcing_versions,
)
from local.guidance import (
    EXPERIMENT_NAME_CONVENTION_TODO,
    HISTORICAL_LINK,
    PI_CLIM_CONTROL_LINK,
    PI_CONTROL_LINK,
    PICLIM_TIME_AXIS,
    SETUP_GENERATION_TODO,
    TIME_AXIS_CAN_BE_ARBITRARY,
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
    render_versions_body,
    render_versions_json,
    same_as_versions,
)

CMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="picontrol",
        experiment_setup=join_blocks(
            "The pre-industrial control simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied on repeat for the entirety of the simulation.",
            SETUP_GENERATION_TODO,
            block(
                """
                You are free to start the time axis of your outputs at whatever year you like
                (e.g. starting at year 1, or 1850, or year 500).
                """
            ),
        ).strip(),
        forcing_headlines=block(
            """
            The `piControl` experiment is a fixed forcings experiment.
            However, it can require some care to use the correct forcings for `piControl`.
            This is particularly true for stratospheric aerosol forcing, ozone and solar
            as the `piControl` values for these forcings aren't simply a repeat of 1850 values.
            Please read the guidance pages linked under [notes](#notes)
            to ensure that you use the correct forcing values.
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="piControl",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="esm-picontrol",
        experiment_setup=join_blocks(
            "The emissions-driven pre-industrial control simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied on repeat for the entirety of the simulation.",
            SETUP_GENERATION_TODO,
            block(
                """
                You are free to start the time axis of your outputs at whatever year you like
                (e.g. starting at year 1, or 1850, or year 500).
                """
            ),
        ).strip(),
        forcing_headlines=block(
            """
            The `esm-piControl` experiment is a fixed forcings experiment.
            However, it can require some care to use the correct forcings for `esm-piControl`.
            This is particularly true for stratospheric aerosol forcing, ozone and solar
            as the `esm-piControl` values for these forcings aren't simply a repeat of 1850 values.
            Please read the guidance pages linked under [notes](#notes)
            to ensure that you use the correct forcing values.
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="esm-piControl",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="historical",
        experiment_setup=join_blocks(
            "The historical simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
        ).strip(),
        forcing_headlines=block(
            """
            The `historical` experiment is a time-varying forcings experiment.
            Please note that the ozone forcing should come from files with the source ID `FZJ-CMIP-ozone-2-0`.
            `FZJ-CMIP-ozone-2-0` was released quite late, so if you have simulations based on `FZJ-CMIP-ozone-1-2`,
            these would also be of interest to the Forcings Task Team so please publish them
            ([discussion of how to set the value for the forcing 'f' identifier in such files is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415)).
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="historical",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_TRANSIENT_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="esm-hist",
        experiment_setup=join_blocks(
            "The emissions-driven historical simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
        ).strip(),
        forcing_headlines=block(
            """
            The `esm-hist` experiment is a time-varying forcings experiment.
            Please note that the ozone forcing should come from files with the source ID `FZJ-CMIP-ozone-2-0`.
            `FZJ-CMIP-ozone-2-0` was released quite late, so if you have simulations based on `FZJ-CMIP-ozone-1-2`,
            these would also be of interest to the Forcings Task Team so please publish them
            ([discussion of how to set the value for the forcing 'f' identifier in such files is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415)).
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="esm-hist",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_TRANSIENT_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="1pctco2",
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The 1pctCO2 simulation is a simple branch from the {PI_CONTROL_LINK}.",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should increase at one percent per year throughout the simulation.",
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=(
            "The `1pctCO2` experiment is a fixed forcings experiment, "
            "except for CO<sub>2</sub> which is transient."
        ),
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=render_data_access_body(
            experiment_name="1pctCO2",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
            extra=join_blocks(
                "You have to increase the atmospheric CO<sub>2</sub> concentrations at one percent per year yourself.",
                block(
                    """
                    <!---
                        TODO: discuss with Matt/someone else the specific implementation instructions.
                        Set concentrations in first year to be higher than piControl
                        (because, if you don't do this and you have a linear increase,
                        then you'd have to drop concentrations in January of the first year in order to get the average correct)
                        TODO: check formula rendering
                    -->
                    The annual-average concentrations should increase following the formula c(y) = c_0 * 1.01 ** (y - y_0 - 1),
                    where c is the annual-average concentration in year y and y_0 is the first year of the `1pctCO2` simulation
                    (i.e. average atmospheric CO<sub>2</sub> concentrations in the first year of the `1pctCO2` simulation
                    should be higher than in `piControl`).
                    It is up to you to decide whether you apply your concentrations as a series of step changes
                    (constant over each year) or as a steady linear increase
                    (such that e.g. concentrations in December are higher than those in January)
                    that results in the correct annual average being applied.
                    """
                ),
            ).strip(),
        ),
    ),
    ExperimentPage(
        slug="abrupt-4xco2",
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The abrupt CO<sub>2</sub> quadrupling simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to four times
                the concentrations used in the `piControl` simulation.
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=(
            "The `abrupt-4xCO2` experiment is a fixed forcings experiment.\n"
            f"For further general headlines, please see the general headlines for the {PI_CONTROL_LINK}."
        ),
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=render_data_access_body(
            experiment_name="abrupt-4xCO2",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
            extra="You have to quadruple the atmospheric CO<sub>2</sub> concentrations yourself.",
        ),
    ),
    ExperimentPage(
        slug="piclim-control",
        experiment_setup=join_blocks(
            join_lines(
                "The piClim-control simulation uses the same forcings as [piControl](./picontrol.md),",
                "with the extra specification that sea-surface temperatures and sea-ice concentrations are prescribed.",
            ),
            block(
                """
                The prescribed sea-surface temperatures and sea-ice concentrations
                must come from a (monthly varying, annually repeating)
                climatology taken from at least 30 years of your [pre-industrial control](./picontrol.md) simulation
                (i.e. these forcings are derived from your model output from one of your own simulations,
                they are not provided by a forcings provider).
                """
            ),
            SETUP_GENERATION_TODO,
            block(
                """
                The start-time of the simulation is not tied to a particular year but, rather, can be chosen arbitrarily
                (e.g., year 200 or year 1850 or year 1).
                If you have no other strong feeling, then it may be clearest to set the start-time
                to be equal to the middle of the period over which the climatology was taken from the pre-industrial control experiment.
                For example, if your climatology is taken over the years 120-150 in the pre-industrial control experiment,
                then you could start the time axis of your `piClim-control` at 135.
                """
            ),
        ).strip(),
        forcing_headlines=(
            "The `piClim-control` experiment is a fixed forcings experiment.\n"
            f"For further general headlines, please see the general headlines for the {PI_CONTROL_LINK}."
        ),
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=join_blocks(
            same_as_versions("piControl simulation", "picontrol"),
            block(
                """
                As noted above, the prescribed sea-surface temperatures and sea-ice concentrations
                must come from model output from one of your own simulations,
                they are not provided by a forcings provider.
                We recommend including information in your `piClim-control` output
                that identifies the `piControl` simulation and time period used to generate
                the prescribed sea-surface temperatures and sea-ice concentrations.
                """
            ),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name="piClim-control",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
            extra=block(
                """
                As noted above, the prescribed sea-surface temperatures and sea-ice concentrations
                must come from model output from one of your own simulations,
                they are not provided by a forcings provider.
                """
            ),
        ),
    ),
    ExperimentPage(
        slug="piclim-4xco2",
        experiment_setup=join_blocks(
            join_lines(
                "The piClim-4xCO2 simulation uses the same forcings as [piClim-control](./piclim-control.md),",
                block(
                    """
                    except atmospheric CO<sub>2</sub> concentrations
                    are set to four times the concentrations used in the [piClim-control](./piclim-control.md) simulation.
                    """
                ),
            ),
            SETUP_GENERATION_TODO,
            PICLIM_TIME_AXIS,
        ).strip(),
        forcing_headlines=(
            "See general headlines for the "
            "[`piClim-control` simulation](./piclim-control.md)."
        ),
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piClim-control simulation", "piclim-control"),
        getting_the_data=render_data_access_body(
            experiment_name="piClim-4xCO2",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
            extra=join_blocks(
                "You have to quadruple the atmospheric CO<sub>2</sub> concentrations yourself.",
                block(
                    """
                    As noted above, the prescribed sea-surface temperatures and sea-ice concentrations
                    must come from model output from one of your own simulations,
                    they are not provided by a forcings provider.
                    """
                ),
            ).strip(),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-anthro",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="anthropogenic-emissions",
                label="anthropogenic emissions",
            ),
            HistoricalForcing(
                forcing_id="biomass-burning-emissions",
                label="biomass-burning emissions",
            ),
            HistoricalForcing(
                forcing_id="land-use",
                label="land-use forcing",
            ),
            HistoricalForcing(
                forcing_id="greenhouse-gas-concentrations",
                label="greenhouse-gas concentrations",
            ),
            HistoricalForcing(
                forcing_id="ozone",
                label="ozone",
            ),
            HistoricalForcing(
                forcing_id="nitrogen-deposition",
                label="nitrogen deposition",
            ),
            HistoricalForcing(
                forcing_id="population-density",
                label="population density",
            ),
        ),
        extra_setup=(
            "Solar and stratospheric aerosol forcing should remain as in "
            "[piClim-control](./piclim-control.md)."
        ),
    ),
    ExperimentPage(
        slug="amip",
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            "The amip simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
        ).strip(),
        forcing_headlines="The `amip` experiment is a time-varying forcings experiment.",
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            (
                "The following pages give further information on each forcing "
                f"beyond the ones used in the {HISTORICAL_LINK}:"
            ),
            "\n".join(
                f"- {reference.label}: [{reference.display_url}]({reference.url})"
                for reference in AMIP_FORCING_REFERENCES
            ),
        ).strip(),
        versions_to_use=join_blocks(
            join_lines(
                f"The forcings relevant for this simulation are the same as for the {HISTORICAL_LINK}",
                "with the addition of the SST and sea-ice forcing.",
                (
                    'For this additional forcing, we provide the version(s), in the form of "source ID(s)",'
                ),
                "which should be used when running this simulation.",
                f"For all other forcings, please see the information on the {HISTORICAL_LINK} page.",
            ),
            "<!-- TODO: auto-generate and just duplicate the information rather than forcing people to other pages -->",
            render_versions_json(AMIP_FORCING_VERSIONS),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name="amip",
            source_ids=source_ids_from_forcing_versions(
                AMIP_FORCING_VERSIONS,
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_TRANSIENT_SOURCE_ID_INDEXES,
            ),
        ),
    ),
)
