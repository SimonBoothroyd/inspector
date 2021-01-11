import { Loadable } from '@core/loadable/loadable';
import { Figure } from '@core/models/plotly';

export interface FigureState extends Figure, Loadable {}
