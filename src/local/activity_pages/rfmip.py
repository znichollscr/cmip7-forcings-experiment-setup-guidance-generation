"""RFMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from local.branching import BranchAtSameTimeAsOtherExperiment
from local.forcing_versions import (
    HISTORICAL_FORCING_VERSIONS,
    PI_CONTROL_FORCING_VERSIONS,
    forcing_ids_except,
    merge_source_ids,
    scen7_forcing_versions_for_slug,
    select_forcing_versions,
    source_ids_from_forcing_versions,
)
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    HISTORICAL_LINK,
    PI_CLIM_CONTROL_LINK,
    ExperimentPage,
)
from local.output_time_axis import PiClimOutputTimeAxisInformation
from local.rendering import (
    block,
    only_keep_first_sentence,
    render_link,
)
from local.vocab import get_experiment

from .cmip import LAST_HISTORICAL_YEAR

# TODO: split out a `render_link_for_experiment` function
SCEN7_M = get_experiment("scen7-m")
SCEN7_M_LINK = render_link(SCEN7_M.drs_name, SCEN7_M.id)

PICLIM_CONTROL = get_experiment("piclim-control")
PICLIM_CONTROL_LINK = render_link(PICLIM_CONTROL.drs_name, PICLIM_CONTROL.id)


RFMIP_EXTENSION_SCENARIO_SLUGS = ("scen7-m", "esm-scen7-m")
PICLIM_CONTROL_PRESCRIBED_BOUNDARY_CONDITIONS = block(
    f"""
    This simulation uses the same prescribed sea-surface temperatures and sea-ice concentrations setup
    as the {PI_CLIM_CONTROL_LINK}.
    As for piClim-control, these prescribed fields must come from model output from one of your own simulations,
    rather than from an input4MIPs forcing dataset.
    Please see the {PI_CLIM_CONTROL_LINK} for details.
    """
)


@dataclass(frozen=True)
class HistoricalTransientForcingPageSpec:
    """Inputs needed to create an RFMIP historical transient forcing page."""

    slug: str
    historical_forcing_ids: tuple[str, ...]
    historical_forcing_label: str
    use_piclim_control_for_other_forcings: bool


def forcing_subject(
    spec: HistoricalTransientForcingPageSpec,
    *,
    sentence_start: bool = False,
) -> str:
    """Return the forcing phrase as the subject of a sentence."""
    if spec.historical_forcing_label == "all forcings":
        return "All forcings" if sentence_start else "all forcings"

    article = "The" if sentence_start else "the"
    return f"{article} {spec.historical_forcing_label}"


def historical_forcing_phrase(spec: HistoricalTransientForcingPageSpec) -> str:
    """Return the forcing phrase for summary text."""
    if spec.historical_forcing_label == "all forcings":
        return "all forcings from the historical simulation"

    return f"historical {spec.historical_forcing_label}"


def rfmip_extension_scenario_links() -> str:
    """Return links to the scenarios used for RFMIP historical extensions."""
    return " or ".join(
        render_link(f"`{get_experiment(slug).drs_name}`", slug)
        for slug in RFMIP_EXTENSION_SCENARIO_SLUGS
    )


def source_ids_for_partial_historical_transient_forcing_page(
    historical_forcing_ids: Sequence[str],
) -> tuple[str, ...]:
    """Derive source IDs for an RFMIP partial historical transient forcing page."""
    return merge_source_ids(
        source_ids_from_forcing_versions(
            select_forcing_versions(
                PI_CONTROL_FORCING_VERSIONS,
                forcing_ids_except(
                    PI_CONTROL_FORCING_VERSIONS, *historical_forcing_ids
                ),
            ),
        ),
        source_ids_from_historical_and_extension_forcings(historical_forcing_ids),
    )


def source_ids_for_all_historical_transient_forcing_page() -> tuple[str, ...]:
    """Derive source IDs for an RFMIP all-forcing historical transient page."""
    return source_ids_from_historical_and_extension_forcings(
        tuple(HISTORICAL_FORCING_VERSIONS)
    )


def source_ids_from_historical_and_extension_forcings(
    forcing_ids: Sequence[str],
) -> tuple[str, ...]:
    """Derive source IDs from historical forcings and extension scenarios."""
    return merge_source_ids(
        source_ids_from_forcing_versions(
            select_forcing_versions(HISTORICAL_FORCING_VERSIONS, forcing_ids),
        ),
        *(
            source_ids_from_forcing_versions(
                select_forcing_versions(
                    scen7_forcing_versions_for_slug(slug),
                    forcing_ids,
                )
            )
            for slug in RFMIP_EXTENSION_SCENARIO_SLUGS
        ),
    )


RFMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="piclim-aer",
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
                    not in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
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
                    in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
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
        id_esgvoc="piclim-histaer",
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        experiment_setup_notes=block(
            f"""
            piClim-histaer is the same setup as {PICLIM_CONTROL_LINK},
            except aerosol emissions follow the {HISTORICAL_LINK} experiment
            then the {SCEN7_M_LINK} experiment.
            """
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-m",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    not in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
    ),
    ExperimentPage(
        id_esgvoc="piclim-histall",
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        experiment_setup_notes=block(
            f"""
            piClim-histaer is the same setup as {PICLIM_CONTROL_LINK},
            except all forcings follow the {HISTORICAL_LINK} experiment
            then the {SCEN7_M_LINK} experiment.
            """
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-m",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
    ),
)
