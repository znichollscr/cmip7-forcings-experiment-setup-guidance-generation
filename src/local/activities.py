"""Definitions for CMIP7 activities used by generated guidance."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

ActivityDescriptionModifier = Callable[[str], str]


class MissingActivityDefinitionError(KeyError):
    """Raised when an index activity has no explicit definition."""


@dataclass(frozen=True)
class ActivityDefinition:
    """A CMIP7 activity used by generated guidance pages."""

    activity_id: str
    description_modifier: ActivityDescriptionModifier

    def description_from(self, esgvoc_description: str) -> str:
        """Return this activity's rendered description."""
        return self.description_modifier(esgvoc_description)


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
SCENARIOMIP = ActivityDefinition(
    activity_id="scenariomip",
    description_modifier=lambda description: description,
)

ACTIVITY_DEFINITIONS: tuple[ActivityDefinition, ...] = (
    CMIP,
    AERCHEMMIP,
    CFMIP,
    C4MIP,
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
