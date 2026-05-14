"""Forcing version definitions and source-ID selection helpers."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ForcingVersions:
    """The versions to use for one forcing."""

    preferred: str | None
    acceptable: tuple[str, ...] = ()


ForcingValue = ForcingVersions


def override_forcing_versions(
    forcing_versions: Mapping[str, ForcingValue],
    overrides: Mapping[str, ForcingValue],
) -> Mapping[str, ForcingValue]:
    """Override forcing-version definitions while preserving forcing order."""
    unknown_forcing_ids = tuple(
        forcing_id for forcing_id in overrides if forcing_id not in forcing_versions
    )
    if unknown_forcing_ids:
        msg = f"Cannot override unknown forcing IDs: {', '.join(unknown_forcing_ids)}."
        raise ValueError(msg)

    return OrderedDict(
        (forcing_id, overrides.get(forcing_id, value))
        for forcing_id, value in forcing_versions.items()
    )


CMIP_FORCING_VERSIONS = OrderedDict(
    (
        (
            "anthropogenic-emissions",
            ForcingVersions(
                preferred="CEDS-CMIP-2025-04-18-supplemental",
                acceptable=("CEDS-CMIP-2025-04-18",),
            ),
        ),
        (
            "biomass-burning-emissions",
            ForcingVersions(preferred="DRES-CMIP-BB4CMIP7-2-0"),
        ),
        (
            "land-use",
            ForcingVersions(
                preferred="UofMD-landState-3-1-2",
                acceptable=("UofMD-landState-3-1-1",),
            ),
        ),
        (
            "greenhouse-gas-concentrations",
            ForcingVersions(preferred="CR-CMIP-1-0-0"),
        ),
        (
            "stratospheric-aerosol-forcing",
            ForcingVersions(preferred="UOEXETER-CMIP-2-2-1"),
        ),
        (
            "ozone",
            ForcingVersions(
                preferred="FZJ-CMIP-ozone-2-0",
                acceptable=("FZJ-CMIP-ozone-1-2",),
            ),
        ),
        (
            "nitrogen-deposition",
            ForcingVersions(
                preferred="FZJ-CMIP-nitrogen-2-0",
                acceptable=("FZJ-CMIP-nitrogen-1-2",),
            ),
        ),
        ("solar", ForcingVersions(preferred="SOLARIS-HEPPA-CMIP-4-6")),
        ("aerosol-optical-properties", ForcingVersions(preferred=None)),
        ("population-density", ForcingVersions(preferred="PIK-CMIP-1-0-1")),
    )
)

CMIP_FIXED_FORCING_VERSIONS = override_forcing_versions(
    CMIP_FORCING_VERSIONS,
    {
        "ozone": ForcingVersions(
            preferred="FZJ-CMIP-ozone-1-2",
            acceptable=("FZJ-CMIP-ozone-2-0",),
        ),
    },
)

SCEN7_H_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ForcingVersions(preferred="IIASA-IAMC-h-1-0-0")),
        (
            "biomass-burning-emissions",
            ForcingVersions(preferred="IIASA-IAMC-h-1-0-0"),
        ),
        (
            "land-use",
            ForcingVersions(
                preferred="UofMD-landState-h-3-1-1",
                acceptable=("UofMD-landState-h-3-1",),
            ),
        ),
        ("greenhouse-gas-concentrations", ForcingVersions(preferred="CR-h-1-0-0")),
        (
            "stratospheric-aerosol-forcing",
            ForcingVersions(preferred="UOEXETER-ScenarioMIP-2-2-2"),
        ),
        ("ozone", ForcingVersions(preferred="FZJ-CMIP-ozone-vl-1-0")),
        (
            "nitrogen-deposition",
            ForcingVersions(preferred="FZJ-CMIP-nitrogen-vl-1-0"),
        ),
        ("solar", ForcingVersions(preferred="SOLARIS-HEPPA-ScenarioMIP-4-6")),
        ("aerosol-optical-properties", ForcingVersions(preferred=None)),
        ("population-density", ForcingVersions(preferred="PIK-h-1-0-0")),
    )
)

SCEN7_VL_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ForcingVersions(preferred="IIASA-IAMC-vl-1-0-0")),
        (
            "biomass-burning-emissions",
            ForcingVersions(preferred="IIASA-IAMC-vl-1-0-0"),
        ),
        (
            "land-use",
            ForcingVersions(
                preferred="UofMD-landState-vl-3-1-1",
                acceptable=("UofMD-landState-vl-3-1",),
            ),
        ),
        ("greenhouse-gas-concentrations", ForcingVersions(preferred="CR-vl-1-0-0")),
        (
            "stratospheric-aerosol-forcing",
            ForcingVersions(preferred="UOEXETER-ScenarioMIP-2-2-2"),
        ),
        ("ozone", ForcingVersions(preferred="FZJ-CMIP-ozone-h-1-0")),
        (
            "nitrogen-deposition",
            ForcingVersions(preferred="FZJ-CMIP-nitrogen-h-1-0"),
        ),
        ("solar", ForcingVersions(preferred="SOLARIS-HEPPA-ScenarioMIP-4-6")),
        ("aerosol-optical-properties", ForcingVersions(preferred=None)),
        ("population-density", ForcingVersions(preferred="PIK-vl-1-0-0")),
    )
)

AMIP_FORCING_VERSIONS = OrderedDict(
    (
        (
            "amip-sea-surface-temperature-and-sea-ice-boundary-forcing",
            ForcingVersions(preferred="PCMDI-AMIP-1-1-10"),
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
            select_forcing_versions(CMIP_FIXED_FORCING_VERSIONS, fixed_forcing_ids),
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
) -> tuple[str, ...]:
    """Derive ESGF-downloadable source IDs from forcing-version mappings."""
    source_ids: list[str] = []
    seen: set[str] = set()

    for forcing_version in forcing_versions:
        for value in forcing_version.values():
            selected_source_ids = preferred_source_ids(
                value=value,
            )

            for source_id in selected_source_ids:
                if source_id in seen:
                    continue

                source_ids.append(source_id)
                seen.add(source_id)

    return tuple(source_ids)


def preferred_source_ids(
    *,
    value: ForcingValue,
) -> tuple[str, ...]:
    """Return the preferred downloadable source ID for one forcing value."""
    preferred_value = preferred_forcing_value(value=value)
    if preferred_value is None or preferred_value in NON_DOWNLOADABLE_FORCING_VALUES:
        return ()

    return (preferred_value,)


def preferred_forcing_value(
    *,
    value: ForcingValue,
) -> str | None:
    """Return the preferred value for one forcing."""
    return value.preferred


def acceptable_forcing_values(
    *,
    value: ForcingValue,
) -> tuple[str, ...]:
    """Return acceptable non-preferred values for one forcing."""
    return value.acceptable
