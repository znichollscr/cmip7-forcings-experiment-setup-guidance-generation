"""Forcing version definitions and source-ID selection helpers."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ForcingVersions:
    """The versions to use for one forcing."""

    recommended: str | None
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


HISTORICAL_FORCING_VERSIONS = OrderedDict(
    (
        (
            "anthropogenic-emissions",
            ForcingVersions(
                recommended="CEDS-CMIP-2025-04-18-supplemental",
                acceptable=("CEDS-CMIP-2025-04-18",),
            ),
        ),
        (
            "biomass-burning-emissions",
            ForcingVersions(recommended="DRES-CMIP-BB4CMIP7-2-0"),
        ),
        (
            "land-use",
            ForcingVersions(
                recommended="UofMD-landState-3-1-2",
                acceptable=("UofMD-landState-3-1-1",),
            ),
        ),
        (
            "greenhouse-gas-concentrations",
            ForcingVersions(recommended="CR-CMIP-1-0-0"),
        ),
        (
            "stratospheric-aerosol-forcing",
            ForcingVersions(recommended="UOEXETER-CMIP-2-2-1"),
        ),
        (
            "ozone",
            ForcingVersions(
                recommended="FZJ-CMIP-ozone-2-0",
                acceptable=("FZJ-CMIP-ozone-1-2",),
            ),
        ),
        (
            "nitrogen-deposition",
            ForcingVersions(
                recommended="FZJ-CMIP-nitrogen-2-0",
                acceptable=("FZJ-CMIP-nitrogen-1-2",),
            ),
        ),
        ("solar", ForcingVersions(recommended="SOLARIS-HEPPA-CMIP-4-6")),
        ("aerosol-optical-properties", ForcingVersions(recommended=None)),
        ("population-density", ForcingVersions(recommended="PIK-CMIP-1-0-1")),
    )
)

PI_CONTROL_FORCING_VERSIONS = override_forcing_versions(
    forcing_versions=HISTORICAL_FORCING_VERSIONS,
    overrides={
        "ozone": ForcingVersions(
            recommended="FZJ-CMIP-ozone-1-2",
            acceptable=("FZJ-CMIP-ozone-2-0",),
        ),
    },
)

SCEN7_H_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ForcingVersions(recommended="IIASA-IAMC-h-1-0-0")),
        (
            "biomass-burning-emissions",
            ForcingVersions(recommended="IIASA-IAMC-h-1-0-0"),
        ),
        (
            "land-use",
            ForcingVersions(
                recommended="UofMD-landState-h-3-1-1",
                acceptable=("UofMD-landState-h-3-1",),
            ),
        ),
        ("greenhouse-gas-concentrations", ForcingVersions(recommended="CR-h-1-0-0")),
        (
            "stratospheric-aerosol-forcing",
            ForcingVersions(recommended="UOEXETER-ScenarioMIP-2-2-2"),
        ),
        ("ozone", ForcingVersions(recommended="FZJ-CMIP-ozone-vl-1-0")),
        (
            "nitrogen-deposition",
            ForcingVersions(recommended="FZJ-CMIP-nitrogen-vl-1-0"),
        ),
        ("solar", ForcingVersions(recommended="SOLARIS-HEPPA-ScenarioMIP-4-6")),
        ("aerosol-optical-properties", ForcingVersions(recommended=None)),
        ("population-density", ForcingVersions(recommended="PIK-h-1-0-0")),
    )
)

SCEN7_VL_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ForcingVersions(recommended="IIASA-IAMC-vl-1-0-0")),
        (
            "biomass-burning-emissions",
            ForcingVersions(recommended="IIASA-IAMC-vl-1-0-0"),
        ),
        (
            "land-use",
            ForcingVersions(
                recommended="UofMD-landState-vl-3-1-1",
                acceptable=("UofMD-landState-vl-3-1",),
            ),
        ),
        ("greenhouse-gas-concentrations", ForcingVersions(recommended="CR-vl-1-0-0")),
        (
            "stratospheric-aerosol-forcing",
            ForcingVersions(recommended="UOEXETER-ScenarioMIP-2-2-2"),
        ),
        ("ozone", ForcingVersions(recommended="FZJ-CMIP-ozone-h-1-0")),
        (
            "nitrogen-deposition",
            ForcingVersions(recommended="FZJ-CMIP-nitrogen-h-1-0"),
        ),
        ("solar", ForcingVersions(recommended="SOLARIS-HEPPA-ScenarioMIP-4-6")),
        ("aerosol-optical-properties", ForcingVersions(recommended=None)),
        ("population-density", ForcingVersions(recommended="PIK-vl-1-0-0")),
    )
)

AMIP_FORCING_VERSIONS = OrderedDict(
    (
        (
            "amip-sea-surface-temperature-and-sea-ice-boundary-forcing",
            ForcingVersions(recommended="PCMDI-AMIP-1-1-10"),
        ),
    )
)

NON_DOWNLOADABLE_FORCING_VALUES = {"not-available-yet"}


def historical_forcing_ids_except(*excluded_forcing_ids: str) -> tuple[str, ...]:
    """Return historical forcing IDs excluding the given IDs."""
    return forcing_ids_except(HISTORICAL_FORCING_VERSIONS, *excluded_forcing_ids)


def forcing_ids_except(
    forcing_versions: Mapping[str, ForcingValue],
    *excluded_forcing_ids: str,
) -> tuple[str, ...]:
    """Return forcing IDs excluding the given IDs."""
    excluded = set(excluded_forcing_ids)
    return tuple(
        forcing_id for forcing_id in forcing_versions if forcing_id not in excluded
    )


def source_ids_for_picontrol_historical_forcing_combination(
    *,
    picontrol_forcing_ids: Sequence[str] = (),
    historical_forcing_ids: Sequence[str] = (),
) -> tuple[str, ...]:
    """Derive source IDs for a mix of piControl and historical forcings."""
    return merge_source_ids(
        source_ids_from_forcing_versions(
            select_forcing_versions(
                PI_CONTROL_FORCING_VERSIONS,
                picontrol_forcing_ids,
            ),
        ),
        source_ids_from_forcing_versions(
            select_forcing_versions(
                HISTORICAL_FORCING_VERSIONS,
                historical_forcing_ids,
            ),
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
            selected_source_ids = recommended_source_ids(
                value=value,
            )

            for source_id in selected_source_ids:
                if source_id in seen:
                    continue

                source_ids.append(source_id)
                seen.add(source_id)

    return tuple(source_ids)


def recommended_source_ids(
    *,
    value: ForcingValue,
) -> tuple[str, ...]:
    """Return the recommended downloadable source ID for one forcing value."""
    recommended_value = recommended_forcing_value(value=value)
    if (
        recommended_value is None
        or recommended_value in NON_DOWNLOADABLE_FORCING_VALUES
    ):
        return ()

    return (recommended_value,)


def recommended_forcing_value(
    *,
    value: ForcingValue,
) -> str | None:
    """Return the recommended value for one forcing."""
    return value.recommended


def acceptable_forcing_values(
    *,
    value: ForcingValue,
) -> tuple[str, ...]:
    """Return acceptable non-recommended values for one forcing."""
    return value.acceptable
