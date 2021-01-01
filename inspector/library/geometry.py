import copy
from typing import Union

import mdtraj
import numpy
from openforcefield.topology import Molecule
from simtk import unit

from inspector.library.models.geometry import GeometrySummary
from inspector.library.models.molecule import RESTMolecule


def summarize_geometry(
    molecule: Union[Molecule, RESTMolecule], conformer: unit.Quantity
) -> GeometrySummary:

    molecule = copy.deepcopy(molecule)

    if isinstance(molecule, Molecule):
        molecule._conformers = [conformer]
    elif isinstance(molecule, RESTMolecule):
        molecule = molecule.to_openff()

    topology = mdtraj.Topology.from_openmm(molecule.to_topology().to_openmm())

    trajectory = mdtraj.Trajectory(
        xyz=conformer.value_in_unit(unit.nanometers)[numpy.newaxis, :, :],
        topology=topology,
    )

    # Summarise the bonds
    bond_indices = [(bond.atom1_index, bond.atom2_index) for bond in molecule.bonds]
    bond_lengths = (
        mdtraj.compute_distances(trajectory, numpy.array(bond_indices), periodic=False)[
            0, :
        ]
        * 10.0
    )

    # Summarise the angles
    angle_indices = [
        tuple(angle[i].molecule_atom_index for i in range(3))
        for angle in molecule.angles
    ]
    bond_angles = (
        mdtraj.compute_angles(trajectory, numpy.array(angle_indices), periodic=False)[
            0, :
        ]
        / numpy.pi
        * 180.0
    )

    # Summarise the proper torsions
    torsion_indices = [
        tuple(torsion[i].molecule_atom_index for i in range(4))
        for torsion in molecule.propers
    ]

    proper_dihedral_angles = (
        mdtraj.compute_dihedrals(
            trajectory, numpy.array(torsion_indices), periodic=False
        )[0, :]
        / numpy.pi
        * 180.0
    )

    # Summaries any hydrogen bonds.
    hydrogen_bond_indices = mdtraj.wernet_nilsson(trajectory)

    # noinspection PyTypeChecker
    summary = GeometrySummary(
        bond_lengths=[(*i, length) for i, length in zip(bond_indices, bond_lengths)],
        bond_angles=[(*i, angle) for i, angle in zip(angle_indices, bond_angles)],
        proper_dihedral_angles=[
            (*i, angle) for i, angle in zip(torsion_indices, proper_dihedral_angles)
        ],
        hydrogen_bonds=[tuple(*i) for i in hydrogen_bond_indices if len(i) > 0],
    )

    return summary
