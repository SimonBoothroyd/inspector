import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Actions, Effect, ofType } from '@ngrx/effects';

import {
  catchError,
  concatMap,
  map,
  mergeMap,
  switchMap,
} from 'rxjs/operators';
import {
  ApplyParameters,
  ApplyParametersError,
  ApplyParametersSuccess,
  DashboardActionTypes,
  LoadMolecule,
  LoadMoleculeError,
  LoadMoleculeSuccess,
  MinimizeConformer,
  MinimizeConformerError,
  MinimizeConformerSuccess,
} from '@core/store/state/state.actions';
import {
  AppliedParameters,
  GeometrySummary,
  MinimizationTrajectory,
  RESTMolecule,
} from '@core/models/molecule';
import { combineLatest, of } from 'rxjs';

@Injectable()
export class StateEffects {
  @Effect()
  loadMolecule = this.actions$.pipe(
    ofType(DashboardActionTypes.LoadMolecule),
    switchMap((action: LoadMolecule) => {
      const molecule$ = this.http.post<RESTMolecule>(
        `http://127.0.0.1:5000/api/dev/molecule/json`,
        { file_contents: action.fileContents, file_format: action.fileFormat }
      );

      const geometry$ = molecule$.pipe(
        mergeMap((response: RESTMolecule) =>
          this.http.post<GeometrySummary>(
            `http://127.0.0.1:5000/api/dev/molecule/geometry`,
            { molecule: response }
          )
        )
      );

      return combineLatest([molecule$, geometry$]).pipe(
        map(
          ([molecule, geometry]) =>
            new LoadMoleculeSuccess({ molecule: molecule, geometry: geometry })
        ),
        catchError((error) => of(new LoadMoleculeError(error)))
      );
    })
  );

  @Effect()
  applyParameters = this.actions$.pipe(
    ofType(DashboardActionTypes.ApplyParameters),
    concatMap((action: ApplyParameters) => {
      const body = {
        molecule: action.molecule,
        smirnoff_xml: action.smirnoffXML,
        openff_name: action.openFFName,
      };

      const appliedParameters$ = this.http.post<AppliedParameters>(
        `http://127.0.0.1:5000/api/dev/molecule/parameters`,
        body
      );

      return appliedParameters$.pipe(
        map(
          (parameters) =>
            new ApplyParametersSuccess(action.name, {
              ...parameters,
              smirnoffXML: action.smirnoffXML,
              openFFName: action.openFFName,
            })
        ),
        catchError((error) => of(new ApplyParametersError(action.name, error)))
      );
    })
  );

  @Effect()
  minimizeConformer = this.actions$.pipe(
    ofType(DashboardActionTypes.MinimizeConformer),
    concatMap((action: MinimizeConformer) => {
      const body = {
        molecule: action.molecule,
        smirnoff_xml: action.smirnoffXML,
        openff_name: action.openFFName,
        method: action.method,
      };

      const trajectory$ = this.http.post<MinimizationTrajectory>(
        `http://127.0.0.1:5000/api/dev/molecule/minimize`,
        body
      );

      return trajectory$.pipe(
        map(
          (trajectory) => new MinimizeConformerSuccess(action.name, trajectory)
        ),
        catchError((error) =>
          of(new MinimizeConformerError(action.name, error))
        )
      );
    })
  );

  constructor(private actions$: Actions, private http: HttpClient) {}
}
