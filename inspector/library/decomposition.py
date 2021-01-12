import logging
from collections import defaultdict
from typing import Dict, List, Tuple, Union

import numpy
from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField, ParameterHandler
from simtk import unit
from simtk.openmm import copy, openmm

from inspector.library.forcefield import label_molecule
from inspector.library.models.energy import DecomposedEnergy
from inspector.library.models.molecule import RESTMolecule
from inspector.library.models.smirnoff import SMIRNOFFParameterType

logger = logging.getLogger(__name__)

_SUPPORTED_VALENCE_TAGS = [
    "Bonds",
    "Angles",
    "ProperTorsions",
    "ImproperTorsions",
]


def _get_openmm_parameters(
    force: openmm.Force,
) -> Dict[Tuple[int, ...], List[Tuple[unit.Quantity, ...]]]:
    """Returns the parameters stored in a given force.

    Args:
        force: The force to retrieve the parameters from.

    Returns:
        A dictionary of the retrieved parameters where each key is a tuple of atom
        indices, and each value is a list of the parameter sets associated with those
        atom indices.
    """

    omm_parameters = defaultdict(list)

    if isinstance(force, openmm.HarmonicBondForce):

        for i in range(force.getNumBonds()):
            index_a, index_b, *parameters = force.getBondParameters(i)
            omm_parameters[(index_a, index_b)].append(parameters)

        assert sum(len(x) for x in omm_parameters.values()) == force.getNumBonds()

    elif isinstance(force, openmm.HarmonicAngleForce):

        for i in range(force.getNumAngles()):
            index_a, index_b, index_c, *parameters = force.getAngleParameters(i)
            omm_parameters[(index_a, index_b, index_c)].append(parameters)

        assert sum(len(x) for x in omm_parameters.values()) == force.getNumAngles()

    elif isinstance(force, openmm.PeriodicTorsionForce):

        for i in range(force.getNumTorsions()):

            (
                index_a,
                index_b,
                index_c,
                index_d,
                *parameters,
            ) = force.getTorsionParameters(i)
            omm_parameters[(index_a, index_b, index_c, index_d)].append(parameters)

        assert sum(len(x) for x in omm_parameters.values()) == force.getNumTorsions()

    else:
        raise NotImplementedError

    return omm_parameters


def _add_openmm_parameter(
    force: openmm.Force,
    atom_indices: Tuple[int, ...],
    parameters: Tuple[unit.Quantity, ...],
):
    """A convenience method to add a set of parameters to a force.

    Args:
        force: The force to add the parameters to.
        atom_indices: The atom indices the parameters apply to.
        parameters: The parameters to add.
    """

    if isinstance(force, openmm.HarmonicBondForce):
        force.addBond(*atom_indices, *parameters)

    elif isinstance(force, openmm.HarmonicAngleForce):
        force.addAngle(*atom_indices, *parameters)

    elif isinstance(force, openmm.PeriodicTorsionForce):
        force.addTorsion(*atom_indices, *parameters)

    else:
        raise NotImplementedError


def group_force_by_parameter_id(
    handler_force: openmm.Force,
    parameters: List[SMIRNOFFParameterType],
    parameter_map: Dict[str, List[Tuple[int, ...]]],
) -> Dict[str, openmm.Force]:
    """Partitions the parameters in a force into a separate force for each parameter
    id.

    Args:
        handler_force: The force containing the parameters to partition.
        parameters: The original SMIRNOFF parameters used to populate the
            ``handler_force``.
        parameter_map: A mapping between each parameter id and the atom indices the
            parameter was applied to.

    Returns:
        A dictionary of parameter ids and the associated force.
    """

    grouped_forces = {}
    grouped_counter = 0

    # Store the force parameters in a dictionary partitioned by atom indices
    omm_parameters = _get_openmm_parameters(handler_force)

    # Copy each term in the force over to the correct force group
    for parameter in parameters:

        grouped_force = handler_force.__class__()
        grouped_forces[parameter.id] = grouped_force

        for mapped_atom_indices in parameter_map[parameter.id]:

            # Improper torsions are a special case due to the trefoil enumeration.
            if parameter.type == "ImproperTorsionType":

                others = [
                    mapped_atom_indices[0],
                    mapped_atom_indices[2],
                    mapped_atom_indices[3],
                ]

                enumerated_atom_indices = [
                    (mapped_atom_indices[1], p[0], p[1], p[2])
                    for p in [
                        (others[i], others[j], others[k])
                        for (i, j, k) in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
                    ]
                ]

            else:
                enumerated_atom_indices = [mapped_atom_indices]

            for atom_indices in enumerated_atom_indices:

                for omm_parameter in omm_parameters[atom_indices]:

                    _add_openmm_parameter(grouped_force, atom_indices, omm_parameter)

                    grouped_counter += 1

    return grouped_forces


def group_forces_by_parameter_id(
    molecule: Molecule, force_field: ForceField
) -> Tuple[openmm.System, Dict[str, Dict[str, int]]]:
    """Applies a particular force field to a specified molecule creating an OpenMM
    system object where each valence parameter (as identified by it's unique id)
    is separated into a different force group.

    Notes:
        * All nonbonded forces will be assigned to force group 0.

    Args:
        molecule: The molecule to apply thr force field to.
        force_field: The force field to apply.

    Returns:
        A tuple of the created OpenMM system, and a dictionary of the form
        ``force_groups[HANDLER_TAG][PARAMETER_ID] = FORCE_GROUP_INDEX``.
    """

    # Label the molecule with the parameters which will be assigned so we can access
    # which 'slot' is filled by which parameter. This allows us to carefully split the
    # potential energy terms into different force groups.
    applied_parameters = label_molecule(molecule, force_field)

    # Create an OpenMM system which will not have force groups yet.
    omm_system: openmm.System = force_field.create_openmm_system(molecule.to_topology())

    # Create a new OpenMM system to store the grouped forces in and copy over the
    # nonbonded forces.
    grouped_omm_system = openmm.System()
    matched_forces = set()

    for i in range(omm_system.getNumParticles()):
        grouped_omm_system.addParticle(omm_system.getParticleMass(i))

    nonbonded_forces = [
        (i, force)
        for i, force in enumerate(omm_system.getForces())
        if isinstance(force, openmm.NonbondedForce)
    ]
    assert (
        len(nonbonded_forces) == 1
    ), "expected only one instance of a NonbondedForce force."

    grouped_omm_system.addForce(copy.deepcopy(nonbonded_forces[0][1]))
    matched_forces.add(nonbonded_forces[0][0])

    # Split the potential energy terms into per-parameter-type force groups.
    force_group_indices = defaultdict(dict)  # force_groups[HANDLER][PARAM_ID] = INDEX
    force_group_counter = 1

    for handler_type in applied_parameters.parameters:

        if handler_type not in _SUPPORTED_VALENCE_TAGS:
            continue

        handler: ParameterHandler = force_field.get_parameter_handler(handler_type)
        omm_force_type = handler._OPENMMTYPE

        # Find the force associated with this handler.
        handler_forces = [
            (i, force)
            for i, force in enumerate(omm_system.getForces())
            if isinstance(force, omm_force_type)
        ]
        assert (
            len(handler_forces) == 1
        ), f"expected only one instance of a {omm_force_type.__name__} force."

        force_index, handler_force = handler_forces[0]
        matched_forces.add(force_index)

        # Group the force into force per parameter id.
        grouped_forces = group_force_by_parameter_id(
            handler_force,
            applied_parameters.parameters[handler_type],
            applied_parameters.parameter_map,
        )

        for parameter_id, grouped_force in grouped_forces.items():

            force_group = force_group_counter

            grouped_force.setForceGroup(force_group)
            grouped_omm_system.addForce(grouped_force)

            force_group_indices[handler_type][parameter_id] = force_group
            force_group_counter += 1

    return grouped_omm_system, force_group_indices


def evaluate_energy(
    omm_system: openmm.System, conformer: unit.Quantity
) -> Tuple[unit.Quantity, Dict[int, unit.Quantity]]:
    """Computes both the total potential energy, and potential energy per force group,
    of a given conformer.

    Args:
        omm_system: The system encoding the potential energy function.
        conformer: The conformer to compute the energy of.

    Returns
        A tuple of the total potential energy, and a dictionary of the potential energy
        per force group.
    """

    integrator = openmm.VerletIntegrator(0.001 * unit.femtoseconds)
    platform = openmm.Platform.getPlatformByName("Reference")

    openmm_context = openmm.Context(omm_system, integrator, platform)
    openmm_context.setPositions(conformer.value_in_unit(unit.nanometers))

    energy_per_force_id = {}

    for force in omm_system.getForces():

        state = openmm_context.getState(
            getEnergy=True, groups=1 << force.getForceGroup()
        )
        energy_per_force_id[force.getForceGroup()] = state.getPotentialEnergy()

    state = openmm_context.getState(getEnergy=True)
    total_energy = state.getPotentialEnergy()

    return total_energy, energy_per_force_id


def evaluate_per_term_energies(
    molecule: Union[Molecule, RESTMolecule],
    conformer: unit.Quantity,
    force_field: ForceField,
) -> DecomposedEnergy:

    molecule = copy.deepcopy(molecule)
    force_field = copy.deepcopy(force_field)

    if isinstance(molecule, RESTMolecule):
        molecule = molecule.to_openff()

    # Remove constraints so we can access the bond energies.
    if len(force_field.get_parameter_handler("Constraints").parameters) > 0:

        logger.warning(
            "Constraints will be removed when evaluating the per term energy."
        )
        force_field.deregister_parameter_handler("Constraints")

    # Apply the force field to the molecule, making sure to add each parameter type into
    # a separate force group.
    omm_system, id_to_force_group = group_forces_by_parameter_id(molecule, force_field)

    # Evaluate the energy.
    total_energy, energy_per_force_id = evaluate_energy(omm_system, conformer)

    summed_energy = sum(
        x.value_in_unit(unit.kilojoules_per_mole) for x in energy_per_force_id.values()
    )

    assert numpy.isclose(
        total_energy.value_in_unit(unit.kilojoules_per_mole), summed_energy
    ), "the ungrouped and grouped energies do not match."

    # Decompose the contributions of the vdW and electrostatic interactions.
    nonbonded_energy = energy_per_force_id[0].value_in_unit(unit.kilojoules_per_mole)

    nonbonded_force = [
        force
        for force in omm_system.getForces()
        if isinstance(force, openmm.NonbondedForce)
    ][0]

    for i in range(nonbonded_force.getNumParticles()):
        _, sigma, epsilon = nonbonded_force.getParticleParameters(i)
        nonbonded_force.setParticleParameters(i, 0.0, sigma, epsilon)

    for i in range(nonbonded_force.getNumExceptions()):
        index_a, index_b, _, sigma, epsilon = nonbonded_force.getExceptionParameters(i)
        nonbonded_force.setExceptionParameters(i, index_a, index_b, 0.0, sigma, epsilon)

    _, no_charge_energies = evaluate_energy(omm_system, conformer)

    vdw_energy = no_charge_energies[0].value_in_unit(unit.kilojoules_per_mole)
    electrostatic_energy = nonbonded_energy - vdw_energy

    return DecomposedEnergy(
        valence_energies={
            handler_name: {
                parameter_id: energy_per_force_id[
                    id_to_force_group[handler_name][parameter_id]
                ].value_in_unit(unit.kilojoules_per_mole)
                for parameter_id in id_to_force_group[handler_name]
            }
            for handler_name in id_to_force_group
        },
        vdw_energy=vdw_energy,
        electrostatic_energy=electrostatic_energy,
    )
