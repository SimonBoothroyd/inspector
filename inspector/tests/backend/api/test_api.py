from io import StringIO

import numpy
import pytest
from fastapi.testclient import TestClient
from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField
from simtk import unit

from inspector.backend.core.config import settings
from inspector.backend.models.molecules import (
    ApplyParametersBody,
    MoleculeToJSONBody,
    SummarizeGeometryBody,
)
from inspector.library.forcefield import label_molecule
from inspector.library.geometry import summarize_geometry
from inspector.library.models.forcefield import AppliedParameters
from inspector.library.models.geometry import GeometrySummary
from inspector.library.models.minimization import MinimizationTrajectory
from inspector.library.models.molecule import RESTMolecule
from inspector.tests import compare_pydantic_models


def test_molecule_to_json(rest_client: TestClient, methane: Molecule):

    with StringIO() as file_buffer:

        methane.to_file(file_buffer, "SDF")
        body = MoleculeToJSONBody(file_contents=file_buffer.getvalue())

    request = rest_client.post(
        f"{settings.API_DEV_STR}/molecule/json", data=body.json()
    )
    request.raise_for_status()

    response_model = RESTMolecule.parse_raw(request.text).to_openff()

    assert response_model.to_smiles() == methane.to_smiles()

    assert numpy.allclose(
        methane.conformers[0].value_in_unit(unit.angstrom),
        response_model.conformers[0].value_in_unit(unit.angstrom),
        atol=1e-4,
    )


@pytest.mark.parametrize("as_object", [False, True])
def test_apply_parameters(rest_client: TestClient, methane: Molecule, as_object: bool):

    force_field_name = "openff-1.0.0.offxml"
    force_field = ForceField(force_field_name)

    if not as_object:
        model_kwargs = {"smirnoff_xml": None, "openff_name": force_field_name}
    else:
        model_kwargs = {"smirnoff_xml": force_field.to_string(), "openff_name": None}

    body = ApplyParametersBody(
        molecule=RESTMolecule.from_openff(methane), **model_kwargs
    )

    request = rest_client.post(
        f"{settings.API_DEV_STR}/molecule/parameters", data=body.json()
    )
    request.raise_for_status()

    response_model = AppliedParameters.parse_raw(request.text)
    expected_model = label_molecule(methane, force_field)

    compare_pydantic_models(response_model, expected_model)


def test_summarize_geometry(rest_client: TestClient, methane: Molecule):

    body = SummarizeGeometryBody(molecule=RESTMolecule.from_openff(methane))

    request = rest_client.post(
        f"{settings.API_DEV_STR}/molecule/geometry", data=body.json()
    )
    request.raise_for_status()

    response_model = GeometrySummary.parse_raw(request.text)
    expected_model = summarize_geometry(methane, methane.conformers[0])

    compare_pydantic_models(response_model, expected_model)


@pytest.mark.parametrize("as_object", [False, True])
def test_minimize_conformer(
    rest_client: TestClient, methane: Molecule, as_object: bool
):

    force_field_name = "openff_unconstrained-1.0.0.offxml"
    force_field = ForceField(force_field_name)

    if not as_object:
        model_kwargs = {"smirnoff_xml": None, "openff_name": force_field_name}
    else:
        model_kwargs = {"smirnoff_xml": force_field.to_string(), "openff_name": None}

    body = ApplyParametersBody(
        molecule=RESTMolecule.from_openff(methane), **model_kwargs
    )

    request = rest_client.post(
        f"{settings.API_DEV_STR}/molecule/minimize", data=body.json()
    )
    request.raise_for_status()

    response_model = MinimizationTrajectory.parse_raw(request.text)

    assert len(response_model.frames) > 1
    assert (
        response_model.frames[0].potential_energy
        > response_model.frames[-1].potential_energy
    )
