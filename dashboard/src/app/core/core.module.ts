import { NgModule, Optional, SkipSelf } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MaterialModule } from '@shared/material.module';

import { RouterModule } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';

import { StoreModule } from '@ngrx/store';
import { StoreRouterConnectingModule } from '@ngrx/router-store';

import { reducers } from '@core/store';
import { throwIfAlreadyLoaded } from '@core/guards/module-import.guard';

import { RouteSerializer } from '@core/store/routes/route.serializer';

import { StateEffects } from '@core/store/state/state.effects';
import { EffectsModule } from '@ngrx/effects';

@NgModule({
  imports: [
    CommonModule,

    MaterialModule,

    RouterModule,
    HttpClientModule,

    StoreModule.forRoot(reducers),
    EffectsModule.forRoot([StateEffects]),

    StoreRouterConnectingModule.forRoot({
      serializer: RouteSerializer,
    }),
  ],
  // providers: [StateService],
})
export class CoreModule {
  constructor(@Optional() @SkipSelf() parentModule: CoreModule) {
    throwIfAlreadyLoaded(parentModule, 'CoreModule');
  }
}
