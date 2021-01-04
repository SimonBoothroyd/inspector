from typing import Literal, Optional

from pydantic import BaseModel, Field, validator

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

    smirnoff_xml: Optional[str] = Field(
        ...,
        description="The SMIRNOFF serialized force field to apply to the ``molecule``. "
        "This field is mutually exclusive with ``openff_name``.",
    )
    openff_name: Optional[str] = Field(
        ...,
        description="The name of an OpenFF released force field to apply to the "
        "``molecule``. This field is mutually exclusive with ``smirnoff_xml``.",
    )

    @validator("openff_name")
    def _validate_mutual_exclusive(cls, v, values):

        assert (v is None or values["smirnoff_xml"] is None) and (
            v is not None or values["smirnoff_xml"] is not None
        ), "exactly one of ``smirnoff_xml`` and ``openff_name`` must be specified."
        return v


class SummarizeGeometryBody(BaseModel):
    """The expected body of the ``/molecules/geometry`` POST endpoint."""

    molecule: RESTMolecule = Field(
        ..., description="The molecule whose geometry should be summarised."
    )
