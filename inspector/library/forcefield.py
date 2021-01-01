"""A module containing utilities for assigning force field parameters to molecules
"""
from collections import defaultdict
from typing import Union

from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField

from inspector.library.models import smirnoff as smirnoff_models
from inspector.library.models.forcefield import AppliedParameters
from inspector.library.models.molecule import RESTMolecule


def label_molecule(
    molecule: Union[Molecule, RESTMolecule], force_field: ForceField
) -> AppliedParameters:

    if isinstance(molecule, RESTMolecule):
        molecule = molecule.to_openff()

    off_parameters = force_field.label_molecules(molecule.to_topology())[0]

    parameter_map = defaultdict(list)
    unique_parameters = defaultdict(list)

    for handler_name, off_handler_parameters in off_parameters.items():

        unique_parameter_ids = set()

        for atom_indices, off_parameter in off_handler_parameters.items():

            if off_parameter.id not in unique_parameter_ids:

                model_class = getattr(smirnoff_models, off_parameter.__class__.__name__)
                model_parameter = model_class.from_openff(off_parameter)

                unique_parameter_ids.add(model_parameter.id)
                unique_parameters[handler_name].append(model_parameter)

            parameter_map[off_parameter.id].append(atom_indices)

    return AppliedParameters(
        parameters=unique_parameters,
        parameter_map=parameter_map,
    )
