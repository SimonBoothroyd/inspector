from random import randint, random

import pytest
from pydantic import ValidationError

from inspector.library.models.smirnoff import (
    AngleType,
    BondType,
    ChargeIncrementType,
    ConstraintType,
    ImproperTorsionType,
    LibraryChargeType,
    ProperTorsionType,
    vdWType,
)
from inspector.tests import compare_pydantic_models


def default_kwargs(n_atoms: int):
    return {"smirks": "-".join([f"[#6X1:{i + 1}]" for i in range(n_atoms)]), "id": "p1"}


@pytest.mark.parametrize(
    "original_parameter",
    [
        ConstraintType(**default_kwargs(2), distance=random()),
        ConstraintType(**default_kwargs(2), distance=None),
        BondType(**default_kwargs(2), length=random(), k=random()),
        AngleType(**default_kwargs(3), angle=random(), k=random()),
        ProperTorsionType(
            **default_kwargs(4),
            periodicity=[randint(0, 10), randint(0, 10)],
            phase=[random(), random()],
            k=[random(), random()],
            idivf=[random(), random()],
        ),
        ProperTorsionType(
            **default_kwargs(4),
            periodicity=[randint(0, 10), randint(0, 10)],
            phase=[random(), random()],
            k=[random(), random()],
            idivf=None,
        ),
        ImproperTorsionType(
            **default_kwargs(4),
            periodicity=[randint(0, 10), randint(0, 10)],
            phase=[random(), random()],
            k=[random(), random()],
            idivf=[random(), random()],
        ),
        ImproperTorsionType(
            **default_kwargs(4),
            periodicity=[randint(0, 10), randint(0, 10)],
            phase=[random(), random()],
            k=[random(), random()],
            idivf=None,
        ),
        vdWType(**default_kwargs(1), epsilon=random(), sigma=random()),
        LibraryChargeType(**default_kwargs(2), charge=[random(), random()]),
        ChargeIncrementType(**default_kwargs(2), charge_increment=[random(), random()]),
    ],
)
def test_smirnoff_round_trip(
    original_parameter,
):

    parameter_class = type(original_parameter)
    round_tripped = parameter_class.from_openff(original_parameter.to_openff())

    compare_pydantic_models(original_parameter, round_tripped)


def test_validate_torsion_lengths():

    with pytest.raises(ValidationError) as error_info:

        ProperTorsionType(
            **default_kwargs(4),
            periodicity=[1],
            phase=[0.0, 0.0],
            k=[0.0],
            idivf=[0.0, 0.0, 0.0],
        )

    assert (
        "`periodicity`, `phase`, `k`, and `idivf` must be lists of the same length"
        in str(error_info.value)
    )
