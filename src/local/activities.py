"""Definitions for CMIP7 activities used by generated guidance."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

import local.vocab
from local.rendering import join_blocks, render_activity_index_link, render_link

ActivityDescriptionModifier = Callable[[str], str]
SCENARIOMIP_DESCRIPTION_TRUNCATION_MARKER = "In CMIP7, the priority tier"


class MissingActivityDefinitionError(KeyError):
    """Raised when an index activity has no explicit definition."""


def get_tier_from_esgvoc(experiment_id_esgvoc: str) -> str:
    """
    Get tier from esgvoc
    """
    tier = local.vocab.get_experiment(experiment_id_esgvoc).tier

    return str(tier)


@dataclass(frozen=True)
class Activity:
    """Activity i.e. MIP e.g. DAMIP, C4MIP"""

    activity_id: str
    description_modifier: ActivityDescriptionModifier
    further_details: str = ""
    get_tier: Callable[[str], str] = get_tier_from_esgvoc

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

CMIP = Activity(
    activity_id="cmip",
    description_modifier=lambda description: description,
)
AERCHEMMIP = Activity(
    activity_id="aerchemmip",
    description_modifier=lambda description: description,
)
CFMIP = Activity(
    activity_id="cfmip",
    description_modifier=lambda description: description,
)
C4MIP = Activity(
    activity_id="c4mip",
    description_modifier=lambda description: description,
)
DAMIP = Activity(
    activity_id="damip",
    description_modifier=lambda description: description,
)
GEOMIP = Activity(
    activity_id="geomip",
    description_modifier=lambda description: description,
)
PMIP = Activity(
    activity_id="pmip",
    description_modifier=lambda description: description,
)
RFMIP = Activity(
    activity_id="rfmip",
    description_modifier=lambda description: description,
)
SCENARIOMIP = Activity(
    activity_id="scenariomip",
    description_modifier=lambda description: description.split(
        SCENARIOMIP_DESCRIPTION_TRUNCATION_MARKER,
        maxsplit=1,
    )[0].rstrip(),
    further_details=SCENARIOMIP_FURTHER_DETAILS,
    get_tier=lambda _: f"See {render_activity_index_link('scenariomip')} information",
)

ACTIVITY_DEFINITIONS: tuple[Activity, ...] = (
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
ACTIVITY_DEFINITIONS_BY_ID: Mapping[str, Activity] = {
    activity.activity_id: activity for activity in ACTIVITY_DEFINITIONS
}


def get_activity_definition(id_esgvoc: str) -> Activity:
    """Return the activity definition for an esgvoc id."""
    try:
        return ACTIVITY_DEFINITIONS_BY_ID[id_esgvoc]
    except KeyError as exc:
        msg = f"Activity {id_esgvoc!r} has no explicit local definition."
        raise MissingActivityDefinitionError(msg) from exc
