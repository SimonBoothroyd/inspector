import numpy
import pytest
from pydantic import ValidationError
from simtk import unit

from inspector.library.models.molecule import InvalidMoleculeError, RESTMolecule
from inspector.tests import does_not_raise


@pytest.mark.parametrize(
    "perturbed_kwargs, expected_raises, expected_message",
    [
        # Valid kwargs
        ({}, does_not_raise(), None),
        # Incorrect number of coordinates.
        (
            {"geometry": [0.0] * 1},
            pytest.raises(ValidationError),
            "geometry length not divisible by three",
        ),
        (
            {"geometry": [0.0] * 3},
            pytest.raises(ValidationError),
            "incorrect geometry length",
        ),
        # Incorrect bond atom index.
        (
            {"connectivity": [(0, -1, 1)]},
            pytest.raises(ValidationError),
            "atom index out of range",
        ),
    ],
)
def test_rest_molecule_init(
    perturbed_kwargs,
    expected_raises,
    expected_message,
):

    model_kwargs = {
        "symbols": ["C", "H", "H", "H", "H"],
        "connectivity": [(0, 1, 1)],
        "geometry": [0.0] * 15,
    }
    model_kwargs.update(perturbed_kwargs)

    with expected_raises as error_info:
        RESTMolecule(**model_kwargs)

    if expected_message is not None:
        assert expected_message in str(error_info.value)


def test_from_off_invalid_molecule(methane):

    methane._conformers = []

    with pytest.raises(InvalidMoleculeError) as error_info:
        RESTMolecule.from_openff(methane)

    assert "The specified molecule was invalid" in str(error_info.value)
    assert "The OpenFF molecule must contain exactly one" in str(error_info.value)


def test_rest_off_molecule_round_trip(methane):

    rest_methane = RESTMolecule.from_openff(methane)

    assert len(rest_methane.symbols) == 5
    assert len(rest_methane.connectivity) == 4
    assert len(rest_methane.geometry) == 15

    off_molecule = rest_methane.to_openff()
    assert methane.to_smiles() == off_molecule.to_smiles()

    assert numpy.allclose(
        methane.conformers[0].value_in_unit(unit.angstrom),
        off_molecule.conformers[0].value_in_unit(unit.angstrom),
    )
