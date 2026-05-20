"""GeoMIP experiment guidance pages."""

from __future__ import annotations

import datetime as dt

from local.branching import BranchFromParentAtTime
from local.forcings import (
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
    get_scen7_forcing_specification,
)
from local.guidance import ExperimentPage
from local.rendering import render_link

GEOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="g7-1p5k-sai",
        render_description=lambda _: "Stablisation of global-mean temperature at 1.5C by increasing stratospheric sulfur forcing.",
        branch_information=BranchFromParentAtTime(dt.datetime(2035, 1, 1)),
        # Checking if the modification is to forcing or something else:
        # see https://github.com/WCRP-CMIP/cmip7-guidance/issues/166
        experiment_setup_notes=(
            f"This experiment is the same as {render_link('scen7-ml', 'scen7-ml')}, "
            "except you should increase the stratospheric sulfur forcing "
            "to whatever level is required to stablise global-mean temperatures at 1.5C "
            "after the branching point. "
            "We are still seeking clarification about exactly what 'increase the stratospheric sulfur forcing' means, "
            "see [https://github.com/WCRP-CMIP/cmip7-guidance/issues/166]() "
            "(and please comment there if you can clarify for us)."
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="scen7-ml",
                )
                for v in get_scen7_forcing_specification("scen7-ml").specific_forcings
            ),
        ),
    ),
)
