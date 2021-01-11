import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CoreModule } from '@core/core.module';
import { SharedModule } from '@shared/shared.module';
import { MaterialModule } from '@shared/material.module';
import { FeaturesModule } from '@app/features/features.module';

@NgModule({
  declarations: [AppComponent],
  imports: [
    CoreModule,
    FeaturesModule,
    SharedModule,
    MaterialModule,

    BrowserModule,
    BrowserAnimationsModule,

    AppRoutingModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
