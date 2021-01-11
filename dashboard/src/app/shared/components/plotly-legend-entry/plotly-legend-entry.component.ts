import {
  ChangeDetectionStrategy,
  Component,
  Input,
  OnInit,
} from '@angular/core';
import { PLOTLY_SYMBOLS } from '@shared/components/plotly-legend-entry/plotly-symbols';

@Component({
  selector: 'app-plotly-legend-entry',
  templateUrl: './plotly-legend-entry.component.html',
  styleUrls: ['./plotly-legend-entry.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlotlyLegendEntryComponent implements OnInit {
  @Input() text!: string;

  @Input() marker?: string;
  @Input() color!: string;

  @Input() line = false;

  constructor() {}

  ngOnInit(): void {}

  symbolPath(name?: string): string {
    console.log(name);

    return !name ? '' : PLOTLY_SYMBOLS[name](3.4);
  }
}
