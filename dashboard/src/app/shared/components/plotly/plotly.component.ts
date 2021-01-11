// This component is heavily cannibalised from the angular-plotly version
// which can be found here:
//
//     https://github.com/plotly/angular-plotly.js/blob/master/src/app/shared/plot/plot.component.ts
//

import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';

import { BreakpointObserver, BreakpointState } from '@angular/cdk/layout';

import { Plotly } from 'angular-plotly.js/lib/plotly.interface';
import { PlotlyService } from 'angular-plotly.js';

import { Subscription } from 'rxjs';
import { BarTrace, Figure, ScatterTrace } from '@core/models/plotly';

interface Axis {
  title?: string;
  showticklabels?: boolean;
  automargin?: boolean;
  matches?: string;
}

interface LegendEntry {
  group: string;
  name: string;

  text: string;
  marker?: string;
  color: string;
  line: boolean;
}

@Component({
  selector: 'app-plotly',
  templateUrl: './plotly.component.html',
  styleUrls: ['./plotly.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlotlyComponent implements OnInit, OnChanges, OnDestroy {
  private innerFigure?: Figure;
  private plotData: (BarTrace | ScatterTrace)[] = [];

  private toggleLegendTimer: any;

  private plotsPerRow$!: Subscription;
  private plotsPerRow: number;

  public readonly defaultClassName = 'js-plotly-plot';

  plotInstance!: Plotly.PlotlyHTMLElement;

  @ViewChild('plot', { static: true }) plotElement!: ElementRef;

  @Input() set figure(value: Figure | undefined) {
    if (this.innerFigure === value) {
      return;
    }

    this.innerFigure = value;
    this.plotData = !this.innerFigure ? [] : this.generatePlotData();
  }

  @Input() subplotWidth: number;
  @Input() subplotHeight: number;

  @Input() autoLeftMargin = false;

  @Input() config?: Partial<Plotly.Config>;

  @Input() breakpointQueries: string[];
  @Input() breakpointColumns: { [query: string]: number };

  @Output() hover = new EventEmitter();
  @Output() unhover = new EventEmitter<undefined>();

  constructor(
    public plotly: PlotlyService,
    private breakpointObserver: BreakpointObserver,
    private ref: ChangeDetectorRef
  ) {
    this.plotsPerRow = 1;

    this.subplotWidth = 260;
    this.subplotHeight = 260;

    this.breakpointQueries = [
      '(max-width: 999px)',
      '(min-width: 1000px) and (max-width: 1259px)',
      '(min-width: 1260px)',
    ];
    this.breakpointColumns = {
      '(max-width: 999px)': 1,
      '(min-width: 1000px) and (max-width: 1259px)': 2,
      '(min-width: 1260px)': 3,
    };

    this.innerFigure = { subplots: [] };
  }

  ngOnInit(): void {
    this.createPlot().then(
      () => this.ref.detectChanges(),
      (error) => console.error('There was an error creating the plot: ' + error)
    );

    this.plotsPerRow$ = this.breakpointObserver
      .observe(this.breakpointQueries)
      .subscribe((state: BreakpointState) => this.updatePlotsPerRow(state));
  }

  ngOnDestroy(): void {
    if (this.plotInstance) {
      PlotlyService.remove(this.plotInstance);
    }
    if (this.plotsPerRow$) {
      this.plotsPerRow$.unsubscribe();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!this.plotInstance) {
      return;
    }
    this.updatePlot().then(() => {});
  }

  private createPlot(): Promise<void> {
    const plot$: Promise<Plotly.PlotlyHTMLElement> = this.plotly.newPlot(
      this.plotElement.nativeElement,
      [],
      undefined,
      this.config,
      undefined
    );

    return plot$
      .then(
        (plotInstance) => {
          this.plotInstance = plotInstance;

          this.plotInstance.on('plotly_hover', (data: any) =>
            this.hover.emit(data)
          );
          this.plotInstance.on('plotly_unhover', (data: any) =>
            this.unhover.emit(undefined)
          );
        },
        (error) => console.error('Error while initializing plot:', error)
      )
      .then(() => this.updatePlot())
      .then(() => this.resizePlot());
  }

  private generatePlotData(): (BarTrace | ScatterTrace)[] {
    if (this.innerFigure?.subplots === undefined) {
      return [];
    }

    const traces = this.innerFigure.subplots.map(
      (subplot, i) =>
        subplot.traces?.map((trace) => ({
          ...trace,
          xaxis: `x${i + 1}`,
          yaxis: `y${i + 1}`,
          visible: true,
        })) ?? []
    );

    return JSON.parse(
      JSON.stringify(([] as (BarTrace | ScatterTrace)[]).concat(...traces))
    );
  }

  private generateLayout() {
    if (this.innerFigure?.subplots == undefined) {
      return {};
    }

    const nSubplots = this.innerFigure.subplots.length;

    const nCols = Math.max(1, Math.min(this.plotsPerRow, nSubplots));
    const nRows = Math.max(1, Math.ceil(nSubplots / nCols));

    // Define any plot sub-titles.
    const annotations = this.innerFigure.subplots.map((subplot, i) =>
      !subplot.title
        ? undefined
        : {
            font: { size: 12 },
            showarrow: false,
            text: subplot.title,
            x: 0.5,
            xanchor: 'center',
            xref: i > 0 ? `x${i + 1} domain` : 'x domain',
            y: 1.01,
            yanchor: 'bottom',
            yref: i > 0 ? `y${i + 1} domain` : 'y domain',
          }
    );

    // Define any x-axis titles.
    const xAxes = this.innerFigure.subplots.reduce<Record<string, Axis>>(
      (object, subplot, i) => ({
        ...object,
        [`xaxis${i + 1}`]: {
          title: subplot.x_axis_label,
          showticklabels: subplot.show_x_ticks,
        },
      }),
      {}
    );

    // Define any y-axis titles.
    const yAxes = this.innerFigure.subplots.reduce<Record<string, Axis>>(
      (object, subplot, i) => ({
        ...object,
        [`yaxis${i + 1}`]: {
          title: i % nCols == 0 ? subplot.y_axis_label : undefined,
          automargin: this.autoLeftMargin,
          showticklabels: subplot.show_y_ticks,
        },
      }),
      {}
    );

    // Match axes if requested.
    if (this.innerFigure.shared_axes) {
      for (let k in xAxes) {
        if (k == 'xaxis1') {
          continue;
        }
        xAxes[k]['matches'] = 'x';
      }
      for (let k in yAxes) {
        yAxes[k]['matches'] = 'x';
      }
    }

    // Check whether to add padding at the bottom.
    let includeXAxisPadding = false;

    if (
      this.innerFigure.subplots.some(
        (subplot) => subplot.x_axis_label != undefined
      )
    ) {
      includeXAxisPadding = true;
    }

    return {
      grid: { rows: nRows, columns: nCols, pattern: 'independent' },
      showlegend: false,
      width: this.subplotWidth * nCols,
      height: this.subplotHeight * nRows,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      annotations: annotations,
      margin: {
        t: 20,
        b: includeXAxisPadding ? 50 : 0,
      },
      hovermode: 'closest',
      ...xAxes,
      ...yAxes,
    };
  }

  private updatePlotsPerRow(state: BreakpointState) {
    let plotsPerRow = this.plotsPerRow;

    for (const breakpointQuery of this.breakpointQueries) {
      if (!state.breakpoints[breakpointQuery]) {
        continue;
      }

      plotsPerRow = this.breakpointColumns[breakpointQuery];
      break;
    }

    if (plotsPerRow == this.plotsPerRow) {
      return;
    }

    this.plotsPerRow = plotsPerRow;

    this.updatePlot().then(() => this.resizePlot());
  }

  public updatePlot(): Promise<void> {
    if (!this.innerFigure || !this.plotly || !this.plotInstance) {
      return Promise.resolve();
    }

    let plotLayout = this.generateLayout();
    let plotConfig = { ...this.config };

    return this.plotly
      .update(
        this.plotInstance,
        this.plotData,
        plotLayout,
        plotConfig,
        undefined
      )
      .then(
        () => {},
        (error) =>
          console.error('There was an error updating the plot: ' + error)
      );
  }

  public resizePlot() {
    if (!this.plotly || !this.plotInstance) {
      return;
    }

    if (
      this.plotInstance.offsetWidth <= 0 ||
      this.plotInstance.offsetHeight <= 0
    ) {
      return;
    }

    this.plotly.resize(this.plotInstance);
  }

  public generateLegend(): LegendEntry[] {
    if (!this.innerFigure) {
      return [];
    }

    return this.plotData
      .filter((value) => value.showlegend)
      .map((value) => ({
        group: value.legendgroup,
        name: value.name,
        text: value.name,
        marker: !value.marker ? 'circle' : value.marker.symbol,
        color: !value.visible
          ? 'lightgray'
          : !value.marker
          ? 'rgb(0, 0, 0)'
          : value.marker.color,
        line: value.type == 'scatter',
      }));
  }

  private toggleTrace(legendGroup: string, traceName: string) {
    this.plotData
      .filter(
        (trace) => trace.legendgroup == legendGroup && trace.name == traceName
      )
      .forEach((trace) => (trace.visible = !trace.visible));

    this.plotly.getPlotly().redraw(this.plotInstance);
    this.ref.detectChanges();
  }

  private toggleTraces(legendGroup: string, traceName: string) {
    const shouldEnable = this.plotData.some((trace) => !trace.visible);

    if (shouldEnable) {
      this.plotData.forEach((trace) => (trace.visible = true));
    } else {
      this.plotData.forEach(
        (trace) =>
          (trace.visible =
            trace.legendgroup == legendGroup && trace.name == traceName)
      );
    }

    this.plotly.getPlotly().redraw(this.plotInstance);
  }

  public onToggleTrace(legendGroup: string, traceName: string): void {
    if (this.toggleLegendTimer != undefined) {
      clearTimeout(this.toggleLegendTimer);
      this.toggleLegendTimer = undefined;

      this.toggleTraces(legendGroup, traceName);
      return;
    }

    this.toggleLegendTimer = setTimeout(() => {
      this.toggleLegendTimer = undefined;
      this.toggleTrace(legendGroup, traceName);
    }, 250);
  }
}
