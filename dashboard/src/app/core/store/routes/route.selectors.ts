import { createFeatureSelector, createSelector } from '@ngrx/store';
import { RouterReducerState } from '@ngrx/router-store';
import { RouterStateUrl } from '@core/store/routes/route.serializer';

export const selectReducerState = createFeatureSelector<
  RouterReducerState<RouterStateUrl>
>('router');
export const getRouterInfo = createSelector(
  selectReducerState,
  (state) => state?.state
);
