import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
} from '@angular/core';
import { Observable } from 'rxjs';
import {
  DashboardState,
  ParameterState,
} from '@core/store/state/state.interfaces';
import { Store } from '@ngrx/store';
import { State } from '@core/store';
import { selectDashboardState } from '@core/store/state/state.selectors';
import { ApplyParameters } from '@core/store/state/state.actions';
import {
  AngleType,
  BondType,
  ChargeIncrementType,
  ConstraintType,
  ImproperTorsionType,
  LibraryChargeType,
  ProperTorsionType,
  VdWType,
} from '@core/models/molecule';
import { BarTrace, DEFAULT_COLORS, Figure } from '@core/models/plotly';

type ParameterType =
  | ConstraintType
  | BondType
  | AngleType
  | ProperTorsionType
  | ImproperTorsionType
  | VdWType
  | LibraryChargeType
  | ChargeIncrementType;

@Component({
  selector: 'app-force-field',
  templateUrl: './force-field.component.html',
  styleUrls: ['./force-field.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ForceFieldComponent implements OnInit, OnDestroy {
  public state$!: Observable<DashboardState>;

  public selectedHandler?: string;
  public selectedAttribute?: string;

  public hoveredAttribute?: string;

  constructor(private store: Store<State>) {}

  ngOnInit(): void {
    this.state$ = this.store.select(selectDashboardState);
  }

  ngOnDestroy() {}

  public forceFieldOptions(
    parameters?: ReadonlyMap<string, ParameterState>
  ): string[] {
    return [
      'openff-1.0.0.offxml',
      'openff-1.2.0.offxml',
      'openff-1.3.0.offxml',
    ].filter((name) => (!parameters ? true : !parameters.has(name)));
  }

  public canSelectForceField(state?: DashboardState): boolean {
    if (!state) {
      return false;
    }

    const parameterStates = [...state.parameters.values()];
    return (
      parameterStates.length === 0 ||
      parameterStates.every((value) => !value.loading)
    );
  }

  public onForceFieldSelected(value: string, state?: DashboardState) {
    if (state?.molecule?.molecule) {
      this.store.dispatch(
        new ApplyParameters(value, state.molecule.molecule, undefined, value)
      );
    }
  }

  public parameterHandlers(
    state?: DashboardState
  ): ReadonlyMap<string, string[]> {
    if (!state) {
      return new Map();
    }

    const handlers = new Map<string, Set<string>>();

    state.parameters.forEach((parameterState) => {
      for (const [handlerName, parameters] of Object.entries(
        parameterState.parameters
      )) {
        if (!handlers.has(handlerName)) {
          handlers.set(handlerName, new Set<string>());
        }

        parameters.forEach((parameter) => {
          this.parameterToAttributes(parameter).forEach((attributeName) =>
            handlers.get(handlerName)?.add(attributeName)
          );
        });
      }
    });

    const sortedHandlers = new Map<string, string[]>();

    handlers.forEach((value, key) =>
      sortedHandlers.set(key, Array.from(value).sort())
    );

    return new Map<string, string[]>(sortedHandlers);
  }

  public parameterToAttributes(parameter: ParameterType): string[] {
    switch (parameter.type) {
      case 'ConstraintType':
        return ['distance'];
      case 'BondType':
        return ['k', 'length'];
      case 'AngleType':
        return ['k', 'angle'];
      case 'ProperTorsionType':
      case 'ImproperTorsionType':
        const torsion = parameter as ProperTorsionType | ImproperTorsionType;

        return [
          ...torsion.periodicity.map((value, i) => `periodicity${i}`),
          ...torsion.phase.map((value, i) => `phase${i}`),
          ...torsion.periodicity.map((value, i) => `k${i}`),
          ...torsion.periodicity.map((value, i) => `idivf${i}`),
        ];

      case 'vdWType':
        return ['epsilon', 'sigma'];
      // case "LibraryChargeType":
      //   //charge
      //   break;
      // case "ChargeIncrementType":
      //   // charge_increment
      //   break;
      default:
        return [];
    }
  }

  private static attributeValue(
    parameter: ParameterType,
    attribute: string
  ): number {
    const indexedTypes = [
      'ProperTorsionType',
      'ImproperTorsionType',
      'LibraryChargeType',
      'ChargeIncrementType',
    ];

    const parameterType = parameter.type as string;

    if (indexedTypes.indexOf(parameterType) < 0) {
      return parameter[attribute] as number;
    }

    const indexIndex = attribute.search(/\d/);

    const attributeName = attribute.slice(0, indexIndex);
    const index = parseInt(attribute.slice(indexIndex));

    return (parameter[attributeName] as number[])[index];
  }

  public forceFieldFigure(
    parameters?: ReadonlyMap<string, ParameterState>
  ): Figure | undefined {
    if (!parameters || !this.selectedHandler || !this.selectedAttribute) {
      return undefined;
    }

    const handler = this.selectedHandler;
    const attribute = this.selectedAttribute;

    return {
      subplots: [
        {
          x_axis_label: 'id',
          y_axis_label: this.selectedAttribute,
          traces: Array.from(parameters).map(
            ([key, value], i): BarTrace => ({
              name: key,
              x: value.parameters[handler].map((parameter) => parameter.id),
              y: value.parameters[handler].map((parameter) =>
                ForceFieldComponent.attributeValue(parameter, attribute)
              ),
              legendgroup: name,
              showlegend: true,
              type: 'bar',
              hoverinfo: 'none',
              marker: {
                color: DEFAULT_COLORS[i],
                symbol: 'square',
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

  public onAttributeHover(e?: any) {
    if (e?.points && e.points.length > 0) {
      this.hoveredAttribute = e.points[0].x;
    } else {
      this.hoveredAttribute = undefined;
    }
  }

  public hoveredSMIRKS(
    parameters?: ReadonlyMap<string, ParameterState>
  ): string {
    if (!this.hoveredAttribute || !this.selectedHandler || !parameters) {
      return '';
    }

    const selectedHandler = this.selectedHandler;
    const parametersById: { [id: string]: ParameterType } = {};

    parameters?.forEach((value, key) => {
      (value.parameters[selectedHandler] ?? ([] as ParameterType[])).forEach(
        (parameter) => (parametersById[parameter.id] = parameter)
      );
    });

    return (
      parametersById[this.hoveredAttribute].smirks ?? 'Something went wrong...'
    );
  }
}
