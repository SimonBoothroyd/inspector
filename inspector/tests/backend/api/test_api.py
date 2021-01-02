from io import StringIO

import numpy
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


def test_apply_parameters(
    rest_client: TestClient, methane: Molecule, openff_1_0_0: ForceField
):

    body = ApplyParametersBody(
        molecule=RESTMolecule.from_openff(methane),
        smirnoff_xml=openff_1_0_0.to_string(),
    )

    request = rest_client.post(
        f"{settings.API_DEV_STR}/molecule/parameters", data=body.json()
    )
    request.raise_for_status()

    response_model = AppliedParameters.parse_raw(request.text)
    expected_model = label_molecule(methane, openff_1_0_0)

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
