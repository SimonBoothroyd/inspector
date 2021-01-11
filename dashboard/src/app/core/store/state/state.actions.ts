import { Action } from '@ngrx/store';
import { MinimizationTrajectory, RESTMolecule } from '@core/models/molecule';
import { Molecule, TaggedParameters } from '@core/store/state/state.interfaces';

export enum DashboardActionTypes {
  LoadMolecule = '[MOLECULE] LOAD',
  LoadMoleculeSuccess = '[MOLECULE] SUCCESS',
  LoadMoleculeError = '[MOLECULE] ERROR',

  ApplyParameters = '[PARAMETERS] APPLY',
  ApplyParametersSuccess = '[PARAMETERS] SUCCESS',
  ApplyParametersError = '[PARAMETERS] ERROR',

  DropParameters = '[PARAMETERS] DROP',

  MinimizeConformer = '[CONFORMER] MINIMIZE',
  MinimizeConformerSuccess = '[CONFORMER] SUCCESS',
  MinimizeConformerError = '[CONFORMER] ERROR',
}

export class LoadMolecule implements Action {
  readonly type = DashboardActionTypes.LoadMolecule;

  constructor(readonly fileContents: string, readonly fileFormat: string) {}
}

export class LoadMoleculeSuccess implements Action {
  readonly type = DashboardActionTypes.LoadMoleculeSuccess;

  constructor(public payload: Molecule) {}
}

export class LoadMoleculeError implements Action {
  readonly type = DashboardActionTypes.LoadMoleculeError;

  constructor(public error: any) {}
}

export class ApplyParameters implements Action {
  readonly type = DashboardActionTypes.ApplyParameters;

  constructor(
    public readonly name: string,
    public readonly molecule: RESTMolecule,
    public readonly smirnoffXML?: string,
    public readonly openFFName?: string
  ) {}
}

export class ApplyParametersSuccess implements Action {
  readonly type = DashboardActionTypes.ApplyParametersSuccess;

  constructor(
    public readonly name: string,
    public readonly payload: TaggedParameters
  ) {}
}

export class ApplyParametersError implements Action {
  readonly type = DashboardActionTypes.ApplyParametersError;

  constructor(public readonly name: string, public readonly error: any) {}
}

export class DropParameters implements Action {
  readonly type = DashboardActionTypes.DropParameters;

  constructor(public readonly name: string) {}
}

export class MinimizeConformer implements Action {
  readonly type = DashboardActionTypes.MinimizeConformer;

  constructor(
    public readonly name: string,
    public readonly molecule: RESTMolecule,
    public readonly method: string,
    public readonly smirnoffXML?: string,
    public readonly openFFName?: string
  ) {}
}

export class MinimizeConformerSuccess implements Action {
  readonly type = DashboardActionTypes.MinimizeConformerSuccess;

  constructor(
    public readonly name: string,
    public readonly payload: MinimizationTrajectory
  ) {}
}

export class MinimizeConformerError implements Action {
  readonly type = DashboardActionTypes.MinimizeConformerError;

  constructor(public readonly name: string, public readonly error: any) {}
}

export type DashboardAction =
  | LoadMolecule
  | LoadMoleculeSuccess
  | LoadMoleculeError
  | ApplyParameters
  | ApplyParametersSuccess
  | ApplyParametersError
  | DropParameters
  | MinimizeConformer
  | MinimizeConformerSuccess
  | MinimizeConformerError;
