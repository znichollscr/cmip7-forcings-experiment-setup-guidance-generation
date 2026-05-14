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
        ("land-use", ("UofMD-landState-3-1-1", "UofMD-landState-3-1-2")),
        ("greenhouse-gas-concentrations", ("CR-CMIP-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-CMIP-2-2-1",)),
        ("ozone", ("FZJ-CMIP-ozone-1-2", "FZJ-CMIP-ozone-2-0")),
        ("nitrogen-deposition", ("FZJ-CMIP-nitrogen-1-2", "FZJ-CMIP-nitrogen-2-0")),
        ("solar", ("SOLARIS-HEPPA-CMIP-4-6",)),
        ("aerosol-optical-properties", None),
        ("population-density", ("PIK-CMIP-1-0-1",)),
    )
)

CMIP_FIXED_PREFERRED_SOURCE_ID_INDEXES = {
    "ozone": 0,
}

SCEN7_H_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ("IIASA-IAMC-h-1-0-0",)),
        ("biomass-burning-emissions", ("IIASA-IAMC-h-1-0-0",)),
        ("land-use", ("UofMD-landState-h-3-1", "UofMD-landState-h-3-1-1")),
        ("greenhouse-gas-concentrations", ("CR-h-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-ScenarioMIP-2-2-2",)),
        ("ozone", "FZJ-CMIP-ozone-vl-1-0"),
        ("nitrogen-deposition", "FZJ-CMIP-nitrogen-vl-1-0"),
        ("solar", ("SOLARIS-HEPPA-ScenarioMIP-4-6",)),
        ("aerosol-optical-properties", None),
        ("population-density", ("PIK-h-1-0-0",)),
    )
)

SCEN7_VL_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ("IIASA-IAMC-vl-1-0-0",)),
        ("biomass-burning-emissions", ("IIASA-IAMC-vl-1-0-0",)),
        ("land-use", ("UofMD-landState-vl-3-1", "UofMD-landState-vl-3-1-1")),
        ("greenhouse-gas-concentrations", ("CR-vl-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-ScenarioMIP-2-2-2",)),
        ("ozone", "FZJ-CMIP-ozone-h-1-0"),
        ("nitrogen-deposition", "FZJ-CMIP-nitrogen-h-1-0"),
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
            preferred_source_id_indexes=CMIP_FIXED_PREFERRED_SOURCE_ID_INDEXES,
        ),
        source_ids_from_forcing_versions(
            select_forcing_versions(CMIP_FORCING_VERSIONS, transient_forcing_ids),
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
    preferred_source_id_indexes: Mapping[str, int] | None = None,
) -> tuple[str, ...]:
    """Derive ESGF-downloadable source IDs from forcing-version mappings."""
    preferred_source_id_indexes = preferred_source_id_indexes or {}
    source_ids: list[str] = []
    seen: set[str] = set()

    for forcing_version in forcing_versions:
        for forcing_id, value in forcing_version.items():
            selected_source_ids = preferred_source_ids(
                forcing_id=forcing_id,
                value=value,
                preferred_source_id_indexes=preferred_source_id_indexes,
            )

            for source_id in selected_source_ids:
                if source_id in seen:
                    continue

                source_ids.append(source_id)
                seen.add(source_id)

    return tuple(source_ids)


def preferred_source_ids(
    *,
    forcing_id: str,
    value: ForcingValue,
    preferred_source_id_indexes: Mapping[str, int] | None = None,
) -> tuple[str, ...]:
    """Return the preferred downloadable source ID for one forcing value."""
    preferred_value = preferred_forcing_value(
        forcing_id=forcing_id,
        value=value,
        preferred_source_id_indexes=preferred_source_id_indexes,
    )
    if preferred_value is None or preferred_value in NON_DOWNLOADABLE_FORCING_VALUES:
        return ()

    return (preferred_value,)


def preferred_forcing_value(
    *,
    forcing_id: str,
    value: ForcingValue,
    preferred_source_id_indexes: Mapping[str, int] | None = None,
) -> str | None:
    """Return the preferred value for one forcing.

    For now, the final listed version is treated as preferred.
    """
    if value is None or isinstance(value, str):
        return value

    if not value:
        msg = f"No forcing versions are defined for {forcing_id!r}."
        raise ValueError(msg)

    preferred_source_id_indexes = preferred_source_id_indexes or {}
    if forcing_id in preferred_source_id_indexes:
        return value[preferred_source_id_indexes[forcing_id]]

    return value[-1]


def acceptable_forcing_values(
    *,
    forcing_id: str,
    value: ForcingValue,
    preferred_source_id_indexes: Mapping[str, int] | None = None,
) -> tuple[str, ...]:
    """Return acceptable non-preferred values for one forcing."""
    if value is None or isinstance(value, str):
        return ()

    preferred_value = preferred_forcing_value(
        forcing_id=forcing_id,
        value=value,
        preferred_source_id_indexes=preferred_source_id_indexes,
    )
    return tuple(item for item in value if item != preferred_value)
