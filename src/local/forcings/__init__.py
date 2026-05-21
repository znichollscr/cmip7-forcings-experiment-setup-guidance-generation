"""
Forcings details
"""

# TODO: move other forcings content into this module
from .experiment_forcings_specifications import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    HISTORICAL_FORCINGS_SPECIFICATION_AMIP_SSTS,
    NOT_AVAILABLE_YET,
    PICONTROL_FORCINGS_SPECIFICATION,
    get_scen7_forcing_specification,
)
from .specification import (
    ForcingSpecification,
    Input4MIPsBasedForcingSpecification,
    NonInput4MIPsBasedForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)

__all__ = [
    "HISTORICAL_FORCINGS_SPECIFICATION",
    "HISTORICAL_FORCINGS_SPECIFICATION_AMIP_SSTS",
    "NOT_AVAILABLE_YET",
    "PICONTROL_FORCINGS_SPECIFICATION",
    "ForcingSpecification",
    "Input4MIPsBasedForcingSpecification",
    "NonInput4MIPsBasedForcingSpecification",
    "OtherExperimentBasedForcingSpecification",
    "get_scen7_forcing_specification",
]
