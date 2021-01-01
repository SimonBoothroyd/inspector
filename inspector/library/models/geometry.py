from typing import List, Tuple

from pydantic import BaseModel, Field, PositiveFloat, conint

AtomIndex = conint(ge=0)

BondLength = Tuple[AtomIndex, AtomIndex, PositiveFloat]

BondAngle = Tuple[AtomIndex, AtomIndex, AtomIndex, float]

DihedralAngle = Tuple[AtomIndex, AtomIndex, AtomIndex, AtomIndex, float]


class GeometrySummary(BaseModel):

    bond_lengths: List[BondLength] = Field(
        ...,
        description="A list of bond lengths [Å], stored as tuples of the form "
        "``(atom_index_a, atom_index_b, length)``.",
    )
    bond_angles: List[BondAngle] = Field(
        ...,
        description="A list of bond lengths [deg], stored as tuples of the form "
        "``(atom_index_a, atom_index_b, atom_index_c, angle)``.",
    )

    proper_dihedral_angles: List[DihedralAngle] = Field(
        ...,
        description="A list of proper dihedral angles [deg], stored as tuples of the "
        "form ``(atom_index_a, atom_index_b, atom_index_c, atom_index_d, angle)``.",
    )

    hydrogen_bonds: List[Tuple[AtomIndex, AtomIndex, AtomIndex]] = Field(
        ...,
        description="A list of atoms involved in hydrogen bonds stored as tuples of the "
        "form ``(donor_index, h_index, acceptor_index)``.",
    )
