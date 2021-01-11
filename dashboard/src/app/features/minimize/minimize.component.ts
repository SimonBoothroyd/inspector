import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
} from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import {
  DashboardState,
  MinimizerState,
  ParameterState,
} from '@core/store/state/state.interfaces';
import { Store } from '@ngrx/store';
import { State } from '@core/store';
import { selectDashboardState } from '@core/store/state/state.selectors';
import { MinimizationTrajectory, RESTMolecule } from '@core/models/molecule';
import { MinimizeConformer } from '@core/store/state/state.actions';
import { BarTrace, DEFAULT_COLORS, Figure } from '@core/models/plotly';

@Component({
  selector: 'app-minimize',
  templateUrl: './minimize.component.html',
  styleUrls: ['./minimize.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MinimizeComponent implements OnInit, OnDestroy {
  private stateSubscription?: Subscription;
  public state$!: Observable<DashboardState>;

  public selectedMinimizer: string = 'L-BGFS-B';
  public selectedTrajectory?: string;

  public frameIndex: number = 0;

  constructor(private store: Store<State>) {}

  ngOnInit(): void {
    this.state$ = this.store.select(selectDashboardState);
    this.stateSubscription = this.state$.subscribe((state) => {});
  }

  ngOnDestroy() {
    if (this.stateSubscription) {
      this.stateSubscription.unsubscribe();
    }
  }

  public canMinimize(state: DashboardState): boolean {
    return (
      state.minimizers.size === 0 &&
      Array.from(state.parameters.values()).every(
        (parameter) => parameter.success
      )
    );
  }

  public getStatusIcon(state: DashboardState, name: string): string {
    if (!state.minimizers.has(name)) {
      return 'check_circle_outline';
    }

    const minimizerState = state.minimizers.get(name) as MinimizerState;

    if (minimizerState.loading) {
      return 'hourglass_top';
    }
    if (minimizerState.error) {
      return 'error';
    }

    return 'check_circle';
  }

  public minimize(
    molecule?: RESTMolecule,
    parameters?: ReadonlyMap<string, ParameterState>
  ) {
    if (!molecule || !parameters) {
      return;
    }

    parameters.forEach((value, key) => {
      if (!value.success) {
        return;
      }

      this.store.dispatch(
        new MinimizeConformer(
          key,
          molecule,
          'L-BFGS-B',
          value.smirnoffXML,
          value.openFFName
        )
      );
    });
  }

  public energyTraceFigure(
    minimizers?: ReadonlyMap<string, MinimizerState>
  ): Figure | undefined {
    if (!minimizers) {
      return undefined;
    }

    return {
      subplots: [
        {
          x_axis_label: 'Iteration',
          y_axis_label: 'ΔU (kJ / mol)',
          traces: Array.from(minimizers)
            .filter(([, value]) => value.success)
            .map(
              ([key, value], i): BarTrace => ({
                name: key,
                x: value.frames.map((frame, iteration) => iteration),
                y: value.frames.map(
                  (frame) =>
                    frame.potential_energy - value.frames[0].potential_energy
                ),
                legendgroup: key,
                showlegend: true,
                type: 'scatter',
                hoverinfo: 'none',
                marker: {
                  color: DEFAULT_COLORS[i],
                  symbol: 'x',
                },
              })
            ),
        },
      ],
      legend: {
        orientation: 'h',
      },
    };
  }

  public getMinimizedMolecule(
    state: DashboardState,
    frame: number
  ): RESTMolecule | undefined {
    if (!this.selectedTrajectory || !state.molecule?.molecule) {
      return undefined;
    }

    const molecule: RESTMolecule = JSON.parse(
      JSON.stringify(state.molecule?.molecule)
    );
    const trajectory = state.minimizers.get(
      this.selectedTrajectory
    ) as MinimizationTrajectory;

    molecule.geometry = trajectory.frames[frame].geometry;

    return molecule;
  }
}
