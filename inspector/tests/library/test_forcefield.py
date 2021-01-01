from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField

from inspector.library.forcefield import label_molecule
from inspector.library.models.molecule import RESTMolecule
from inspector.tests import compare_pydantic_models


def test_label_molecules(methane: Molecule, openff_1_0_0: ForceField):

    applied_parameters = label_molecule(methane, openff_1_0_0)

    assert {*applied_parameters.parameters} == {"Constraints", "Bonds", "Angles", "vdW"}

    assert len(applied_parameters.parameters["Constraints"]) == 1
    assert applied_parameters.parameters["Constraints"][0].id == "c1"

    assert len(applied_parameters.parameters["Bonds"]) == 1
    assert applied_parameters.parameters["Bonds"][0].id == "b83"

    assert len(applied_parameters.parameters["Angles"]) == 1
    assert applied_parameters.parameters["Angles"][0].id == "a2"

    assert len(applied_parameters.parameters["vdW"]) == 2
    assert applied_parameters.parameters["vdW"][0].id == "n16"


def test_label_molecules_rest(methane: Molecule, openff_1_0_0: ForceField):
    openff_parameters = label_molecule(methane, openff_1_0_0)
    rest_parameters = label_molecule(RESTMolecule.from_openff(methane), openff_1_0_0)

    compare_pydantic_models(openff_parameters, rest_parameters)
