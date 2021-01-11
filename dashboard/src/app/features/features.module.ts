import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SharedModule } from '@shared/shared.module';
import { MinimizeComponent } from './minimize/minimize.component';
import { GeometryComponent } from './geometry/geometry.component';
import { ForceFieldComponent } from './force-field/force-field.component';

@NgModule({
  declarations: [MinimizeComponent, GeometryComponent, ForceFieldComponent],
  imports: [CommonModule, SharedModule],
})
export class FeaturesModule {}
