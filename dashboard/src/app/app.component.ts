import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { State } from '@core/store';
import { Observable } from 'rxjs';
import { DashboardState } from '@core/store/state/state.interfaces';
import { selectDashboardState } from '@core/store/state/state.selectors';
import {
  LoadMolecule,
  LoadMoleculeError,
} from '@core/store/state/state.actions';
import { getRouterInfo } from '@core/store/routes/route.selectors';
import { RouterStateUrl } from '@core/store/routes/route.serializer';

interface TabPage {
  label: string;
  link: string;
  index: number;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent implements OnInit {
  public state$!: Observable<DashboardState>;
  public routerState$!: Observable<RouterStateUrl>;

  public tabPages: TabPage[] = [
    {
      label: 'Parameters',
      link: '/parameters',
      index: 0,
    },
    // {
    //   label: 'Geometry',
    //   link: '/geometry',
    //   index: 1,
    // },
    {
      label: 'Minimize',
      link: '/minimize',
      index: 1,
    },
  ];

  public constructor(private store: Store<State>) {}

  ngOnInit(): void {
    this.state$ = this.store.select(selectDashboardState);
    this.routerState$ = this.store.select(getRouterInfo);
  }

  public activeTabIndex(routerState: RouterStateUrl | null): number {
    return !routerState
      ? -1
      : this.tabPages.findIndex((tab) => routerState.url.startsWith(tab.link));
  }

  public async handleFileInput(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.item(0) as File;

    if (!file) {
      return;
    }

    const extensionMatches = /(?:\.([^.]+))?$/.exec(file.name);
    const extension = !extensionMatches
      ? undefined
      : extensionMatches[0].toUpperCase().replace('.', '');

    if (extension !== 'SDF') {
      this.store.dispatch(
        new LoadMoleculeError({
          message: 'Only SDF files can currently be loaded.',
        })
      );
      return;
    }

    const text = await file.text();

    this.store.dispatch(new LoadMolecule(text, extension));
  }
}
