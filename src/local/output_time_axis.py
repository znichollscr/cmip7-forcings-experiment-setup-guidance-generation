"""Output time axis text helpers for experiment guidance pages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from local.rendering import block, join_blocks, render_link
from local.vocab import get_experiment

if TYPE_CHECKING:
    from local.guidance import ExperimentPage


# Usually quite standard and simple.
# Sometimes need lines like,
# "You can choose start and end dates, but to keep life for analysts easy,
# recommend to keep continuous time axis from branch point/
# line up with equivalent section from parent experiment/
# line up with time axis of other experiment" etc.


@dataclass(frozen=True)
class EsgvocDrivenOutputTimeAxisInformation:
    """
    Output time axis information based on esgvoc alone
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the output time axis information as a string"""
        experiment_esgvoc = experiment.experiment_esgvoc
        start_date = experiment_esgvoc.start_timestamp
        end_date = experiment_esgvoc.end_timestamp
        min_number_years_per_simulation = experiment_esgvoc.min_number_yrs_per_sim
        min_number_years_per_simulation = (
            int(min_number_years_per_simulation)
            if min_number_years_per_simulation is not None
            and min_number_years_per_simulation.is_integer()
            else min_number_years_per_simulation
        )

        if start_date and end_date:
            if min_number_years_per_simulation:
                START_OF_YEAR_MONTH = 1
                START_OF_YEAR_DAY = 1
                END_OF_YEAR_MONTH = 12
                END_OF_YEAR_DAY = 31
                if (
                    start_date.month != START_OF_YEAR_MONTH
                    or start_date.day != START_OF_YEAR_DAY
                    or end_date.month != END_OF_YEAR_MONTH
                    or end_date.day != END_OF_YEAR_DAY
                ):
                    raise NotImplementedError(experiment)
                full_simulation_years = end_date.year - start_date.year + 1

                year = "years" if min_number_years_per_simulation > 1 else "year"
                if min_number_years_per_simulation == full_simulation_years:
                    res = (
                        "Your output time axis must start on "
                        f"{start_date.date().isoformat()} "
                        "and must end on "
                        f"{end_date.date().isoformat()}. "
                        f"You must perform the full simulation "
                        f"i.e. {min_number_years_per_simulation} "
                        f"simulation {year}."
                    )

                else:
                    res = (
                        "Your output time axis must start on "
                        f"{start_date.date().isoformat()} "
                        "and must not end later than "
                        f"{end_date.date().isoformat()}. "
                        f"You must perform at least "
                        f"{min_number_years_per_simulation} simulation {year}."
                    )

        else:
            if start_date:
                res = (
                    "Your output time axis must start on "
                    f"{start_date.date().isoformat()}. "
                    "You are free to end the time axis of your outputs "
                    "at whatever time you like that is compatible with the start date."
                )

            elif end_date:
                res = (
                    "Your output time axis must not end later than "
                    f"{end_date.date().isoformat()}. "
                    "You are free to start the time axis of your outputs "
                    "at whatever time you like that is compatible with the end date."
                )

            else:
                res = (
                    "You are free to start and end the time axis of your outputs "
                    "at whatever time you like "
                    "(e.g. starting at year 1, or 1850, or year 500)."
                )

            if min_number_years_per_simulation:
                year = "years" if min_number_years_per_simulation > 1 else "year"
                res = (
                    f"{res} You must perform at least "
                    f"{min_number_years_per_simulation} simulation {year}."
                )

        return res


@dataclass(frozen=True)
class PiClimOutputTimeAxisInformation:
    """
    Output time axis information for piClim-* experiments
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the output time axis information as a string"""
        experiment_esgvoc = experiment.experiment_esgvoc
        if (
            experiment_esgvoc.start_timestamp is not None
            or experiment_esgvoc.end_timestamp is not None
        ):
            msg = "Expected no specific start and end"
            raise AssertionError(msg)

        base = EsgvocDrivenOutputTimeAxisInformation().render(experiment)

        if experiment_esgvoc.id == "piclim-control":
            extra_notes = block(
                f"""
            If you have no strong feeling, then it may be clearest to set the start time
            to the middle of the period over which the climatology
            was taken from the pre-industrial control experiment.
            For example, if your climatology is taken over the years 120-150
            in the pre-industrial control experiment,
            then you could start the time axis
            of your {experiment_esgvoc.drs_name} output at year 135.
            """
            )
        else:
            piclim_control_exp = get_experiment("piclim-control")
            piclim_control_link = render_link(
                piclim_control_exp.drs_name, piclim_control_exp.id
            )
            extra_notes = block(
                f"""
            If you have no strong feeling, then you will make life simplest for analysts
            if you use the same time axis as {piclim_control_link}.
            """
            )

        res = join_blocks(
            base,
            extra_notes,
        )

        return res


@dataclass(frozen=True)
class RecommendContinueFromBranchPointTimeAxisInformation:
    """
    Output time axis recommended to continue from branch in parent
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the output time axis information as a string"""
        experiment_esgvoc = experiment.experiment_esgvoc
        if (
            experiment_esgvoc.start_timestamp is not None
            or experiment_esgvoc.end_timestamp is not None
        ):
            msg = "Expected no specific start and end"
            raise AssertionError(msg)

        base = EsgvocDrivenOutputTimeAxisInformation().render(experiment)

        extra_notes = block(
            """
        If you have no strong feeling, then you will make life simplest for analysts
        if you continue your time axis from the branching point
        (e.g. if you branch on 1500-01-01, start your time axis on 1500-01-01).
        """
        )

        res = join_blocks(
            base,
            extra_notes,
        )

        return res


@dataclass(frozen=True)
class RecommendSameAsOtherExperimentTimeAxisInformation:
    """
    Output time axis information for piClim-* experiments
    """

    other_experiment: str
    """Other experiment whose time axis should be matched"""

    def render(self, experiment: ExperimentPage) -> str:
        """Render the output time axis information as a string"""
        experiment_esgvoc = experiment.experiment_esgvoc
        if (
            experiment_esgvoc.start_timestamp is not None
            or experiment_esgvoc.end_timestamp is not None
        ):
            msg = "Expected no specific start and end"
            raise AssertionError(msg)

        base = EsgvocDrivenOutputTimeAxisInformation().render(experiment)

        other_exp = get_experiment(self.other_experiment)
        other_exp_link = render_link(other_exp.drs_name, other_exp.id)
        extra_notes = block(
            f"""
        If you have no strong feeling, then you will make life simplest for analysts
        if you use the same time axis as {other_exp_link}.
        """
        )

        res = join_blocks(
            base,
            extra_notes,
        )

        return res
