import { createDefaultLoadable, Loadable } from '@core/loadable/loadable';
import {
  AppliedParameters,
  GeometrySummary,
  MinimizationTrajectory,
  RESTMolecule,
} from '@core/models/molecule';

export interface Molecule {
  molecule?: RESTMolecule;
  geometry?: GeometrySummary;
}

export const initialMolecule: Molecule = {
  molecule: undefined,
  geometry: undefined,
};

export interface MoleculeState extends Loadable, Molecule {}

export const initialMoleculeState: MoleculeState = {
  ...initialMolecule,
  ...createDefaultLoadable(),
};

export interface TaggedParameters extends AppliedParameters {
  smirnoffXML?: string;
  openFFName?: string;
}

export interface ParameterState extends Loadable, TaggedParameters {}

export const initialParameterState: ParameterState = {
  ...{
    parameters: {},
    parameter_map: {},
  },
  ...createDefaultLoadable(),
};

export interface MinimizerState extends Loadable, MinimizationTrajectory {}

export const initialMinimizerState: MinimizerState = {
  frames: [],
  ...createDefaultLoadable(),
};

export interface DashboardState {
  molecule?: MoleculeState;
  parameters: ReadonlyMap<string, ParameterState>;
  minimizers: ReadonlyMap<string, MinimizerState>;
}

export const initialDashboardState: DashboardState = {
  molecule: undefined,
  parameters: new Map<string, ParameterState>(),
  minimizers: new Map<string, MinimizerState>(),
};
