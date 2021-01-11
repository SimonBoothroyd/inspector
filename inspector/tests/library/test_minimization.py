import numpy
import pytest
from openforcefield.typing.engines.smirnoff import ForceField
from scipy import optimize
from scipy.optimize import OptimizeResult
from simtk import openmm, unit
from simtk.openmm import app

from inspector.library.minimization import EnergyMinimizer, MinimizationError
from inspector.library.models.molecule import RESTMolecule


def expected_conformer_and_energy(molecule, conformer, omm_system):

    integrator = openmm.VerletIntegrator(0.002 * unit.picoseconds)

    simulation = app.Simulation(
        molecule.to_topology().to_openmm(),
        omm_system,
        integrator,
        openmm.Platform.getPlatformByName("Reference"),
    )

    simulation.context.setPositions(conformer)
    simulation.minimizeEnergy()

    state: openmm.State = simulation.context.getState(getPositions=True, getEnergy=True)

    return (
        state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole),
        state.getPositions(asNumpy=True).value_in_unit(unit.angstrom),
    )


def test_evaluate_energy_and_force(z_propenal):

    force_field = ForceField("openff_unconstrained-1.2.0.offxml")
    omm_system = force_field.create_openmm_system(z_propenal.to_topology())

    energy, force = EnergyMinimizer._evaluate_energy_and_force(
        z_propenal.conformers[0].value_in_unit(unit.nanometers), omm_system
    )

    assert not numpy.isnan(energy)
    assert not numpy.any(numpy.isnan(force))

    assert numpy.isclose(energy, 6.526425302550168)
    assert force.shape == (z_propenal.n_atoms * 3,)


@pytest.mark.parametrize("as_rest_molecule", [False, True])
def test_minimize(as_rest_molecule, z_propenal):

    conformer = z_propenal.conformers[0]
    z_propenal._conformers = [conformer]

    molecule = RESTMolecule.from_openff(z_propenal)
    off_molecule = molecule.to_openff()

    if not as_rest_molecule:
        molecule = off_molecule

    force_field = ForceField("openff-1.2.0.offxml")

    trajectory = EnergyMinimizer.minimize(
        molecule, conformer, force_field, method="L-BFGS-B"
    )

    actual_conformer = numpy.array(trajectory.frames[-1].geometry).reshape(9, 3)
    actual_energy = trajectory.frames[-1].potential_energy

    force_field = ForceField("openff_unconstrained-1.2.0.offxml")

    expected_energy, expected_conformer = expected_conformer_and_energy(
        off_molecule,
        conformer,
        force_field.create_openmm_system(off_molecule.to_topology()),
    )

    assert numpy.allclose(actual_conformer, expected_conformer, atol=1e-3)
    assert numpy.isclose(actual_energy, expected_energy)


def test_minimizer_failed(z_propenal, monkeypatch):
    def minimize(*args, **kwargs):
        return OptimizeResult(success=False, message="Failed")

    monkeypatch.setattr(optimize, "minimize", minimize)

    with pytest.raises(MinimizationError, match="Failed"):

        EnergyMinimizer.minimize(
            z_propenal, z_propenal.conformers[0], ForceField(), method="L-BFGS-B"
        )
