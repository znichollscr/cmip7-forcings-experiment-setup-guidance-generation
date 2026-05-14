"""Forcing version definitions and source-ID selection helpers."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from typing import Union

ForcingValue = Union[Sequence[str], str, None]

CMIP_FORCING_VERSIONS = OrderedDict(
    (
        (
            "anthropogenic-emissions",
            ("CEDS-CMIP-2025-04-18", "CEDS-CMIP-2025-04-18-supplemental"),
        ),
        ("biomass-burning-emissions", ("DRES-CMIP-BB4CMIP7-2-0",)),
        ("land-use", ("UofMD-landState-3-1-1",)),
        ("greenhouse-gas-concentrations", ("CR-CMIP-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-CMIP-2-2-1",)),
        ("ozone", ("FZJ-CMIP-ozone-1-2", "FZJ-CMIP-ozone-2-0")),
        ("nitrogen-deposition", ("FZJ-CMIP-nitrogen-1-2", "FZJ-CMIP-nitrogen-2-0")),
        ("solar", ("SOLARIS-HEPPA-CMIP-4-6",)),
        ("aerosol-optical-properties", None),
        ("population-density", ("PIK-CMIP-1-0-1",)),
    )
)

CMIP_FIXED_SOURCE_ID_INDEXES = {
    "nitrogen-deposition": 0,
    "ozone": 0,
}

CMIP_TRANSIENT_SOURCE_ID_INDEXES = {
    "nitrogen-deposition": 0,
    "ozone": 1,
}

SCEN7_H_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ("IIASA-IAMC-h-1-0-0",)),
        ("biomass-burning-emissions", ("IIASA-IAMC-h-1-0-0",)),
        ("land-use", "not-available-yet"),
        ("greenhouse-gas-concentrations", ("CR-h-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-ScenarioMIP-2-2-2",)),
        ("ozone", "not-available-yet"),
        ("nitrogen-deposition", "not-available-yet"),
        ("solar", ("SOLARIS-HEPPA-ScenarioMIP-4-6",)),
        ("aerosol-optical-properties", None),
        ("population-density", ("PIK-h-1-0-0",)),
    )
)

SCEN7_VL_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ("IIASA-IAMC-vl-1-0-0",)),
        ("biomass-burning-emissions", ("IIASA-IAMC-vl-1-0-0",)),
        ("land-use", "not-available-yet"),
        ("greenhouse-gas-concentrations", ("CR-vl-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-ScenarioMIP-2-2-2",)),
        ("ozone", "not-available-yet"),
        ("nitrogen-deposition", "not-available-yet"),
        ("solar", ("SOLARIS-HEPPA-ScenarioMIP-4-6",)),
        ("aerosol-optical-properties", None),
        ("population-density", ("PIK-vl-1-0-0",)),
    )
)

AMIP_FORCING_VERSIONS = OrderedDict(
    (
        (
            "amip-sea-surface-temperature-and-sea-ice-boundary-forcing",
            ("PCMDI-AMIP-1-1-10",),
        ),
    )
)

NON_DOWNLOADABLE_FORCING_VALUES = {"not-available-yet"}


def cmip_forcing_ids_except(*excluded_forcing_ids: str) -> tuple[str, ...]:
    """Return CMIP forcing IDs excluding the given IDs."""
    return forcing_ids_except(CMIP_FORCING_VERSIONS, *excluded_forcing_ids)


def forcing_ids_except(
    forcing_versions: Mapping[str, ForcingValue],
    *excluded_forcing_ids: str,
) -> tuple[str, ...]:
    """Return forcing IDs excluding the given IDs."""
    excluded = set(excluded_forcing_ids)
    return tuple(
        forcing_id for forcing_id in forcing_versions if forcing_id not in excluded
    )


def source_ids_for_cmip_forcing_combination(
    *,
    fixed_forcing_ids: Sequence[str] = (),
    transient_forcing_ids: Sequence[str] = (),
) -> tuple[str, ...]:
    """Derive source IDs for a mix of fixed and transient CMIP forcings."""
    return merge_source_ids(
        source_ids_from_forcing_versions(
            select_forcing_versions(CMIP_FORCING_VERSIONS, fixed_forcing_ids),
            source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
        ),
        source_ids_from_forcing_versions(
            select_forcing_versions(CMIP_FORCING_VERSIONS, transient_forcing_ids),
            source_id_indexes=CMIP_TRANSIENT_SOURCE_ID_INDEXES,
        ),
    )


def select_forcing_versions(
    forcing_versions: Mapping[str, ForcingValue],
    forcing_ids: Sequence[str],
) -> Mapping[str, ForcingValue]:
    """Select forcing versions by forcing ID while preserving source order."""
    return OrderedDict(
        (forcing_id, forcing_versions[forcing_id]) for forcing_id in forcing_ids
    )


def merge_source_ids(*source_id_collections: Sequence[str]) -> tuple[str, ...]:
    """Merge source-ID collections while preserving order and de-duplicating."""
    source_ids: list[str] = []
    seen: set[str] = set()

    for source_id_collection in source_id_collections:
        for source_id in source_id_collection:
            if source_id in seen:
                continue

            source_ids.append(source_id)
            seen.add(source_id)

    return tuple(source_ids)


def source_ids_from_forcing_versions(
    *forcing_versions: Mapping[str, ForcingValue],
    source_id_indexes: Mapping[str, int] | None = None,
) -> tuple[str, ...]:
    """Derive ESGF-downloadable source IDs from forcing-version mappings."""
    source_id_indexes = source_id_indexes or {}
    source_ids: list[str] = []
    seen: set[str] = set()

    for forcing_version in forcing_versions:
        for forcing_id, value in forcing_version.items():
            if value is None:
                continue

            if isinstance(value, str):
                selected_source_ids = (
                    () if value in NON_DOWNLOADABLE_FORCING_VALUES else (value,)
                )
            elif forcing_id in source_id_indexes:
                selected_source_ids = (value[source_id_indexes[forcing_id]],)
            else:
                selected_source_ids = tuple(value)

            for source_id in selected_source_ids:
                if source_id in seen:
                    continue

                source_ids.append(source_id)
                seen.add(source_id)

    return tuple(source_ids)
