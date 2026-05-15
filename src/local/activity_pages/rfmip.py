"""RFMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from local.forcing_versions import (
    HISTORICAL_FORCING_VERSIONS,
    PI_CONTROL_FORCING_VERSIONS,
    forcing_ids_except,
    merge_source_ids,
    scen7_forcing_versions_for_slug,
    select_forcing_versions,
    source_ids_from_forcing_versions,
)
from local.guidance import HISTORICAL_LINK, PI_CLIM_CONTROL_LINK, ExperimentPage
from local.piclim_variants import (
    HistoricalForcing,
    make_piclim_historical_forcing_variant_page,
)
from local.rendering import (
    block,
    join_blocks,
    join_lines,
    render_data_access_body,
    render_link,
)
from local.vocab import get_experiment

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


def make_historical_transient_forcing_page(
    spec: HistoricalTransientForcingPageSpec,
) -> ExperimentPage:
    """Create an RFMIP page using historical forcings with scenario extensions."""
    experiment_name = get_experiment(spec.slug).drs_name
    extension_scenario_links = rfmip_extension_scenario_links()

    if spec.use_piclim_control_for_other_forcings:
        other_forcings_setup = (
            f"All other forcings should remain as in the {PI_CLIM_CONTROL_LINK}."
        )
        other_forcings_versions = join_lines(
            "For all other forcings,",
            (
                "the forcing versions relevant for this simulation are the same "
                f"as for the {PI_CLIM_CONTROL_LINK}."
            ),
        )
        source_ids = source_ids_for_partial_historical_transient_forcing_page(
            spec.historical_forcing_ids
        )
    else:
        other_forcings_setup = ""
        other_forcings_versions = ""
        source_ids = source_ids_for_all_historical_transient_forcing_page()

    return ExperimentPage(
        slug=spec.slug,
        experiment_setup=join_blocks(
            PICLIM_CONTROL_PRESCRIBED_BOUNDARY_CONDITIONS,
            (
                f"{forcing_subject(spec, sentence_start=True)} should evolve as in the "
                f"{HISTORICAL_LINK}."
            ),
            (
                "For the extension beyond the historical simulation, "
                f"{forcing_subject(spec)} should follow "
                f"{extension_scenario_links}, whichever is relevant to your "
                "model setup."
            ),
            other_forcings_setup,
        ).strip(),
        forcing_headlines=join_lines(
            f"The `{experiment_name}` experiment combines",
            historical_forcing_phrase(spec),
            f"extended with {extension_scenario_links}.",
        ),
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
        versions_to_use=join_blocks(
            join_lines(
                f"For {spec.historical_forcing_label},",
                f"the relevant forcing is the same as for the {HISTORICAL_LINK},",
                f"then {extension_scenario_links} for the extension.",
            ),
            other_forcings_versions,
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name=experiment_name,
            source_ids=source_ids,
        ),
    )


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
                forcing_ids_except(PI_CONTROL_FORCING_VERSIONS, *historical_forcing_ids),
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
    make_piclim_historical_forcing_variant_page(
        slug="piclim-aer",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="anthropogenic-emissions",
                label="anthropogenic aerosol emissions",
            ),
            HistoricalForcing(
                forcing_id="biomass-burning-emissions",
                label="biomass-burning aerosol emissions",
            ),
        ),
    ),
    make_historical_transient_forcing_page(
        HistoricalTransientForcingPageSpec(
            slug="piclim-histaer",
            historical_forcing_ids=(
                "anthropogenic-emissions",
                "biomass-burning-emissions",
            ),
            historical_forcing_label="aerosol emissions",
            use_piclim_control_for_other_forcings=True,
        )
    ),
    make_historical_transient_forcing_page(
        HistoricalTransientForcingPageSpec(
            slug="piclim-histall",
            historical_forcing_ids=tuple(HISTORICAL_FORCING_VERSIONS),
            historical_forcing_label="all forcings",
            use_piclim_control_for_other_forcings=False,
        )
    ),
)
