import { routerReducer, RouterReducerState } from '@ngrx/router-store';
import { ActionReducerMap } from '@ngrx/store';

import { RouterStateUrl } from '@core/store/routes/route.serializer';

import { DashboardState } from '@core/store/state/state.interfaces';
import * as stateReducers from '@core/store/state/state.reducers';

export interface State {
  state: DashboardState;
  router: RouterReducerState<RouterStateUrl>;
}

export const reducers: ActionReducerMap<State> = {
  state: stateReducers.reducer,
  router: routerReducer,
};
