import pytest
from openforcefield.topology import Molecule

from inspector.library.geometry import summarize_geometry
from inspector.library.models.molecule import RESTMolecule
from inspector.tests import compare_pydantic_models


@pytest.mark.parametrize("conformer_index", [0, 1])
def test_summarize_geometry(z_propenal: Molecule, conformer_index: int):

    z_propenal._conformers = [z_propenal.conformers[conformer_index]]

    # Compute the summary using both the OpenFF and REST molecule representations.
    summary = summarize_geometry(z_propenal, z_propenal.conformers[0])

    summary_rest = summarize_geometry(
        RESTMolecule.from_openff(z_propenal), z_propenal.conformers[0]
    )

    compare_pydantic_models(summary, summary_rest)

    assert len(summary.bond_lengths) == z_propenal.n_bonds
    assert len(summary.bond_angles) == z_propenal.n_angles
    assert len(summary.proper_dihedral_angles) == z_propenal.n_propers
    assert len(summary.hydrogen_bonds) == 1 - conformer_index
