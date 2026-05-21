"""CMIP experiment guidance pages."""

from __future__ import annotations

from functools import partial
from textwrap import indent

from local.branching import BranchAtSameTimeAsOtherExperiment, BranchFromParentAtAnyTime
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
)
from local.output_time_axis import PiClimOutputTimeAxisInformation
from local.rendering import (
    block,
    join_blocks,
    only_keep_first_sentence,
    render_link,
)
from local.vocab import get_experiment

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

LAST_HISTORICAL_YEAR = get_experiment("historical").end_timestamp.year


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


CMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
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
                        user_modifications=f"apply the {LAST_HISTORICAL_YEAR} value on repeat",
                        fixed_override=True,
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
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
