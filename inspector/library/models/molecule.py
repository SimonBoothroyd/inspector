from typing import Literal, Optional, Tuple, TypeVar

import numpy
from openforcefield.topology import Molecule
from pydantic import BaseModel, Field, conlist, constr, validator
from simtk import unit

T = TypeVar("T", bound="RESTMolecule")

AtomicSymbol = Literal["C", "O", "H", "N", "S", "F", "Br", "Cl", "I", "P"]

SEMVER_REGEX = (
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)(?:-"
    r"(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+"
    r"(?:\.[0-9a-zA-Z-]+)*))?$"
)

REST_MOLECULE_SCHEMA_VERSION = "0.0.1-alpha.1"


class InvalidMoleculeError(ValueError):
    """An exception raised when an invalid molecule was passed to a function"""

    def __init__(self, reason: Optional[str] = None):

        super(InvalidMoleculeError, self).__init__(
            "The specified molecule was invalid"
            + ("." if reason is None else f": {reason}")
        )


class RESTMolecule(BaseModel):
    """A compact, minimal representation of a molecule which can be served from or
    received by the RESTful API.
    """

    schema_version: constr(regex=SEMVER_REGEX) = Field(
        REST_MOLECULE_SCHEMA_VERSION, description="The version of this model's schema."
    )

    symbols: conlist(AtomicSymbol, min_items=1) = Field(
        ...,
        description="An ordered list of the atomic symbols of each atom in the molecule "
        "with length=n_atoms.",
    )
    connectivity: conlist(Tuple[int, int, int], min_items=1) = Field(
        None,
        description="The connectivity between each atom in the ``symbols`` list. Each "
        "item must be a tuple of the form ``(atom_index_a, atom_index_b, bond_order)``.",
    )

    geometry: conlist(float, min_items=1) = Field(
        ...,
        description="A flattened array of the molecules XYZ atomic coordinates [Å] "
        "with length=n_atoms*3 which can be reshaped to array with shape=(n_atoms, 3)."
        "\n"
        "The ordering of the coordinates must match the ordering of the ``symbols`` "
        "and ``connectivity`` lists.",
    )

    @validator("connectivity")
    def _validate_connectivity(cls, v, values):

        n_atoms = len(values["symbols"])

        assert all(
            0 <= index_a < n_atoms and 0 <= index_b < n_atoms
            for index_a, index_b, _ in v
        ), "atom index out of range."

        return v

    @validator("geometry")
    def _validate_geometry(cls, v, values):

        assert len(v) % 3 == 0, "geometry length not divisible by three."
        assert len(v) / 3 == len(values["symbols"]), "incorrect geometry length."

        return v

    @classmethod
    def from_openff(cls: "RESTMolecule", molecule: Molecule) -> "RESTMolecule":

        if molecule.n_conformers != 1:

            raise InvalidMoleculeError(
                f"The OpenFF molecule must contain exactly one conformer "
                f"({molecule.n_conformers} found)."
            )

        return cls(
            symbols=[atom.element.symbol for atom in molecule.atoms],
            connectivity=[
                (bond.atom1_index, bond.atom2_index, bond.bond_order)
                for bond in molecule.bonds
            ],
            geometry=[*molecule.conformers[0].value_in_unit(unit.angstrom).flatten()],
        )

    def to_openff(self) -> Molecule:

        from rdkit import Chem
        from rdkit.Chem import rdmolops
        from rdkit.Geometry.rdGeometry import Point3D

        geometry = numpy.array(self.geometry).reshape(int(len(self.geometry) / 3), 3)
        conformer = Chem.Conformer(len(self.symbols))

        # noinspection PyArgumentList
        rdkit_rw_molecule = Chem.RWMol(Chem.Mol())

        # Add the atoms and set the conformer coordinates.
        for i, symbol in enumerate(self.symbols):

            atom = rdkit_rw_molecule.AddAtom(Chem.Atom(symbol))

            conformer.SetAtomPosition(
                atom, Point3D(geometry[i][0], geometry[i][1], geometry[i][2])
            )

        # Add the bond connectivity.
        for index_a, index_b, bond_order in self.connectivity:

            bond_type = {
                1: Chem.BondType.SINGLE,
                2: Chem.BondType.DOUBLE,
                3: Chem.BondType.TRIPLE,
            }[bond_order]

            rdkit_rw_molecule.AddBond(index_a, index_b, bond_type)

        # noinspection PyArgumentList
        rdkit_molecule = rdkit_rw_molecule.GetMol()
        Chem.SanitizeMol(rdkit_molecule)

        # Add the coordinates to the molecule and assign stereochemistry.
        conformer_id = rdkit_molecule.AddConformer(conformer, assignId=True)
        rdmolops.AssignStereochemistryFrom3D(
            rdkit_molecule, confId=conformer_id, replaceExistingTags=True
        )

        molecule = Molecule.from_rdkit(rdkit_molecule)
        return molecule
