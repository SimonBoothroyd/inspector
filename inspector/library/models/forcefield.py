from typing import Dict, List, Tuple

from pydantic import BaseModel, Field

from inspector.library.models.smirnoff import SMIRNOFFParameterType


class AppliedParameters(BaseModel):

    parameters: Dict[str, List[SMIRNOFFParameterType]] = Field(
        ...,
        description="A dictionary of the parameters applied to the molecule, where each "
        "key is the name of a SMIRNOFF parameter and each value a list of the"
        "applied parameters associated with that handler.",
    )
    parameter_map: Dict[str, List[Tuple[int, ...]]] = Field(
        ...,
        description="A map between a the id of each applied parameter and a list of the "
        "indices of each group of atoms that the parameter is applied to."
        "\n"
        "For bond parameters for e.g. the value will be a list of tuples of two "
        "indices, while for torsions each tuple will contain four atom indices.",
    )
