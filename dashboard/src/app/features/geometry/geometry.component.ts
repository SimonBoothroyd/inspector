import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-geometry',
  templateUrl: './geometry.component.html',
  styleUrls: ['./geometry.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GeometryComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {}
}
