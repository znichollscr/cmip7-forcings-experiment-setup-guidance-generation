"""Branching text helpers for experiment guidance pages."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING

from local.rendering import (
    join_blocks,
    render_activity_index_link,
    render_link,
    render_term_reference,
)
from local.vocab import get_activity, get_experiment

if TYPE_CHECKING:
    from local.guidance import ExperimentPage


@dataclass(frozen=True)
class BranchFromParentAtAnyTime:
    """
    Branching from the parent experiment at any time
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the branch information as a string"""
        parent_experiment_esgvoc = experiment.parent_experiment_esgvoc
        if parent_experiment_esgvoc is None:
            msg = f"No parent experiment for {experiment.id_esgvoc}"
            raise AssertionError(msg)

        parent_experiment_link = render_link(
            parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
        )

        res = f"Branch from {parent_experiment_link} at a time of your choosing."

        return res


@dataclass(frozen=True)
class BranchFromParentAtTime:
    """
    Branching from the parent experiment at a specific time
    """

    branch_time: dt.datetime
    """
    Branch time
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the branch information as a string"""
        parent_experiment_esgvoc = experiment.parent_experiment_esgvoc
        if parent_experiment_esgvoc is None:
            msg = f"No parent experiment for {experiment.id_esgvoc}"
            raise AssertionError(msg)

        parent_experiment_link = render_link(
            parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
        )

        formatted_time = self.branch_time.date().isoformat()
        res = f"Branch from {parent_experiment_link} at {formatted_time}."

        return res


@dataclass(frozen=True)
class BranchFromParentEnd:
    """
    Branching from the end of the parent experiment with an optional increment
    """

    increment: dt.timedelta = dt.timedelta(days=0)
    """
    Increment from the end of the parent time experiment to add
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the branch information as a string"""
        parent_experiment_esgvoc = experiment.parent_experiment_esgvoc
        if parent_experiment_esgvoc is None:
            msg = f"No parent experiment for {experiment.id_esgvoc}"
            raise AssertionError(msg)

        parent_experiment_link = render_link(
            parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
        )

        branch_time = parent_experiment_esgvoc.end_timestamp + self.increment

        formatted_time = branch_time.date().isoformat()
        res = f"Branch from {parent_experiment_link} at {formatted_time}."

        return res


@dataclass(frozen=True)
class BranchAtSameTimeAsOtherExperiment:
    """
    Branch at the same time as another experiment
    """

    other_experiment: str
    """
    Experiment whose branching time we should match
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the branch information as a string"""
        parent_experiment_esgvoc = experiment.parent_experiment_esgvoc
        if parent_experiment_esgvoc is None:
            msg = f"No parent experiment for {experiment.id_esgvoc}"
            raise AssertionError(msg)

        parent_experiment_link = render_link(
            parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
        )

        experiment_to_match = get_experiment(self.other_experiment)
        experiment_to_match_link = render_link(
            experiment_to_match.drs_name, experiment_to_match.id
        )

        res = (
            f"Branch from {parent_experiment_link} "
            f"at the same time as {experiment_to_match_link}."
        )

        return res


def render_parent_and_branching_information(experiment: ExperimentPage) -> str:
    """Render parent-experiment information"""
    parent_experiment_esgvoc = experiment.experiment_esgvoc.parent_experiment
    if parent_experiment_esgvoc is None:
        msg = (
            f"{experiment.experiment_esgvoc.drs_name} doesn't have a parent experiment"
        )
        raise AssertionError(msg)

    if isinstance(parent_experiment_esgvoc, str):
        parent_experiment_esgvoc = get_experiment(parent_experiment_esgvoc)

    parent_activity_esgvoc = experiment.experiment_esgvoc.parent_activity
    if parent_activity_esgvoc is None:
        msg = f"{experiment.experiment_esgvoc.drs_name} doesn't have a parent activity"
        raise AssertionError(msg)

    if isinstance(parent_activity_esgvoc, str):
        parent_activity_esgvoc = get_activity(parent_activity_esgvoc)

    parent_mip_era = experiment.experiment_esgvoc.parent_mip_era
    if parent_mip_era is None:
        msg = f"{experiment.experiment_esgvoc.drs_name} doesn't have a parent mip_era"
        raise AssertionError(msg)

    if isinstance(parent_mip_era, str):
        raise TypeError(f"{type(parent_mip_era)=}")

    # TODO: push check that parent page exists into higher-up layers
    parent_experiment_link = render_link(
        parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
    )
    parent_activity_link = render_activity_index_link(parent_activity_esgvoc)

    parent_information = (
        f"The {experiment.drs_name} experiment branches from the "
        f"{parent_experiment_link} experiment (part of {parent_activity_link}). "
        "The parent experiment's MIP era is "
        f"{render_term_reference(parent_mip_era.drs_name, (parent_mip_era.url,))}."
    )

    branch_information = experiment.render_branch_information()

    # Options for branching information:
    # 1. branch at time of choosing
    # 1. branch at time of choosing, but ideally line up with other experiment
    # 1. branch at time of choosing, suggest [this approach]
    # 1. branch at end of parent experiment
    # 1. branch at end of parent experiment plus one day
    # 1. branch at specific time in parent experiment
    # 1. no parent experiment therefore no branching
    # 1. fully custom override

    res = join_blocks(
        parent_information,
        branch_information,
    )

    return res
