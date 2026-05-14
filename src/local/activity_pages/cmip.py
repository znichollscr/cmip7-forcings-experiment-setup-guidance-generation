"""CMIP experiment guidance pages."""

from __future__ import annotations

from local.forcing_references import AMIP_FORCING_REFERENCES, COMMON_FORCING_NOTES
from local.forcing_versions import (
    AMIP_FORCING_VERSIONS,
    CMIP_FIXED_FORCING_VERSIONS,
    CMIP_FORCING_VERSIONS,
    source_ids_from_forcing_versions,
)
from local.guidance import (
    HISTORICAL_LINK,
    PI_CLIM_CONTROL_LINK,
    PI_CONTROL_LINK,
    PICLIM_TIME_AXIS,
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

FIXED_FORCINGS_REPEAT_SETUP = join_blocks(
    "These should be applied on repeat for the entirety of the simulation.",
    block(
        """
        You are free to start the time axis of your outputs at whatever year you like
        (e.g. starting at year 1, or 1850, or year 500).
        """
    ),
).strip()
TRANSIENT_FORCINGS_SETUP_TAIL = "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation."
PICLIM_PRESCRIBED_SST_SIC_FORCING_NOTE = block(
    """
    As noted above, the prescribed sea-surface temperatures and sea-ice concentrations
    must come from model output from one of your own simulations,
    they are not provided by a forcings provider.
    """
)
PI_CONTROL_OZONE_FORCING_NOTE = block(
    """
    Please note that the ozone forcing should come from files with the source ID `FZJ-CMIP-ozone-1-2`,
    no `piControl` data is included in `FZJ-CMIP-ozone-2-0`
    (which only updates `historical` values).
    """
)
HISTORICAL_OZONE_FORCING_NOTE = block(
    """
    Please note that the ozone forcing should come from files with the source ID `FZJ-CMIP-ozone-2-0`:
    the CMIP Panel co-chairs are recommending that simulations based on `FZJ-CMIP-ozone-1-2` are re-run if possible.
    `FZJ-CMIP-ozone-2-0` was released quite late, so if you have simulations based on `FZJ-CMIP-ozone-1-2`,
    these would be of interest to the Forcings Task Team so please publish them
    ([discussion of how to set the value for the forcing 'f' identifier in such files is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415)).
    """
)
NITROGEN_DEPOSITION_FORCING_NOTE = block(
    """
    Please also note that the nitrogen deposition forcing should come from files with the source ID `FZJ-CMIP-nitrogen-2-0`.
    `FZJ-CMIP-nitrogen-2-0` was released quite late and the impact of the change is likely to be small,
    so if you have simulations based on `FZJ-CMIP-nitrogen-1-2`,
    you do not need to re-run them.
    """
)
HISTORICAL_NITROGEN_DEPOSITION_RECOMMENDATION = block(
    """
    Further, even if you have run pre-industrial control simulations with `FZJ-CMIP-nitrogen-1-2`,
    it is recommended to nonetheless run historical simulations with `FZJ-CMIP-nitrogen-2-0`
    because the discontinuity going from pre-industrial control `FZJ-CMIP-nitrogen-1-2`
    to historical `FZJ-CMIP-nitrogen-2-0` is expected to introduce smaller issues
    than using `FZJ-CMIP-nitrogen-1-2` over the historical period.
    """
)
READ_FORCING_NOTES_GUIDANCE = block(
    """
    Please read the guidance pages linked under [notes](#notes)
    to ensure that you use the correct forcing values.
    """
)
CMIP_FIXED_VERSIONS_TO_USE = render_versions_body(CMIP_FIXED_FORCING_VERSIONS)
CMIP_TRANSIENT_VERSIONS_TO_USE = render_versions_body(CMIP_FORCING_VERSIONS)


def fixed_forcings_setup(first_sentence: str) -> str:
    """Render setup guidance for a fixed-forcings CMIP experiment."""
    return join_blocks(first_sentence, FIXED_FORCINGS_REPEAT_SETUP).strip()


def transient_forcings_setup(simulation_label: str) -> str:
    """Render setup guidance for a transient-forcings CMIP experiment."""
    return join_blocks(
        f"The {simulation_label} uses a specific set of forcings (see [forcings](#forcings)).",
        TRANSIENT_FORCINGS_SETUP_TAIL,
    ).strip()


def fixed_cmip_data_access_body(experiment_name: str) -> str:
    """Render the data-access body for fixed CMIP forcings."""
    return render_data_access_body(
        experiment_name=experiment_name,
        source_ids=fixed_cmip_source_ids(),
    )


def transient_cmip_data_access_body(experiment_name: str) -> str:
    """Render the data-access body for transient CMIP forcings."""
    return cmip_data_access_body(experiment_name)


def cmip_data_access_body(experiment_name: str) -> str:
    """Render the data-access body for CMIP forcing versions."""
    return render_data_access_body(
        experiment_name=experiment_name,
        source_ids=cmip_source_ids(),
    )


def fixed_cmip_source_ids() -> tuple[str, ...]:
    """Return source IDs for fixed CMIP forcings."""
    return source_ids_from_forcing_versions(CMIP_FIXED_FORCING_VERSIONS)


def cmip_source_ids() -> tuple[str, ...]:
    """Return source IDs for CMIP forcing versions."""
    return source_ids_from_forcing_versions(CMIP_FORCING_VERSIONS)


def fixed_forcing_headlines(
    experiment_name: str,
    *,
    forcing_values_experiment_name: str | None = None,
) -> str:
    """Render shared fixed-forcings headlines."""
    forcing_values_experiment_name = forcing_values_experiment_name or experiment_name
    return join_blocks(
        block(
            f"""
        The `{experiment_name}` experiment is a fixed forcings experiment.

        However, it can require some care to use the correct forcings for `{forcing_values_experiment_name}`.
        This is particularly true for stratospheric aerosol forcing, ozone and solar
        as the `{forcing_values_experiment_name}` values for these forcings aren't simply a repeat of 1850 values.
        """
        ),
        PI_CONTROL_OZONE_FORCING_NOTE,
        NITROGEN_DEPOSITION_FORCING_NOTE,
        READ_FORCING_NOTES_GUIDANCE,
    ).strip()


def historical_forcing_headlines(experiment_name: str) -> str:
    """Render shared historical-forcings headlines."""
    return join_blocks(
        block(
            f"""
        The `{experiment_name}` experiment is a time-varying forcings experiment.
        """
        ),
        HISTORICAL_OZONE_FORCING_NOTE,
        NITROGEN_DEPOSITION_FORCING_NOTE,
        HISTORICAL_NITROGEN_DEPOSITION_RECOMMENDATION,
        READ_FORCING_NOTES_GUIDANCE,
    ).strip()


def make_fixed_control_page(
    *,
    slug: str,
    experiment_name: str,
    simulation_label: str,
    setup_forcing_description: str,
    forcing_values_experiment_name: str | None = None,
) -> ExperimentPage:
    """Create a fixed pre-industrial control page."""
    return ExperimentPage(
        slug=slug,
        experiment_setup=fixed_forcings_setup(
            f"The {simulation_label} uses {setup_forcing_description} (see [forcings](#forcings))."
        ),
        forcing_headlines=fixed_forcing_headlines(
            experiment_name,
            forcing_values_experiment_name=forcing_values_experiment_name,
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=CMIP_FIXED_VERSIONS_TO_USE,
        getting_the_data=fixed_cmip_data_access_body(experiment_name),
    )


def make_picontrol_spinup_page(
    *,
    slug: str,
    experiment_name: str,
    simulation_label: str,
    forcing_values_experiment_name: str,
) -> ExperimentPage:
    """Create a piControl spin-up page."""
    return make_fixed_control_page(
        slug=slug,
        experiment_name=experiment_name,
        simulation_label=simulation_label,
        setup_forcing_description="fixed pre-industrial forcings",
        forcing_values_experiment_name=forcing_values_experiment_name,
    )


def make_historical_page(
    *,
    slug: str,
    experiment_name: str,
    simulation_label: str,
) -> ExperimentPage:
    """Create a historical page."""
    return ExperimentPage(
        slug=slug,
        experiment_setup=transient_forcings_setup(simulation_label),
        forcing_headlines=historical_forcing_headlines(experiment_name),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=CMIP_TRANSIENT_VERSIONS_TO_USE,
        getting_the_data=transient_cmip_data_access_body(experiment_name),
    )


CMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_picontrol_spinup_page(
        slug="picontrol-spinup",
        experiment_name="piControl-spinup",
        simulation_label="pre-industrial control spin-up simulation",
        forcing_values_experiment_name="piControl",
    ),
    make_fixed_control_page(
        slug="picontrol",
        experiment_name="piControl",
        simulation_label="pre-industrial control simulation",
        setup_forcing_description="a specific set of forcings",
    ),
    make_picontrol_spinup_page(
        slug="esm-picontrol-spinup",
        experiment_name="esm-piControl-spinup",
        simulation_label="emissions-driven pre-industrial control spin-up simulation",
        forcing_values_experiment_name="esm-piControl",
    ),
    make_fixed_control_page(
        slug="esm-picontrol",
        experiment_name="esm-piControl",
        simulation_label="emissions-driven pre-industrial control simulation",
        setup_forcing_description="a specific set of forcings",
    ),
    make_historical_page(
        slug="historical",
        experiment_name="historical",
        simulation_label="historical simulation",
    ),
    make_historical_page(
        slug="esm-hist",
        experiment_name="esm-hist",
        simulation_label="emissions-driven historical simulation",
    ),
    ExperimentPage(
        slug="1pctco2",
        experiment_setup=join_blocks(
            f"The 1pctCO2 simulation is a simple branch from the {PI_CONTROL_LINK}.",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should increase at one percent per year throughout the simulation.",
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=(
            "The `1pctCO2` experiment is a fixed forcings experiment, "
            "except for CO<sub>2</sub> which is transient."
        ),
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
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
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=fixed_cmip_data_access_body("1pctCO2"),
    ),
    ExperimentPage(
        slug="abrupt-4xco2",
        experiment_setup=join_blocks(
            f"The abrupt CO<sub>2</sub> quadrupling simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to four times
                the concentrations used in the `piControl` simulation.
                """
            ),
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=(
            "The `abrupt-4xCO2` experiment is a fixed forcings experiment.\n"
            f"For further general headlines, please see the general headlines for the {PI_CONTROL_LINK}."
        ),
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            "You have to quadruple the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=fixed_cmip_data_access_body("abrupt-4xCO2"),
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
            join_lines(
                PICLIM_PRESCRIBED_SST_SIC_FORCING_NOTE,
                block(
                    """
                We recommend including information in your `piClim-control` output
                that identifies the `piControl` simulation and time period used to generate
                the prescribed sea-surface temperatures and sea-ice concentrations.
                """
                ),
            ),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name="piClim-control",
            source_ids=fixed_cmip_source_ids(),
            extra=PICLIM_PRESCRIBED_SST_SIC_FORCING_NOTE,
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
            PICLIM_TIME_AXIS,
        ).strip(),
        forcing_headlines=(
            "See general headlines for the "
            "[`piClim-control` simulation](./piclim-control.md)."
        ),
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=(
            f"{same_as_versions('piClim-control simulation', 'piclim-control')} "
            "You have to quadruple the CO2 concentrations yourself."
        ),
        getting_the_data=render_data_access_body(
            experiment_name="piClim-4xCO2",
            source_ids=fixed_cmip_source_ids(),
            extra=join_blocks(
                "You have to quadruple the atmospheric CO<sub>2</sub> concentrations yourself.",
                PICLIM_PRESCRIBED_SST_SIC_FORCING_NOTE,
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
        experiment_setup=transient_forcings_setup("amip simulation"),
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
            render_versions_json(AMIP_FORCING_VERSIONS),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name="amip",
            source_ids=source_ids_from_forcing_versions(
                AMIP_FORCING_VERSIONS,
                CMIP_FORCING_VERSIONS,
            ),
        ),
    ),
)
