import pytest
from pydantic import ValidationError

from inspector.library.models.minimization import MinimizationFrame


def test_geometry_validation():

    MinimizationFrame(geometry=[0.0] * 3, potential_energy=0.0)

    with pytest.raises(ValidationError) as error_info:
        MinimizationFrame(geometry=[0.0], potential_energy=0.0)

    assert "geometry length not divisible by three" in str(error_info.value)
