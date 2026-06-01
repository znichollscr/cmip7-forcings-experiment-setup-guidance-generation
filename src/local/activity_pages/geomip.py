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
from local.mip_co_chair_review import get_pending_review_aft_experiments
from local.rendering import render_link

GEOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="g7-1p5k-sai",
        render_description=lambda _: (
            "Stablisation of global-mean temperature at 1.5C by increasing stratospheric sulfur forcing."
        ),
        branch_information=BranchFromParentAtTime(dt.datetime(2035, 1, 1)),
        experiment_setup_notes=(
            f"This experiment is the same as {render_link('scen7-ml', 'scen7-ml')}, "
            "except you should increase the stratospheric sulfur forcing "
            "through the injection of SO₂ at 30N and 30S year round, "
            "or (for models with no prognostic sulfate cycle) "
            "through the addition of a prescribed stratospheric aerosol field provided "
            "by the GeoMIP team. "
            "The stratospheric sulfur forcing should be increased "
            "to whatever level is required to stablise global-mean temperatures at 1.5C "
            "after the branching point. "
            "For details, see [Visioni et al., 2026](https://doi.org/10.5194/egusphere-2026-2417), "
            "Section 3.1.2."
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
        mip_co_chair_review=get_pending_review_aft_experiments("geomip"),
    ),
)
