import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ForceFieldComponent } from '@app/features/force-field/force-field.component';
import { MinimizeComponent } from '@app/features/minimize/minimize.component';

const routes: Routes = [
  { path: '', redirectTo: '/parameters', pathMatch: 'full' },
  { path: 'parameters', component: ForceFieldComponent },
  // { path: 'geometry', component: GeometryComponent },
  { path: 'minimize', component: MinimizeComponent },
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {
      relativeLinkResolution: 'corrected',
    }),
  ],
  exports: [RouterModule],
})
export class AppRoutingModule {}
