import { withLoadable } from '@core/loadable/with-loadable';
import {
  DashboardState,
  initialDashboardState,
  initialMinimizerState,
  initialMoleculeState,
  initialParameterState,
  MinimizerState,
  MoleculeState,
  ParameterState,
} from '@core/store/state/state.interfaces';
import {
  ApplyParameters,
  ApplyParametersError,
  ApplyParametersSuccess,
  DashboardAction,
  DashboardActionTypes,
  DropParameters,
  MinimizeConformer,
  MinimizeConformerError,
  MinimizeConformerSuccess,
} from '@core/store/state/state.actions';
import { Action } from '@ngrx/store';

function moleculeReducer(
  state: MoleculeState = { ...initialMoleculeState },
  action: DashboardAction
): MoleculeState {
  return action.type != DashboardActionTypes.LoadMoleculeSuccess
    ? state
    : {
        ...state,
        ...action.payload,
      };
}

function parameterReducer(
  state: ParameterState = { ...initialParameterState },
  action: DashboardAction
): ParameterState {
  switch (action.type) {
    case DashboardActionTypes.ApplyParametersSuccess:
      state = { ...state, ...action.payload };
      break;
  }

  return state;
}

function minimizerReducer(
  state: MinimizerState = { ...initialMinimizerState },
  action: DashboardAction
): MinimizerState {
  switch (action.type) {
    case DashboardActionTypes.MinimizeConformerSuccess:
      state = { ...state, ...action.payload };
      break;
  }

  return state;
}

export function reducer(
  state: DashboardState = { ...initialDashboardState },
  action: Action
): DashboardState {
  const dashboardAction: DashboardAction = action as DashboardAction;

  switch (action.type) {
    case DashboardActionTypes.LoadMolecule:
    case DashboardActionTypes.LoadMoleculeSuccess:
    case DashboardActionTypes.LoadMoleculeError:
      state = {
        molecule: withLoadable(moleculeReducer, {
          loadingActionType: DashboardActionTypes.LoadMolecule,
          successActionType: DashboardActionTypes.LoadMoleculeSuccess,
          errorActionType: DashboardActionTypes.LoadMoleculeError,
        })(state.molecule ?? { ...initialMoleculeState }, dashboardAction),
        parameters: new Map<string, ParameterState>(),
        minimizers: new Map<string, MinimizerState>(),
      };
      break;

    case DashboardActionTypes.ApplyParameters:
    case DashboardActionTypes.ApplyParametersSuccess:
    case DashboardActionTypes.ApplyParametersError:
      const applyAction = action as
        | ApplyParameters
        | ApplyParametersSuccess
        | ApplyParametersError;

      const appliedState = new Map(state.parameters);

      appliedState.set(
        applyAction.name,
        withLoadable(parameterReducer, {
          loadingActionType: DashboardActionTypes.ApplyParameters,
          successActionType: DashboardActionTypes.ApplyParametersSuccess,
          errorActionType: DashboardActionTypes.ApplyParametersError,
        })(
          state.parameters.get(applyAction.name) ?? {
            ...initialParameterState,
          },
          applyAction
        )
      );

      state = { ...state, parameters: appliedState };
      break;

    case DashboardActionTypes.DropParameters:
      const dropAction = action as DropParameters;
      const droppedState = new Map(state.parameters);

      if (state.parameters.get(dropAction.name) !== undefined) {
        droppedState.delete(dropAction.name);
      }
      state = { ...state, parameters: droppedState };

      break;

    case DashboardActionTypes.MinimizeConformer:
    case DashboardActionTypes.MinimizeConformerSuccess:
    case DashboardActionTypes.MinimizeConformerError:
      const minimizeAction = action as
        | MinimizeConformer
        | MinimizeConformerSuccess
        | MinimizeConformerError;

      const minimizerState = new Map(state.minimizers);

      minimizerState.set(
        minimizeAction.name,
        withLoadable(minimizerReducer, {
          loadingActionType: DashboardActionTypes.MinimizeConformer,
          successActionType: DashboardActionTypes.MinimizeConformerSuccess,
          errorActionType: DashboardActionTypes.MinimizeConformerError,
        })(
          state.minimizers.get(minimizeAction.name) ?? {
            ...initialMinimizerState,
          },
          minimizeAction
        )
      );

      state = { ...state, minimizers: minimizerState };
      break;

    default:
      state = { ...state };
  }

  return state;
}
