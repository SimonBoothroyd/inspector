import { createFeatureSelector } from '@ngrx/store';

import { DashboardState } from '@core/store/state/state.interfaces';

export const selectDashboardState = createFeatureSelector<DashboardState>(
  'state'
);
