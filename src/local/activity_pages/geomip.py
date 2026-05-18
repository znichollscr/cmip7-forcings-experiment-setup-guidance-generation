"""GeoMIP experiment guidance pages."""

from __future__ import annotations

import datetime as dt

from local.branching import BranchFromParentAtTime
from local.guidance import ExperimentPage
from local.rendering import render_link

SCEN7_M_LINK = render_link("scen7-ml simulation", "scen7-ml")


GEOMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="g7-1p5k-sai",
        branch_information=BranchFromParentAtTime(dt.datetime(2035, 1, 1)),
    ),
    # ExperimentPageOld(
    #     slug="g7-1p5k-sai",
    #     experiment_setup=join_blocks(
    #         f"The `{get_experiment('g7-1p5k-sai').drs_name}` simulation is a branch from the {SCEN7_M_LINK}.",
    #         f"The simulation should follow the {SCEN7_M_LINK} scenario until 2035.",
    #         block(
    #             """
    #             After 2035, increase the stratospheric sulfur forcing until the
    #             global-mean temperature is stabilized at 1.5C.
    #             """
    #         ),
    #     ).strip(),
    #     forcing_headlines=(
    #         f"The `{get_experiment('g7-1p5k-sai').drs_name}` experiment is a time-varying forcings experiment."
    #     ),
    #     notes=join_blocks(
    #         f"See notes for the {SCEN7_M_LINK}.",
    #         "You have to adjust the stratospheric sulfur forcing yourself to achieve temperature stabilization.",
    #     ).strip(),
    #     versions_to_use=join_blocks(
    #         (
    #             "For all forcings except the stratospheric sulfur forcing, the "
    #             f"forcing versions relevant for this simulation are the same as "
    #             f"for the {SCEN7_M_LINK}."
    #         ),
    #         (
    #             "The stratospheric sulfur forcing must be adjusted by each "
    #             "modeling group to achieve stable temperatures at 1.5C."
    #         ),
    #     ).strip(),
    #     getting_the_data=render_data_access_body(
    #         experiment_name="G7-1p5K-SAI",
    #         source_ids=source_ids_from_forcing_versions(
    #             SCEN7_FORCING_VERSIONS_BY_SLUG["scen7-ml"],
    #         ),
    #     ),
    # ),
)
