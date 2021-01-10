import abc
from typing import List, Literal, Optional, TypeVar, Union

from openforcefield.typing.engines.smirnoff.parameters import (
    AngleHandler,
    BondHandler,
    ChargeIncrementModelHandler,
    ConstraintHandler,
    ImproperTorsionHandler,
    LibraryChargeHandler,
    ProperTorsionHandler,
    vdWHandler,
)
from pydantic import BaseModel, Field, conlist, validator
from simtk import unit

T = TypeVar("T", bound="_ParameterType")


class _ParameterType(BaseModel, abc.ABC):
    """The base class for force field parameters."""

    smirks: str = Field(
        ...,
        description="The SMIRKS pattern describing the chemical environment that the "
        "parameter should be applied to.",
    )
    id: str = Field(..., description="The id assigned to the parameter.")


class ConstraintType(_ParameterType):
    """A pydantic representation of a SMIRNOFF constraint type."""

    type: Literal["ConstraintType"] = "ConstraintType"

    distance: Optional[float] = Field(..., description="The constraint distance [Å].")

    @classmethod
    def from_openff(
        cls, parameter: ConstraintHandler.ConstraintType
    ) -> "ConstraintType":
        """Creates an instance of the model from the corresponding OpenFF model."""

        return cls(
            smirks=parameter.smirks,
            id=parameter.id,
            distance=None
            if parameter.distance is None
            else parameter.distance.value_in_unit(unit.angstrom),
        )

    def to_openff(self) -> ConstraintHandler.ConstraintType:
        """Create an corresponding OpenFF instance of this model."""

        return ConstraintHandler.ConstraintType(
            smirks=self.smirks,
            id=self.id,
            distance=None if self.distance is None else self.distance * unit.angstrom,
        )


class BondType(_ParameterType):
    """A pydantic representation of a SMIRNOFF bond type."""

    type: Literal["BondType"] = "BondType"

    length: float = Field(..., description="The bond length [Å].")
    k: float = Field(..., description="The spring constant [kcal / mol / Å**2].")

    @classmethod
    def from_openff(cls, parameter: BondHandler.BondType) -> "BondType":
        """Creates an instance of the model from the corresponding OpenFF model."""

        return cls(
            smirks=parameter.smirks,
            id=parameter.id,
            length=parameter.length.value_in_unit(unit.angstrom),
            k=parameter.k.value_in_unit(
                unit.kilocalories_per_mole / unit.angstrom ** 2
            ),
        )

    def to_openff(self) -> BondHandler.BondType:
        """Create an corresponding OpenFF instance of this model."""

        return BondHandler.BondType(
            smirks=self.smirks,
            id=self.id,
            length=self.length * unit.angstrom,
            k=self.k * unit.kilocalories_per_mole / unit.angstrom ** 2,
        )


class AngleType(_ParameterType):
    """A pydantic representation of a SMIRNOFF angle type."""

    type: Literal["AngleType"] = "AngleType"

    angle: float = Field(..., description="The equilibrium bond angle [deg]")
    k: float = Field(..., description="The spring constant [kcal / mol / deg**2]")

    @classmethod
    def from_openff(cls, parameter: AngleHandler.AngleType) -> "AngleType":
        """Creates an instance of the model from the corresponding OpenFF model."""

        return cls(
            smirks=parameter.smirks,
            id=parameter.id,
            angle=parameter.angle.value_in_unit(unit.degrees),
            k=parameter.k.value_in_unit(unit.kilocalories_per_mole / unit.degrees ** 2),
        )

    def to_openff(self) -> AngleHandler.AngleType:
        """Create an corresponding OpenFF instance of this model."""

        return AngleHandler.AngleType(
            smirks=self.smirks,
            id=self.id,
            angle=self.angle * unit.degrees,
            k=self.k * unit.kilocalories_per_mole / unit.degrees ** 2,
        )


class _TorsionType(_ParameterType, abc.ABC):
    """A base class for pydantic representation of SMIRNOFF torsion types."""

    periodicity: conlist(int, min_items=1) = Field(
        ..., description="The periodicity of each torsion term."
    )
    phase: conlist(float, min_items=1) = Field(
        ..., description="The phase of each torsion term [deg]."
    )
    k: conlist(float, min_items=1) = Field(
        ..., description="The barrier height of each torsion term [kcal / mol]."
    )
    idivf: Optional[List[float]] = Field(
        ..., description="The `idivf` value of each torsion term."
    )

    @validator("phase", "k", "idivf")
    def _validate_lengths(cls, v, values):

        assert v is None or len(v) == len(
            values["periodicity"]
        ), "`periodicity`, `phase`, `k`, and `idivf` must be lists of the same length."

        return v

    @classmethod
    @abc.abstractmethod
    def _openff_parameter_class(cls):
        """The OpenFF parameter class associated with this model."""

    @classmethod
    def from_openff(cls: T, parameter) -> T:
        """Creates an instance of the model from the corresponding OpenFF model."""

        return cls(
            smirks=parameter.smirks,
            id=parameter.id,
            periodicity=[*parameter.periodicity],
            phase=[x.value_in_unit(unit.degrees) for x in parameter.phase],
            k=[x.value_in_unit(unit.kilocalories_per_mole) for x in parameter.k],
            idivf=None if parameter.idivf is None else [*parameter.idivf],
        )

    def to_openff(self):
        """Create an corresponding OpenFF instance of this model."""

        return self._openff_parameter_class()(
            smirks=self.smirks,
            id=self.id,
            periodicity=[*self.periodicity],
            phase=[x * unit.degrees for x in self.phase],
            k=[x * unit.kilocalories_per_mole for x in self.k],
            idivf=None if self.idivf is None else [*self.idivf],
        )


class ProperTorsionType(_TorsionType):
    """A pydantic representation of a SMIRNOFF torsion type for proper torsions."""

    type: Literal["ProperTorsionType"] = "ProperTorsionType"

    # k_bondorder: List[Dict[str, float]] = Field(
    #     [], description="The fractional bond order parameters [kcal / mol]."
    # )

    @classmethod
    def _openff_parameter_class(cls):
        return ProperTorsionHandler.ProperTorsionType

    @classmethod
    def from_openff(
        cls, parameter: ProperTorsionHandler.ProperTorsionType
    ) -> "ProperTorsionType":
        return super(ProperTorsionType, cls).from_openff(parameter)

    def to_openff(self) -> ProperTorsionHandler.ProperTorsionType:
        return super(ProperTorsionType, self).to_openff()


class ImproperTorsionType(_TorsionType):
    """A pydantic representation of a SMIRNOFF torsion type for improper torsions."""

    type: Literal["ImproperTorsionType"] = "ImproperTorsionType"

    @classmethod
    def _openff_parameter_class(cls):
        return ImproperTorsionHandler.ImproperTorsionType

    @classmethod
    def from_openff(
        cls, parameter: ImproperTorsionHandler.ImproperTorsionType
    ) -> "ImproperTorsionType":
        return super(ImproperTorsionType, cls).from_openff(parameter)

    def to_openff(self) -> ImproperTorsionHandler.ImproperTorsionType:
        return super(ImproperTorsionType, self).to_openff()


class vdWType(_ParameterType):
    """A pydantic representation of a SMIRNOFF vdWForce type."""

    type: Literal["vdWType"] = "vdWType"

    epsilon: float = Field(..., description="The epsilon parameter [kcal / mol].")
    sigma: float = Field(..., description="The sigma parameter [Å].")

    @classmethod
    def from_openff(cls, parameter: vdWHandler.vdWType) -> "vdWType":
        """Creates an instance of the model from the corresponding OpenFF model."""

        return cls(
            smirks=parameter.smirks,
            id=parameter.id,
            epsilon=parameter.epsilon.value_in_unit(unit.kilocalories_per_mole),
            sigma=parameter.sigma.value_in_unit(unit.angstrom),
        )

    def to_openff(self) -> vdWHandler.vdWType:
        """Create an corresponding OpenFF instance of this model."""

        return vdWHandler.vdWType(
            smirks=self.smirks,
            id=self.id,
            epsilon=self.epsilon * unit.kilocalories_per_mole,
            sigma=self.sigma * unit.angstrom,
        )


class LibraryChargeType(_ParameterType):
    """A pydantic representation of a SMIRNOFF Library Charge type."""

    type: Literal["LibraryChargeType"] = "LibraryChargeType"

    charge: conlist(float, min_items=1) = Field(
        ..., description="The charge of each tagged atom [e]."
    )

    @classmethod
    def from_openff(
        cls, parameter: LibraryChargeHandler.LibraryChargeType
    ) -> "LibraryChargeType":
        """Creates an instance of the model from the corresponding OpenFF model."""

        return cls(
            smirks=parameter.smirks,
            id=parameter.id,
            charge=[x.value_in_unit(unit.elementary_charge) for x in parameter.charge],
        )

    def to_openff(self) -> LibraryChargeHandler.LibraryChargeType:
        """Create an corresponding OpenFF instance of this model."""

        return LibraryChargeHandler.LibraryChargeType(
            smirks=self.smirks,
            id=self.id,
            charge=[x * unit.elementary_charge for x in self.charge],
        )


class ChargeIncrementType(_ParameterType):
    """A pydantic representation of a SMIRNOFF bond charge correction type."""

    type: Literal["ChargeIncrementType"] = "ChargeIncrementType"

    charge_increment: conlist(float, min_items=1) = Field(
        ..., description="The charge increment to apply to each tagged atom [e]."
    )

    @classmethod
    def from_openff(
        cls, parameter: ChargeIncrementModelHandler.ChargeIncrementType
    ) -> "ChargeIncrementType":
        """Creates an instance of the model from the corresponding OpenFF model."""

        return cls(
            smirks=parameter.smirks,
            id=parameter.id,
            charge_increment=[
                x.value_in_unit(unit.elementary_charge)
                for x in parameter.charge_increment
            ],
        )

    def to_openff(self) -> ChargeIncrementModelHandler.ChargeIncrementType:
        """Create an corresponding OpenFF instance of this model."""

        return ChargeIncrementModelHandler.ChargeIncrementType(
            smirks=self.smirks,
            id=self.id,
            charge_increment=[
                x * unit.elementary_charge for x in self.charge_increment
            ],
        )


SMIRNOFFParameterType = Union[
    ConstraintType,
    BondType,
    AngleType,
    ProperTorsionType,
    ImproperTorsionType,
    vdWType,
    LibraryChargeType,
    ChargeIncrementType,
]
