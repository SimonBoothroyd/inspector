import { NgModule, Optional, SkipSelf } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MaterialModule } from './material.module';
import { FlexLayoutModule } from '@angular/flex-layout';

import { LoadableComponent } from '@shared/components/loadable/loadable.component';

import { throwIfAlreadyLoaded } from '@core/guards/module-import.guard';
import { FormsModule } from '@angular/forms';

import { PlotlyComponent } from '@shared/components/plotly/plotly.component';

import { PlotlyViaWindowModule } from 'angular-plotly.js';
import { RouterModule } from '@angular/router';
import { PlotlyLegendEntryComponent } from '@shared/components/plotly-legend-entry/plotly-legend-entry.component';
import { MolViewerComponent } from './components/mol-viewer/mol-viewer.component';

@NgModule({
  declarations: [
    LoadableComponent,
    PlotlyComponent,
    PlotlyLegendEntryComponent,
    MolViewerComponent,
  ],
  imports: [
    CommonModule,
    MaterialModule,
    FlexLayoutModule,
    FormsModule,
    PlotlyViaWindowModule,
    RouterModule,
  ],
  exports: [
    MaterialModule,
    FlexLayoutModule,
    LoadableComponent,
    PlotlyComponent,
    PlotlyLegendEntryComponent,
    FormsModule,
    PlotlyViaWindowModule,
    MolViewerComponent,
  ],
})
export class SharedModule {
  constructor(@Optional() @SkipSelf() parentModule: SharedModule) {
    throwIfAlreadyLoaded(parentModule, 'SharedModule');
  }
}
