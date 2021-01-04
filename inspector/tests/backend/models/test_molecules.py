import pytest
from pydantic import ValidationError

from inspector.backend.models.molecules import ApplyParametersBody
from inspector.library.models.molecule import RESTMolecule


def test_apply_parameters_body_validate(methane):

    molecule = RESTMolecule.from_openff(methane)

    # Mutually exclusive init
    ApplyParametersBody(molecule=molecule, smirnoff_xml="", openff_name=None)
    ApplyParametersBody(molecule=molecule, smirnoff_xml=None, openff_name="")

    with pytest.raises(ValidationError) as error_info:
        ApplyParametersBody(molecule=molecule, smirnoff_xml="", openff_name="")

    assert "exactly one of" in str(error_info.value)

    with pytest.raises(ValidationError) as error_info:
        ApplyParametersBody(molecule=molecule, smirnoff_xml=None, openff_name=None)

    assert "exactly one of" in str(error_info.value)
