"""Output time axis text helpers for experiment guidance pages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from local.rendering import block, join_blocks, render_link
from local.vocab import get_experiment

if TYPE_CHECKING:
    from local.guidance import ExperimentPage


START_OF_YEAR_MONTH = 1
START_OF_YEAR_DAY = 1
END_OF_YEAR_MONTH = 12
END_OF_YEAR_DAY = 31

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
        minimum_simulation_years = _minimum_simulation_years(experiment_esgvoc)

        if start_date and end_date:
            return _render_fixed_start_and_end_time_axis(
                experiment=experiment,
                start_date=start_date,
                end_date=end_date,
                minimum_simulation_years=minimum_simulation_years,
            )

        res = _render_open_time_axis(
            start_date=start_date,
            end_date=end_date,
        )
        if minimum_simulation_years:
            year = _year_word(minimum_simulation_years)
            res = (
                f"{res} You must perform at least "
                f"{minimum_simulation_years} simulation {year}."
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
        base = _render_open_base_time_axis(experiment)

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
        base = _render_open_base_time_axis(experiment)

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
        base = _render_open_base_time_axis(experiment)

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


def _minimum_simulation_years(experiment_esgvoc) -> int | float | None:
    minimum_years = experiment_esgvoc.min_number_yrs_per_sim
    if minimum_years is not None and minimum_years.is_integer():
        return int(minimum_years)

    return minimum_years


def _render_fixed_start_and_end_time_axis(
    *,
    experiment: ExperimentPage,
    start_date,
    end_date,
    minimum_simulation_years: int | float | None,
) -> str:
    if minimum_simulation_years:
        if (
            start_date.month != START_OF_YEAR_MONTH
            or start_date.day != START_OF_YEAR_DAY
            or end_date.month != END_OF_YEAR_MONTH
            or end_date.day != END_OF_YEAR_DAY
        ):
            raise NotImplementedError(experiment)

        full_simulation_years = end_date.year - start_date.year + 1
        year = _year_word(minimum_simulation_years)
        if minimum_simulation_years == full_simulation_years:
            return (
                "Your output time axis must start on "
                f"{start_date.date().isoformat()} "
                "and must end on "
                f"{end_date.date().isoformat()}. "
                f"You must perform the full simulation "
                f"i.e. {minimum_simulation_years} "
                f"simulation {year}."
            )

        return (
            "Your output time axis must start on "
            f"{start_date.date().isoformat()} "
            "and must not end later than "
            f"{end_date.date().isoformat()}. "
            f"You must perform at least "
            f"{minimum_simulation_years} simulation {year}."
        )

    msg = "Expected minimum simulation years with fixed start and end"
    raise AssertionError(msg)


def _render_open_time_axis(*, start_date, end_date) -> str:
    if start_date:
        return (
            "Your output time axis must start on "
            f"{start_date.date().isoformat()}. "
            "You are free to end the time axis of your outputs "
            "at whatever time you like that is compatible with the start date."
        )

    if end_date:
        return (
            "Your output time axis must not end later than "
            f"{end_date.date().isoformat()}. "
            "You are free to start the time axis of your outputs "
            "at whatever time you like that is compatible with the end date."
        )

    return (
        "You are free to start and end the time axis of your outputs "
        "at whatever time you like "
        "(e.g. starting at year 1, or 1850, or year 500)."
    )


def _render_open_base_time_axis(experiment: ExperimentPage) -> str:
    experiment_esgvoc = experiment.experiment_esgvoc
    if (
        experiment_esgvoc.start_timestamp is not None
        or experiment_esgvoc.end_timestamp is not None
    ):
        msg = "Expected no specific start and end"
        raise AssertionError(msg)

    return EsgvocDrivenOutputTimeAxisInformation().render(experiment)


def _year_word(years: int | float) -> str:
    return "years" if years > 1 else "year"
