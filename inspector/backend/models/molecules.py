from typing import Literal

from pydantic import BaseModel, Field

from inspector.library.models.molecule import RESTMolecule


class MoleculeToJSONBody(BaseModel):
    """The expected body of the ``/molecules/json`` POST endpoint."""

    file_contents: str = Field(..., description="The contents of the molecule file.")
    file_format: Literal["SDF"] = Field("SDF", description="The format of the file.")


class ApplyParametersBody(BaseModel):
    """The expected body of the ``/molecules/parameters`` POST endpoint."""

    molecule: RESTMolecule = Field(
        ..., description="The molecule to apply the paramers to."
    )
    smirnoff_xml: str = Field(
        ...,
        description="The OFFXML serialized force field to apply to the ``molecule``.",
    )


class SummarizeGeometryBody(BaseModel):
    """The expected body of the ``/molecules/geometry`` POST endpoint."""

    molecule: RESTMolecule = Field(
        ..., description="The molecule whose geometry should be summarised."
    )
