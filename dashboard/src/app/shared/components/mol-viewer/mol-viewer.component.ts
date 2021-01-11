import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  NgZone,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { RESTMolecule } from '@core/models/molecule';

interface Atom {
  elem: string;
  x: number;
  y: number;
  z: number;
  serial: number;
}

@Component({
  selector: 'app-mol-viewer',
  templateUrl: './mol-viewer.component.html',
  styleUrls: ['./mol-viewer.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MolViewerComponent implements OnInit {
  private innerMolecule?: RESTMolecule;

  private selectedIds: number[] = [];
  private viewer: any;

  @ViewChild('container', { static: true }) container!: ElementRef;

  @Input() set molecule(value: RESTMolecule | undefined) {
    this.innerMolecule = value;
    this.renderMolecule();
  }

  @Output() selectionChanged = new EventEmitter<number[]>();

  constructor(private zone: NgZone) {}

  ngOnInit(): void {
    this.zone.runOutsideAngular(() => {
      this.viewer = $3Dmol.createViewer(this.container.nativeElement, {
        backgroundColor: 'white',
        defaultcolors: $3Dmol.elementColors.rasmol,
        antialias: true,
        disableFog: true,
      });

      this.renderMolecule();
    });
  }

  private renderMolecule() {
    this.selectedIds = [];
    this.viewer?.clear();

    if (!this.innerMolecule || !this.viewer) {
      return;
    }

    const molecule = this.innerMolecule;

    // Create the molecule model
    const atoms = molecule.symbols.map((symbol, i) => ({
      elem: symbol,
      x: molecule.geometry[i * 3],
      y: molecule.geometry[i * 3 + 1],
      z: molecule.geometry[i * 3 + 2],
      bonds: [] as number[],
      bondOrder: [] as number[],
    }));

    molecule.connectivity.forEach((bond) => {
      atoms[bond[0]].bonds.push(bond[1]);
      atoms[bond[1]].bonds.push(bond[0]);

      atoms[bond[0]].bondOrder.push(bond[2]);
      atoms[bond[1]].bondOrder.push(bond[2]);
    });

    const model = this.viewer.addModel();
    model.addAtoms(atoms);

    // Update the styles.
    this.setStyles();

    // Allow atoms to be selected.
    const parent = this;
    this.viewer.setClickable({}, true, (atom: Atom) =>
      parent.onClickAtom(atom)
    );

    // Render the molecule.
    this.viewer.zoomTo();
    this.viewer.render();
  }

  private setStyles() {
    // Update the styles of the unselected atoms
    this.viewer.setStyle(
      {},
      { sphere: { radius: '0.25' }, stick: { radius: 0.1 } }
    );

    // Update the styles of the selected.
    this.viewer.setStyle(
      { serial: this.selectedIds },
      { sphere: { radius: '0.25', color: 'yellow' }, stick: { radius: 0.1 } }
    );
  }

  private onClickAtom(atom: Atom) {
    if (this.selectedIds.includes(atom.serial)) {
      this.selectedIds.splice(this.selectedIds.indexOf(atom.serial), 1);
    } else {
      this.selectedIds.push(atom.serial);
    }

    this.viewer.removeAllLabels();

    this.selectedIds.forEach((i) => {
      this.viewer.addLabel(i, {
        position: {
          x: this.innerMolecule?.geometry[i * 3],
          y: this.innerMolecule?.geometry[i * 3 + 1],
          z: this.innerMolecule?.geometry[i * 3 + 2],
        },
        backgroundColor: 0x800080,
        backgroundOpacity: 0.8,
      });
    });

    this.setStyles();
    this.viewer.render();

    this.selectionChanged.emit([...this.selectedIds]);
  }
}
