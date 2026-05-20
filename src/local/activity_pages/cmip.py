"""CMIP experiment guidance pages."""

from __future__ import annotations

from functools import partial
from textwrap import indent

from local.branching import BranchAtSameTimeAsOtherExperiment, BranchFromParentAtAnyTime
from local.forcing_references import COMMON_FORCING_NOTES
from local.forcing_versions import (
    HISTORICAL_FORCING_VERSIONS,
    PI_CONTROL_FORCING_VERSIONS,
    source_ids_from_forcing_versions,
)
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    HISTORICAL_FORCINGS_SPECIFICATION_AMIP_SSTS,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    NonInput4MIPsBasedForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    PI_CONTROL_LINK,
    ExperimentPage,
    ExperimentPageOld,
)
from local.output_time_axis import PiClimOutputTimeAxisInformation
from local.rendering import (
    block,
    join_blocks,
    only_keep_first_sentence,
    render_data_access_body,
    render_link,
    render_versions_body,
)
from local.vocab import get_experiment

PI_CONTROL_FORCINGS_REPEAT_SETUP = join_blocks(
    "These should be applied on repeat for the entirety of the simulation.",
    block(
        """
        You are free to start the time axis of your outputs at whatever year you like
        (e.g. starting at year 1, or 1850, or year 500).
        """
    ),
).strip()
HISTORICAL_FORCINGS_SETUP_TAIL = "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation."
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
ONEPCTCO2_GREENHOUSE_GAS_MODIFICATIONS = indent(
    block(
        r"""
        increase the atmospheric CO<sub>2</sub> concentrations at one percent per year yourself.
        CO2 concentrations should increase as

        $$
        c(t) = c_0 \cdot 1.01^{\frac{t - t_0}{\tau}},
        $$

        where $t_0$ is 1850 and $\tau$ is one year.

        For step-wise increases of CO<sub>2</sub>, specify a concentration that results,
        to good approximation, in a mean CO2 concentration (or mean forcing)
        for each time step consistent with the mean calculated when the CO2 concentration increases continuously.
        A particularly simple formula of sufficient accuracy for a 1% increase
        and time steps used in earth system models is

        $$
        c(t \rightarrow t + \Delta t) = \frac{c(t) + c(t + \Delta t)}{2},
        $$

        where $c(t \rightarrow t + \Delta t)$ is the value to apply in the time step
        that extends from time $t$ to $t + \Delta t$ and $\Delta t$
        is the size of the time step in your model
        (this can vary from time step to time step and it does not affect the formula above).
        For annual time steps, this reduces to

        $$
        \begin{aligned}
        c(y)
        &= c_0 \cdot 1.01^{y - y_0} \cdot \frac{1 + 1.01}{2} \\
        &= c_0 \cdot 1.01^{y - y_0} \cdot 1.05,
        \end{aligned}
        $$

        where $y$ is the year in which to apply the given value
        and $y_0$ is the starting year i.e. 1850.

        For monthly time steps, this reduces to

        $$
        \begin{aligned}
        c(y, m)
        &= c_0 \cdot \frac{1.01^{y - y_0} \cdot 1.01^{(m - 1) / 12} + 1.01^{y - y_0} \cdot 1.01^{m / 12}}{2} \\
        &= c_0 \cdot 1.01^{y - y_0} \cdot 1.01^{(m - 1) / 12} \cdot \frac{1 + 1.01^(1 / 12)}{2} \\
        &= c_0 \cdot 1.01^{y - y_0} \cdot 1.01^{(m - 1) / 12} \cdot 1.0004,
        \end{aligned}
        $$

        where $m$ is the month in which to apply the given value (January is 1, February is 2 etc.).
        """
    ),
    "    ",
)

PRESENT_YEAR = get_experiment("historical").end_timestamp.year

PI_CONTROL_VERSIONS_TO_USE = render_versions_body(PI_CONTROL_FORCING_VERSIONS)
HISTORICAL_VERSIONS_TO_USE = render_versions_body(HISTORICAL_FORCING_VERSIONS)


def picontrol_forcings_setup(first_sentence: str) -> str:
    """Render setup guidance for a piControl-forcings CMIP experiment."""
    return join_blocks(first_sentence, PI_CONTROL_FORCINGS_REPEAT_SETUP).strip()


def historical_forcings_setup(simulation_label: str) -> str:
    """Render setup guidance for a historical-forcings CMIP experiment."""
    return join_blocks(
        f"The {simulation_label} uses a specific set of forcings (see [forcings](#forcings)).",
        HISTORICAL_FORCINGS_SETUP_TAIL,
    ).strip()


def picontrol_cmip_data_access_body(experiment_name: str) -> str:
    """Render the data-access body for piControl CMIP forcings."""
    return render_data_access_body(
        experiment_name=experiment_name,
        source_ids=picontrol_cmip_source_ids(),
    )


def historical_cmip_data_access_body(experiment_name: str) -> str:
    """Render the data-access body for historical CMIP forcings."""
    return render_data_access_body(
        experiment_name=experiment_name,
        source_ids=historical_cmip_source_ids(),
    )


def picontrol_cmip_source_ids() -> tuple[str, ...]:
    """Return source IDs for piControl CMIP forcings."""
    return source_ids_from_forcing_versions(PI_CONTROL_FORCING_VERSIONS)


def historical_cmip_source_ids() -> tuple[str, ...]:
    """Return source IDs for historical CMIP forcings."""
    return source_ids_from_forcing_versions(HISTORICAL_FORCING_VERSIONS)


def picontrol_forcing_headlines(
    experiment_name: str,
    *,
    forcing_values_experiment_name: str | None = None,
) -> str:
    """Render shared piControl-forcings headlines."""
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


def make_picontrol_forcing_page(
    *,
    slug: str,
    experiment_name: str,
    simulation_label: str,
    setup_forcing_description: str,
    forcing_values_experiment_name: str | None = None,
) -> ExperimentPageOld:
    """Create a piControl-forcing page."""
    return ExperimentPageOld(
        slug=slug,
        experiment_setup=picontrol_forcings_setup(
            f"The {simulation_label} uses {setup_forcing_description} (see [forcings](#forcings))."
        ),
        forcing_headlines=picontrol_forcing_headlines(
            experiment_name,
            forcing_values_experiment_name=forcing_values_experiment_name,
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=PI_CONTROL_VERSIONS_TO_USE,
        getting_the_data=picontrol_cmip_data_access_body(experiment_name),
    )


def make_picontrol_spinup_page(
    *,
    slug: str,
    experiment_name: str,
    simulation_label: str,
    forcing_values_experiment_name: str,
) -> ExperimentPageOld:
    """Create a piControl spin-up page."""
    return make_picontrol_forcing_page(
        slug=slug,
        experiment_name=experiment_name,
        simulation_label=simulation_label,
        setup_forcing_description="piControl forcings",
        forcing_values_experiment_name=forcing_values_experiment_name,
    )


def make_historical_page(
    *,
    slug: str,
    experiment_name: str,
    simulation_label: str,
) -> ExperimentPageOld:
    """Create a historical page."""
    return ExperimentPageOld(
        slug=slug,
        experiment_setup=historical_forcings_setup(simulation_label),
        forcing_headlines=historical_forcing_headlines(experiment_name),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=HISTORICAL_VERSIONS_TO_USE,
        getting_the_data=historical_cmip_data_access_body(experiment_name),
    )


def get_historical_description(
    esgvoc_description: str, emms_driven: bool = False
) -> str:
    """Get historical description"""
    base = "Simulation of the climate of the recent past (1850 onwards)"

    if emms_driven:
        res = f"{base} with prescribed carbon dioxide emissions."

    else:
        res = f"{base} with prescribed carbon dioxide concentrations."

    return res


CMIP_EXPERIMENT_PAGES: tuple[ExperimentPageOld, ...] = (
    ExperimentPage(
        id_esgvoc="picontrol-spinup",
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="picontrol",
                )
                for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
            )
        ),
    ),
    ExperimentPage(
        id_esgvoc="picontrol",
        branch_information=BranchFromParentAtAnyTime(),
        forcings=PICONTROL_FORCINGS_SPECIFICATION,
    ),
    ExperimentPage(
        id_esgvoc="esm-picontrol-spinup",
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="picontrol",
                )
                for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
            )
        ),
    ),
    ExperimentPage(
        id_esgvoc="esm-picontrol",
        branch_information=BranchFromParentAtAnyTime(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="picontrol",
                )
                for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
            )
        ),
    ),
    ExperimentPage(
        id_esgvoc="historical",
        branch_information=BranchFromParentAtAnyTime(),
        forcings=HISTORICAL_FORCINGS_SPECIFICATION,
        render_description=get_historical_description,
    ),
    ExperimentPage(
        id_esgvoc="esm-hist",
        branch_information=BranchFromParentAtAnyTime(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="historical",
                )
                for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
            )
        ),
        render_description=partial(get_historical_description, emms_driven=True),
    ),
    ExperimentPage(
        id_esgvoc="1pctco2",
        branch_information=BranchFromParentAtAnyTime(),
        experiment_setup_notes=join_blocks(
            f"The 1pctCO2 experiment is a simple branch from the {PI_CONTROL_LINK}. ",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should increase at one percent per year throughout the experiment.",
        ),
        fixed_or_transient_or_mix_forcing_override=(
            "The 1pctCO2 experiment is a fixed forcings experiment, "
            "except for CO<sub>2</sub> which is transient."
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug != "greenhouse-gas-concentrations"
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                        fixed_override=False,
                        user_modifications=ONEPCTCO2_GREENHOUSE_GAS_MODIFICATIONS,
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug == "greenhouse-gas-concentrations"
                ),
            )
        ),
    ),
    ExperimentPage(
        id_esgvoc="abrupt-4xco2",
        branch_information=BranchFromParentAtAnyTime(),
        experiment_setup_notes=join_blocks(
            f"The abrupt CO<sub>2</sub> quadrupling experiment is a simple branch from the {PI_CONTROL_LINK}. ",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should "
            "be set to four times the CO<sub>2</sub> concentrations used in the piControl experiment.",
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug != "greenhouse-gas-concentrations"
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="greenhouse-gas-concentrations",
                    experiment_esgvoc_id="piclim-control",
                    user_modifications="quadruple the CO<sub>2</sub> concentrations",
                ),
            )
        ),
    ),
    ExperimentPage(
        id_esgvoc="piclim-control",
        branch_information=BranchFromParentAtAnyTime(),
        experiment_setup_notes=join_blocks(
            block(
                f"""
                The prescribed sea-surface temperatures and sea-ice concentrations
                must come from a (monthly varying, annually repeating)
                climatology taken from at least 30 years of your {render_link("pre-industrial control", "picontrol")} simulation
                (i.e. these forcings are derived from your model output from one of your own simulations,
                they are not provided by a forcings provider).
                """
            ),
        ),
        forcings=ForcingSpecification(
            specific_forcings=(
                NonInput4MIPsBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    label_override="sea-surface temperature forcing",
                    fixed=True,
                    notes=(
                        "derived from a (monthly varying, annually repeating) "
                        "climatology taken from at least 30 years of your "
                        f"{render_link('pre-industrial control', 'picontrol')} simulation"
                    ),
                ),
            ),
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="picontrol",
                )
                for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
            ),
        ),
        output_time_axis_info=PiClimOutputTimeAxisInformation(),
    ),
    ExperimentPage(
        id_esgvoc="piclim-4xco2",
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug != "greenhouse-gas-concentrations"
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                        user_modifications="quadruple the CO<sub>2</sub> concentrations",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug == "greenhouse-gas-concentrations"
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
        output_time_axis_info=PiClimOutputTimeAxisInformation(),
        render_description=only_keep_first_sentence,
    ),
    # TODO: de-duplicate the piclim-* definitions across activities
    ExperimentPage(
        id_esgvoc="piclim-anthro",
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    in (
                        "solar",
                        "stratospheric-volcanic-so2-emissions-aod",
                    )
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                        user_modifications=f"apply the {PRESENT_YEAR} value on repeat",
                        fixed_override=True,
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    not in (
                        "solar",
                        "stratospheric-volcanic-so2-emissions-aod",
                    )
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
        output_time_axis_info=PiClimOutputTimeAxisInformation(),
        render_description=only_keep_first_sentence,
    ),
    ExperimentPage(
        id_esgvoc="amip",
        forcings=ForcingSpecification(
            specific_forcings=(HISTORICAL_FORCINGS_SPECIFICATION_AMIP_SSTS,),
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="historical",
                )
                for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
            ),
        ),
    ),
)
