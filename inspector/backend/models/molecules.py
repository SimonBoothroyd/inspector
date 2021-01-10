from typing import Literal, Optional

from pydantic import BaseModel, Field, validator

from inspector.library.models.molecule import RESTMolecule


class _BaseForceFieldBody(BaseModel):
    """The base model for endpoints which require a force field."""

    smirnoff_xml: Optional[str] = Field(
        None,
        description="The SMIRNOFF serialized force field. This field is mutually "
        "exclusive with ``openff_name``.",
    )
    openff_name: Optional[str] = Field(
        None,
        description="The name of an OpenFF released force field. This field is mutually "
        "exclusive with ``smirnoff_xml``.",
    )

    @validator("openff_name")
    def _validate_mutual_exclusive(cls, v, values):

        smirnoff_xml = values.get("smirnoff_xml", None)

        assert (v is None or smirnoff_xml is None) and (
            v is not None or smirnoff_xml is not None
        ), "exactly one of ``smirnoff_xml`` and ``openff_name`` must be specified."

        return v


class MoleculeToJSONBody(BaseModel):
    """The expected body of the ``/molecules/json`` POST endpoint."""

    file_contents: str = Field(..., description="The contents of the molecule file.")
    file_format: Literal["SDF"] = Field("SDF", description="The format of the file.")


class SummarizeGeometryBody(BaseModel):
    """The expected body of the ``/molecules/geometry`` POST endpoint."""

    molecule: RESTMolecule = Field(
        ..., description="The molecule whose geometry should be summarised."
    )


class ApplyParametersBody(_BaseForceFieldBody):
    """The expected body of the ``/molecules/parameters`` POST endpoint."""

    molecule: RESTMolecule = Field(
        ..., description="The molecule to apply the parameters to."
    )

    @validator("openff_name")
    def _validate_mutual_exclusive(cls, v, values):

        smirnoff_xml = values.get("smirnoff_xml", None)

        assert (v is None or smirnoff_xml is None) and (
            v is not None or smirnoff_xml is not None
        ), "exactly one of ``smirnoff_xml`` and ``openff_name`` must be specified."

        return v


class MinimizeConformerBody(_BaseForceFieldBody):
    """The expected body of the ``/molecules/minimize`` POST endpoint."""

    molecule: RESTMolecule = Field(
        ..., description="The molecule containing the conformer to minimize."
    )

    method: Literal["L-BFGS-B"] = Field(
        "L-BFGS-B", description="The minimization algorithm to use."
    )
