from typing import Dict

from pydantic import BaseModel, Field


class DecomposedEnergy(BaseModel):
    """A class which stores the contribution of each SMIRNOFF parameter to the total
    potential energy of a system."""

    valence_energies: Dict[str, Dict[str, float]] = Field(
        ...,
        description="The energy contributions of each valence parameter type stored in "
        "a dictionary of the form ``energy_per_parameter[HANDLER_TAG][PARAMETER_ID]`` "
        "with units of [kJ / mol].",
    )

    vdw_energy: float = Field(
        ...,
        description="The contribution of the vdW interactions to the total potential "
        "energy [kJ / mol].",
    )
    electrostatic_energy: float = Field(
        ...,
        description="The contribution of the electrostatic interactions to the total "
        "potential energy [kJ / mol].",
    )
