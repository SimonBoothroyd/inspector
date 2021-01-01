import numpy
import pytest
from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField
from simtk import unit


@pytest.fixture()
def methane() -> Molecule:

    molecule: Molecule = Molecule.from_smiles("C")
    molecule.add_conformer(
        numpy.array(
            [
                [-0.0000658, -0.0000061, 0.0000215],
                [-0.0566733, 1.0873573, -0.0859463],
                [0.6194599, -0.3971111, -0.8071615],
                [-1.0042799, -0.4236047, -0.0695677],
                [0.4415590, -0.2666354, 0.9626540],
            ]
        )
        * unit.angstrom
    )

    return molecule


@pytest.fixture()
def z_propenal() -> Molecule:

    molecule = Molecule()

    molecule.add_atom(6, 0, False)
    molecule.add_atom(6, 0, False)
    molecule.add_atom(8, 0, False)
    molecule.add_atom(6, 0, False)
    molecule.add_atom(8, 0, False)
    molecule.add_atom(1, 0, False)
    molecule.add_atom(1, 0, False)
    molecule.add_atom(1, 0, False)
    molecule.add_atom(1, 0, False)

    molecule.add_bond(0, 1, 2, False)
    molecule.add_bond(1, 2, 1, False)
    molecule.add_bond(0, 3, 1, False)
    molecule.add_bond(3, 4, 2, False)
    molecule.add_bond(0, 5, 1, False)
    molecule.add_bond(1, 6, 1, False)
    molecule.add_bond(2, 7, 1, False)
    molecule.add_bond(3, 8, 1, False)

    molecule.add_conformer(
        # Add a conformer with an internal H-bond.
        numpy.array(
            [
                [0.5477, 0.3297, -0.0621],
                [-0.1168, -0.7881, 0.2329],
                [-1.4803, -0.8771, 0.1667],
                [-0.2158, 1.5206, -0.4772],
                [-1.4382, 1.5111, -0.5580],
                [1.6274, 0.3962, -0.0089],
                [0.3388, -1.7170, 0.5467],
                [-1.8612, -0.0347, -0.1160],
                [0.3747, 2.4222, -0.7115],
            ]
        )
        * unit.angstrom
    )
    molecule.add_conformer(
        # Add a conformer without an internal H-bond.
        numpy.array(
            [
                [0.5477, 0.3297, -0.0621],
                [-0.1168, -0.7881, 0.2329],
                [-1.4803, -0.8771, 0.1667],
                [-0.2158, 1.5206, -0.4772],
                [0.3353, 2.5772, -0.7614],
                [1.6274, 0.3962, -0.0089],
                [0.3388, -1.7170, 0.5467],
                [-1.7743, -1.7634, 0.4166],
                [-1.3122, 1.4082, -0.5180],
            ]
        )
        * unit.angstrom
    )

    return molecule


@pytest.fixture()
def openff_1_0_0() -> ForceField:
    return ForceField("openff-1.0.0.offxml")
