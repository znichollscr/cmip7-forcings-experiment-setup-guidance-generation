"""Definitions for CMIP7 activities used by generated guidance."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from local.rendering import join_blocks, render_link

ActivityDescriptionModifier = Callable[[str], str]
SCENARIOMIP_DESCRIPTION_TRUNCATION_MARKER = "In CMIP7, the priority tier"


class MissingActivityDefinitionError(KeyError):
    """Raised when an index activity has no explicit definition."""


@dataclass(frozen=True)
class ActivityDefinition:
    """A CMIP7 activity used by generated guidance pages."""

    activity_id: str
    description_modifier: ActivityDescriptionModifier
    further_details: str = ""

    def description_from(self, esgvoc_description: str) -> str:
        """Return this activity's rendered description."""
        return self.description_modifier(esgvoc_description)


SCEN7_VL_LINK = render_link("`scen7-vl`", "scen7-vl")
SCENARIOMIP_FURTHER_DETAILS = join_blocks(
    (
        "The priority of ScenarioMIP experiments (expressed as Tier 1 and 2) "
        "is summarized in the flowchart below, which is based on Table 1 of "
        "[Van Vuuren et al. 2026]"
        "(https://gmd.copernicus.org/articles/19/2627/2026/). "
        "Emissions-driven experiments, indicated in yellow, have names "
        "beginning with `esm-`."
    ),
    "\n".join(
        (
            "- If your model is capable of running in emissions-driven mode, "
            "ScenarioMIP request emissions-driven scenarios, and additionally "
            "the concentration-driven experiment `scen7-m`, at Tier-1 "
            "(highest priority).",
            "- If your model will run only the concentration-driven "
            "experiments, ScenarioMIP request all concentration-driven "
            "scenarios at Tier-1.",
        )
    ),
    (
        "If you are running in emissions-driven mode, you are welcome to run "
        "other scenarios in concentration-driven mode, but they have not been "
        "assigned a specific tier (i.e., are lowest priority)."
    ),
    "\n".join(
        (
            "<figure>",
            '  <img src="figures/ScenarioMIP-tiers_v3.svg">',
            "  <figcaption>",
            (
                "    ScenarioMIP experiments, with emissions-driven experiments "
                "indicated in yellow."
            ),
            "  </figcaption>",
            "</figure>",
        )
    ),
).strip()

CMIP = ActivityDefinition(
    activity_id="cmip",
    description_modifier=lambda description: description,
)
AERCHEMMIP = ActivityDefinition(
    activity_id="aerchemmip",
    description_modifier=lambda description: description,
)
CFMIP = ActivityDefinition(
    activity_id="cfmip",
    description_modifier=lambda description: description,
)
C4MIP = ActivityDefinition(
    activity_id="c4mip",
    description_modifier=lambda description: description,
)
DAMIP = ActivityDefinition(
    activity_id="damip",
    description_modifier=lambda description: description,
)
GEOMIP = ActivityDefinition(
    activity_id="geomip",
    description_modifier=lambda description: description,
)
PMIP = ActivityDefinition(
    activity_id="pmip",
    description_modifier=lambda description: description,
)
RFMIP = ActivityDefinition(
    activity_id="rfmip",
    description_modifier=lambda description: description,
)
SCENARIOMIP = ActivityDefinition(
    activity_id="scenariomip",
    description_modifier=lambda description: description.split(
        SCENARIOMIP_DESCRIPTION_TRUNCATION_MARKER,
        maxsplit=1,
    )[0].rstrip(),
    further_details=SCENARIOMIP_FURTHER_DETAILS,
)

ACTIVITY_DEFINITIONS: tuple[ActivityDefinition, ...] = (
    CMIP,
    AERCHEMMIP,
    CFMIP,
    C4MIP,
    DAMIP,
    GEOMIP,
    PMIP,
    RFMIP,
    SCENARIOMIP,
)
ACTIVITY_DEFINITIONS_BY_ID: Mapping[str, ActivityDefinition] = {
    activity.activity_id: activity for activity in ACTIVITY_DEFINITIONS
}


def get_activity_definition(activity_id: str) -> ActivityDefinition:
    """Return the local activity definition for an esgvoc activity id."""
    try:
        return ACTIVITY_DEFINITIONS_BY_ID[activity_id]
    except KeyError as exc:
        msg = f"Activity {activity_id!r} has no explicit local definition."
        raise MissingActivityDefinitionError(msg) from exc
