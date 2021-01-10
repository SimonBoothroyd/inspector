from tempfile import NamedTemporaryFile

import numpy
from fastapi import APIRouter
from openforcefield.topology import Molecule
from openforcefield.typing.engines.smirnoff import ForceField
from simtk import unit

from inspector.backend.models.molecules import (
    ApplyParametersBody,
    MinimizeConformerBody,
    MoleculeToJSONBody,
    SummarizeGeometryBody,
)
from inspector.library.forcefield import label_molecule
from inspector.library.geometry import summarize_geometry
from inspector.library.minimization import EnergyMinimizer
from inspector.library.models.forcefield import AppliedParameters
from inspector.library.models.geometry import GeometrySummary
from inspector.library.models.minimization import MinimizationTrajectory
from inspector.library.models.molecule import RESTMolecule

api_router = APIRouter()


@api_router.post("/molecule/json", response_model=RESTMolecule)
async def post_molecule_to_json(body: MoleculeToJSONBody):

    with NamedTemporaryFile(suffix=f".{body.file_format}") as temporary_file:

        with open(temporary_file.name, "w") as file:
            file.write(body.file_contents)

        off_molecule = Molecule.from_file(file.name, body.file_format)

    return RESTMolecule.from_openff(off_molecule)


@api_router.post("/molecule/parameters", response_model=AppliedParameters)
async def post_apply_parameters(body: ApplyParametersBody):

    force_field = ForceField(
        body.smirnoff_xml if body.smirnoff_xml is not None else body.openff_name
    )

    return label_molecule(body.molecule, force_field=force_field)


@api_router.post("/molecule/geometry", response_model=GeometrySummary)
async def post_summarize_geometry(body: SummarizeGeometryBody):

    conformer = numpy.array(body.molecule.geometry).reshape(
        len(body.molecule.symbols), 3
    )
    return summarize_geometry(body.molecule, conformer * unit.angstrom)


@api_router.post("/molecule/minimize", response_model=MinimizationTrajectory)
async def post_minimize_conformer(body: MinimizeConformerBody):

    force_field = ForceField(
        body.smirnoff_xml if body.smirnoff_xml is not None else body.openff_name
    )
    conformer = (
        numpy.array(body.molecule.geometry).reshape(len(body.molecule.symbols), 3)
        * unit.angstrom
    )

    return EnergyMinimizer.minimize(
        body.molecule, conformer, force_field, method=body.method
    )
