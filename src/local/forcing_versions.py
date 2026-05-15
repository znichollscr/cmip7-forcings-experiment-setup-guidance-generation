"""Forcing version definitions and source-ID selection helpers."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

ForcingSourceIds = str | Sequence[str] | None


@dataclass(frozen=True)
class ForcingVersions:
    """The versions to use for one forcing."""

    recommended: ForcingSourceIds
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
                recommended=(
                    "CEDS-CMIP-2025-04-18",
                    "CEDS-CMIP-2025-04-18-supplemental",
                ),
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
        "ozone": ForcingVersions(recommended="FZJ-CMIP-ozone-1-2"),
    },
)

SCEN7_VL_FORCING_VERSIONS = OrderedDict(
    (
        (
            "anthropogenic-emissions",
            ForcingVersions(recommended=("IIASA-IAMC-vl-1-0-0", "IIASA-IAMC-1-0-0")),
        ),
        (
            "biomass-burning-emissions",
            ForcingVersions(recommended=("IIASA-IAMC-vl-1-0-0", "IIASA-IAMC-1-0-0")),
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
SCEN7_EXPERIMENT_PREFIX = "scen7-"
SCEN7_ESM_EXPERIMENT_PREFIX = f"esm-{SCEN7_EXPERIMENT_PREFIX}"
SCEN7_TEMPLATE_SUFFIX = "vl"
SCEN7_FORCING_VERSION_SLUGS = (
    "scen7-h",
    "esm-scen7-h",
    "scen7-h-ext",
    "esm-scen7-h-ext",
    "scen7-hl",
    "esm-scen7-hl",
    "scen7-hl-ext",
    "esm-scen7-hl-ext",
    "scen7-l",
    "esm-scen7-l",
    "scen7-l-ext",
    "esm-scen7-l-ext",
    "scen7-ln",
    "esm-scen7-ln",
    "scen7-ln-ext",
    "esm-scen7-ln-ext",
    "scen7-m",
    "esm-scen7-m",
    "scen7-m-ext",
    "esm-scen7-m-ext",
    "scen7-ml",
    "esm-scen7-ml",
    "scen7-ml-ext",
    "esm-scen7-ml-ext",
    "scen7-vl",
    "esm-scen7-vl",
    "scen7-vl-ext",
    "esm-scen7-vl-ext",
)


def _scen7_forcing_versions_for_suffix(suffix: str) -> Mapping[str, ForcingValue]:
    """Return ScenarioMIP forcing versions by replacing the template suffix."""
    return OrderedDict(
        (
            forcing_id,
            _replace_scen7_forcing_value_suffix(value, suffix=suffix),
        )
        for forcing_id, value in SCEN7_VL_FORCING_VERSIONS.items()
    )


def _scen7_suffix_from_slug(slug: str) -> str:
    """Return the scenario suffix from a ScenarioMIP experiment slug."""
    if slug.startswith(SCEN7_ESM_EXPERIMENT_PREFIX):
        return slug.removeprefix(SCEN7_ESM_EXPERIMENT_PREFIX)

    if slug.startswith(SCEN7_EXPERIMENT_PREFIX):
        return slug.removeprefix(SCEN7_EXPERIMENT_PREFIX)

    msg = f"Cannot derive ScenarioMIP suffix from {slug!r}."
    raise ValueError(msg)


def _replace_scen7_forcing_value_suffix(
    value: ForcingValue,
    *,
    suffix: str,
) -> ForcingValue:
    """Replace the ScenarioMIP template suffix in a forcing-version value."""
    return ForcingVersions(
        recommended=_replace_scen7_source_ids_suffix(
            value.recommended,
            suffix=suffix,
        ),
        acceptable=tuple(
            _replace_scen7_source_id_suffix(item, suffix=suffix)
            for item in value.acceptable
        ),
    )


def _replace_scen7_source_ids_suffix(
    source_ids: ForcingSourceIds,
    *,
    suffix: str,
) -> ForcingSourceIds:
    """Replace the ScenarioMIP template suffix in one or more source IDs."""
    if source_ids is None:
        return None

    if isinstance(source_ids, str):
        return _replace_scen7_source_id_suffix(source_ids, suffix=suffix)

    return tuple(
        _replace_scen7_source_id_suffix(source_id, suffix=suffix)
        for source_id in source_ids
    )


def _replace_scen7_source_id_suffix(source_id: str, *, suffix: str) -> str:
    """Replace the ScenarioMIP template suffix in one source ID."""
    return source_id.replace(
        f"-{SCEN7_TEMPLATE_SUFFIX}-",
        f"-{suffix}-",
    )


def _scen7_forcing_versions_for_slug(slug: str) -> Mapping[str, ForcingValue]:
    """Return ScenarioMIP forcing versions for an experiment slug."""
    return _scen7_forcing_versions_for_suffix(_scen7_suffix_from_slug(slug))


SCEN7_FORCING_VERSIONS_BY_SLUG = OrderedDict(
    (slug, _scen7_forcing_versions_for_slug(slug))
    for slug in SCEN7_FORCING_VERSION_SLUGS
)
SCEN7_H_FORCING_VERSIONS = SCEN7_FORCING_VERSIONS_BY_SLUG["scen7-h"]


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
    """Return recommended downloadable source IDs for one forcing value."""
    return tuple(
        source_id
        for source_id in recommended_forcing_values(value=value)
        if source_id not in NON_DOWNLOADABLE_FORCING_VALUES
    )


def recommended_forcing_values(
    *,
    value: ForcingValue,
) -> tuple[str, ...]:
    """Return the recommended values for one forcing."""
    if value.recommended is None:
        return ()

    if isinstance(value.recommended, str):
        return (value.recommended,)

    return tuple(value.recommended)


def acceptable_forcing_values(
    *,
    value: ForcingValue,
) -> tuple[str, ...]:
    """Return acceptable non-recommended values for one forcing."""
    return value.acceptable
