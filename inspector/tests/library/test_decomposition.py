import numpy
from openforcefield.typing.engines.smirnoff import ForceField
from simtk import unit

from inspector.library.decomposition import evaluate_energy, evaluate_per_term_energies
from inspector.library.models.molecule import RESTMolecule


def test_evaluate_per_term_energies(z_propenal, openff_1_0_0):

    z_propenal._conformers = [z_propenal.conformers[0]]
    molecule = RESTMolecule.from_openff(z_propenal)

    # Compute the expected energy
    unconstrained_ff = ForceField("openff_unconstrained-1.0.0.offxml")

    omm_system = unconstrained_ff.create_openmm_system(z_propenal.to_topology())
    expected_energy, _ = evaluate_energy(omm_system, z_propenal.conformers[0])

    # Compute the decomposed energies.
    decomposed_energy = evaluate_per_term_energies(
        molecule, z_propenal.conformers[0], openff_1_0_0
    )

    total_valence_energy = sum(
        valence_energy
        for handler_name in decomposed_energy.valence_energies
        for valence_energy in decomposed_energy.valence_energies[handler_name].values()
    )

    total_energy = (
        total_valence_energy
        + decomposed_energy.vdw_energy
        + decomposed_energy.electrostatic_energy
    )

    assert numpy.isclose(
        expected_energy.value_in_unit(unit.kilojoules_per_mole), total_energy
    )
