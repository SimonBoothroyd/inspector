from typing import List

from pydantic import BaseModel, Field, conlist, validator


class MinimizationFrame(BaseModel):
    """Contains the output of a single iteration from an energy minimization."""

    geometry: conlist(float, min_items=1) = Field(
        ...,
        description="A flattened array of the molecules XYZ atomic coordinates [Å] "
        "with length=n_atoms*3 which can be reshaped to array with shape=(n_atoms, 3).",
    )
    potential_energy: float = Field(
        ...,
        description="The potential energy of the molecule at this frame [kJ / mol].",
    )

    @validator("geometry")
    def _validate_geometry(cls, v):
        assert len(v) % 3 == 0, "geometry length not divisible by three."
        return v


class MinimizationTrajectory(BaseModel):
    """Contains the trajectory of outputs (both conformers and energies) produced by each
    iteration of an energy minimization."""

    frames: List[MinimizationFrame] = Field(
        ...,
        description="The outputs of each iteration of the minimization.",
    )
