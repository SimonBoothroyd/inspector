import {
  Loadable,
  onLoadableError,
  onLoadableLoad,
  onLoadableSuccess,
} from './loadable';

export interface Action {
  type: string;
}

export type ReducerFunction<T, U extends Action> = (state: T, action: U) => T;

export interface ActionTypes {
  loadingActionType: string;
  successActionType: string;
  errorActionType: string;
}

export function withLoadable<T extends Loadable, U extends Action = Action>(
  reducer: ReducerFunction<T, U>,
  { loadingActionType, successActionType, errorActionType }: ActionTypes
) {
  return (state: T, action: U): T => {
    if (action.type === loadingActionType) {
      state = onLoadableLoad(state);
    }
    if (action.type === successActionType) {
      state = onLoadableSuccess(state);
    }
    if (action.type === errorActionType) {
      state = onLoadableError(state, (action as any).error);
    }
    return reducer(state, action);
  };
}
