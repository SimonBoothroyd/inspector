import abc
import copy
import functools
from typing import List, Literal, Optional, Tuple, Union

import numpy
from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField
from scipy import optimize
from simtk import openmm, unit

from inspector.library.models.minimization import (
    MinimizationFrame,
    MinimizationTrajectory,
)
from inspector.library.models.molecule import RESTMolecule


class MinimizationError(ValueError):
    """An exception raised when the energy minimizer fails to successfully run."""


class EnergyMinimizer(abc.ABC):
    """A class which provides methods for performing energy minimization on the conformer
    of a molecule."""

    @staticmethod
    def _evaluate_energy_and_force(
        conformer: numpy.ndarray, system: openmm.System
    ) -> Tuple[float, numpy.ndarray]:
        """Evaluates the energy and it's gradient with respect to coordinates (i.e.
        -F(x)) of a given conformer.

        Args:
            conformer: The conformer with shape=(n_atoms, 3) and units of nm.
            system: The system which encodes the potential energy function.
        """
        integrator = openmm.VerletIntegrator(0.001 * unit.femtoseconds)

        platform = openmm.Platform.getPlatformByName("Reference")
        openmm_context = openmm.Context(system, integrator, platform)

        openmm_context.setPositions(conformer.reshape(system.getNumParticles(), 3))

        state = openmm_context.getState(getEnergy=True, getForces=True)

        return (
            state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole),
            -state.getForces(asNumpy=True)
            .value_in_unit(unit.kilojoules_per_mole / unit.nanometer)
            .flatten(),
        )

    @staticmethod
    def minimize(
        molecule: Union[Molecule, RESTMolecule],
        conformer: unit.Quantity,
        force_field: ForceField,
        method: Literal["L-BFGS-B"] = "L-BFGS-B",
        energy_tolerance: Optional[float] = None,
    ) -> MinimizationTrajectory:
        """Performs energy minimization of a specified conformer of a molecule.

        Args:
            molecule: The definition of the molecule to minimize.
            conformer: The conformer to minimize with shape=(n_atoms, 3) and units
                compatible with nm.
            force_field: The force field which defines the potential energy function.
            method: The minimization algorithm to use.
            energy_tolerance: The target tolerance to converge the energy within-in
                [kJ / mol]

        Returns:
            The trajectory of each iteration of the minimization, including both the
            conformer and energy at each iteration.
        """

        molecule = copy.deepcopy(molecule)

        if isinstance(molecule, RESTMolecule):
            molecule = molecule.to_openff()

        if len(force_field.get_parameter_handler("Constraints").parameters) > 0:
            force_field.deregister_parameter_handler("Constraints")

        # Apply the force field to the molecule.
        omm_system = force_field.create_openmm_system(molecule.to_topology())

        # Create an array to store each frame in and a callback function
        # to create and store the frame.
        frames: List[MinimizationFrame] = []

        def callback(current_conformer: numpy.ndarray):

            energy = EnergyMinimizer._evaluate_energy_and_force(
                current_conformer, omm_system
            )[0]

            frames.append(
                MinimizationFrame(
                    geometry=[*(current_conformer * 10.0)], potential_energy=energy
                )
            )

            return numpy.isnan(energy)

        result = optimize.minimize(
            functools.partial(
                EnergyMinimizer._evaluate_energy_and_force, system=omm_system
            ),
            conformer.value_in_unit(unit.nanometer),
            method=method,
            jac=True,
            callback=callback,
            tol=energy_tolerance,
        )

        if not result.success:
            raise MinimizationError(result.message)

        return MinimizationTrajectory(frames=frames)
