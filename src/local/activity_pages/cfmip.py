"""CFMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Mapping

from local.forcing_references import AMIP_FORCING_REFERENCES
from local.forcing_versions import (
    AMIP_FORCING_VERSIONS,
    HISTORICAL_FORCING_VERSIONS,
    PI_CONTROL_FORCING_VERSIONS,
    source_ids_from_forcing_versions,
)
from local.guidance import (
    ABRUPT_4XCO2_LINK,
    HISTORICAL_LINK,
    PI_CONTROL_LINK,
    TIME_AXIS_CAN_BE_ARBITRARY,
    ExperimentPageOld,
)
from local.rendering import (
    block,
    join_blocks,
    render_data_access_body,
    render_link,
    render_versions_json,
    same_as_versions,
)
from local.vocab import get_experiment

AMIP_LINK = render_link("amip simulation", "amip")


def _amip_notes(source_link: str) -> str:
    """Render the shared AMIP notes block."""
    return join_blocks(
        f"See notes for the {source_link}.",
        (
            "The following pages give further information on each forcing "
            f"beyond the ones used in the {source_link}:"
        ),
        "\n".join(
            f"- {reference.label}: [{reference.display_url}]({reference.url})"
            for reference in AMIP_FORCING_REFERENCES
        ),
    ).strip()


def _amip_versions_to_use(source_link: str) -> str:
    """Render the standard AMIP versions section for a source experiment."""
    return join_blocks(
        (
            f"The forcings relevant for this simulation are the same as for the {source_link} "
            "with the addition of the SST and sea-ice forcing."
        ),
        (
            'For this additional forcing, we provide the version(s), in the form of "source ID(s)", '
            "which should be used when running this simulation."
        ),
        f"For all other forcings, please see the information on the {source_link} page.",
        render_versions_json(AMIP_FORCING_VERSIONS),
    ).strip()


def _amip_source_link(source_forcing_versions: Mapping[str, object]) -> str:
    """Return the page link that matches a source forcing inventory."""
    if source_forcing_versions is HISTORICAL_FORCING_VERSIONS:
        return HISTORICAL_LINK

    if source_forcing_versions is PI_CONTROL_FORCING_VERSIONS:
        return PI_CONTROL_LINK

    return AMIP_LINK


def make_amip_variant_page(
    *,
    slug: str,
    setup_text: str,
    headline_text: str,
    source_forcing_versions: Mapping[str, object],
    extra_note: str = "",
) -> ExperimentPageOld:
    """Create an AMIP variant page."""
    experiment_name = get_experiment(slug).drs_name
    source_link = _amip_source_link(source_forcing_versions)

    return ExperimentPageOld(
        slug=slug,
        experiment_setup=join_blocks(
            f"The {experiment_name} simulation is a variant of the {AMIP_LINK}.",
            setup_text,
        ).strip(),
        forcing_headlines=headline_text,
        notes=join_blocks(
            _amip_notes(source_link),
            extra_note,
        ).strip(),
        versions_to_use=_amip_versions_to_use(source_link),
        getting_the_data=render_data_access_body(
            experiment_name=experiment_name,
            source_ids=source_ids_from_forcing_versions(
                AMIP_FORCING_VERSIONS,
                source_forcing_versions,
            ),
        ),
        include_parent_information=False,
    )


CFMIP_EXPERIMENT_PAGES: tuple[ExperimentPageOld, ...] = (
    make_amip_variant_page(
        slug="amip-p4k",
        setup_text=(
            "Sea-surface temperatures are increased by 4K in ice-free regions."
        ),
        headline_text=(
            "The `amip-p4K` experiment is a time-varying forcings experiment."
        ),
        source_forcing_versions=HISTORICAL_FORCING_VERSIONS,
        extra_note=(
            "You have to add the 4K to the sea-surface temperatures in your "
            "model's ice-free regions yourself."
        ),
    ),
    make_amip_variant_page(
        slug="amip-piforcing",
        setup_text=(
            "It starts in 1870 and all forcings except sea-surface temperatures "
            "are set to pre-industrial levels rather than time-varying forcings."
        ),
        headline_text=(
            "The `amip-piForcing` experiment is a fixed forcings experiment."
        ),
        source_forcing_versions=PI_CONTROL_FORCING_VERSIONS,
    ),
    ExperimentPageOld(
        slug="abrupt-2xco2",
        experiment_setup=join_blocks(
            f"The abrupt CO<sub>2</sub> doubling simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to two times
                the concentrations used in the `piControl` simulation.
                """
            ),
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            "You have to double the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=render_data_access_body(
            experiment_name="abrupt-2xCO2",
            source_ids=source_ids_from_forcing_versions(PI_CONTROL_FORCING_VERSIONS),
        ),
    ),
    ExperimentPageOld(
        slug="abrupt-0p5xco2",
        experiment_setup=join_blocks(
            f"The abrupt CO<sub>2</sub> halving simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to half
                the concentrations used in the `piControl` simulation.
                """
            ),
            TIME_AXIS_CAN_BE_ARBITRARY,
        ).strip(),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            "You have to halve the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=render_data_access_body(
            experiment_name="abrupt-0p5xCO2",
            source_ids=source_ids_from_forcing_versions(PI_CONTROL_FORCING_VERSIONS),
        ),
    ),
)
