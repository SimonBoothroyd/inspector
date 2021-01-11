// The symbol definitions found here are modified from the plotly versions:
//   https://github.com/plotly/plotly.js/blob/master/src/components/drawing/symbol_defs.js

export const PLOTLY_SYMBOLS: { [name: string]: (r: number) => string } = {
  circle: (r: number): string => {
    const rs = r.toFixed(2);
    return (
      'M' +
      rs +
      ',0A' +
      rs +
      ',' +
      rs +
      ' 0 1,1 0,-' +
      rs +
      'A' +
      rs +
      ',' +
      rs +
      ' 0 0,1 ' +
      rs +
      ',0Z'
    );
  },
  'circle-open': (r: number): string => {
    const rs = r.toFixed(2);
    return (
      'M' +
      rs +
      ',0A' +
      rs +
      ',' +
      rs +
      ' 0 1,1 0,-' +
      rs +
      'A' +
      rs +
      ',' +
      rs +
      ' 0 0,1 ' +
      rs +
      ',0Z'
    );
  },
  x: (r: number): string => {
    const rx = ((r * 0.8) / Math.sqrt(2)).toFixed(2);
    const ne = 'l' + rx + ',' + rx;
    const se = 'l' + rx + ',-' + rx;
    const sw = 'l-' + rx + ',-' + rx;
    const nw = 'l-' + rx + ',' + rx;
    return (
      'M0,' + rx + ne + se + sw + se + sw + nw + sw + nw + ne + nw + ne + 'Z'
    );
  },
  diamond: (r: number): string => {
    const rd = (r * 1.3).toFixed(2);
    return 'M' + rd + ',0L0,' + rd + 'L-' + rd + ',0L0,-' + rd + 'Z';
  },
  cross: (r: number): string => {
    const rc = (r * 0.4).toFixed(2);
    const rc2 = (r * 1.2).toFixed(2);
    return (
      'M' +
      rc2 +
      ',' +
      rc +
      'H' +
      rc +
      'V' +
      rc2 +
      'H-' +
      rc +
      'V' +
      rc +
      'H-' +
      rc2 +
      'V-' +
      rc +
      'H-' +
      rc +
      'V-' +
      rc2 +
      'H' +
      rc +
      'V-' +
      rc +
      'H' +
      rc2 +
      'Z'
    );
  },
  square: (r: number): string => {
    const rs = r.toFixed(2);
    return 'M' + rs + ',' + rs + 'H-' + rs + 'V-' + rs + 'H' + rs + 'Z';
  },
  'star-diamond': (r: number): string => {
    const rp = (r * 1.4).toFixed(2);
    const rc = (r * 1.9).toFixed(2);
    const aPart = 'A ' + rc + ',' + rc + ' 0 0 1 ';
    return (
      'M-' +
      rp +
      ',0' +
      aPart +
      '0,' +
      rp +
      aPart +
      rp +
      ',0' +
      aPart +
      '0,-' +
      rp +
      aPart +
      '-' +
      rp +
      ',0' +
      'Z'
    );
  },
  'triangle-up': (r: number): string => {
    const rt = ((r * 2) / Math.sqrt(3)).toFixed(2);
    const r2 = (r / 2).toFixed(2);
    const rs = r.toFixed(2);
    return 'M-' + rt + ',' + r2 + 'H' + rt + 'L0,-' + rs + 'Z';
  },
  'star-square': (r: number): string => {
    const rp = (r * 1.1).toFixed(2);
    const rc = (r * 2).toFixed(2);
    const aPart = 'A ' + rc + ',' + rc + ' 0 0 1 ';
    return (
      'M-' +
      rp +
      ',-' +
      rp +
      aPart +
      '-' +
      rp +
      ',' +
      rp +
      aPart +
      rp +
      ',' +
      rp +
      aPart +
      rp +
      ',-' +
      rp +
      aPart +
      '-' +
      rp +
      ',-' +
      rp +
      'Z'
    );
  },
  'triangle-down': (r: number): string => {
    const rt = ((r * 2) / Math.sqrt(3)).toFixed(2);
    const r2 = (r / 2).toFixed(2);
    const rs = r.toFixed(2);
    return 'M-' + rt + ',-' + r2 + 'H' + rt + 'L0,' + rs + 'Z';
  },
  pentagon: (r: number): string => {
    const x1 = (r * 0.951).toFixed(2);
    const x2 = (r * 0.588).toFixed(2);
    const y0 = (-r).toFixed(2);
    const y1 = (r * -0.309).toFixed(2);
    const y2 = (r * 0.809).toFixed(2);
    return (
      'M' +
      x1 +
      ',' +
      y1 +
      'L' +
      x2 +
      ',' +
      y2 +
      'H-' +
      x2 +
      'L-' +
      x1 +
      ',' +
      y1 +
      'L0,' +
      y0 +
      'Z'
    );
  },
  hexagon: (r: number): string => {
    const y0 = r.toFixed(2);
    const y1 = (r / 2).toFixed(2);
    const x = ((r * Math.sqrt(3)) / 2).toFixed(2);
    return (
      'M' +
      x +
      ',-' +
      y1 +
      'V' +
      y1 +
      'L0,' +
      y0 +
      'L-' +
      x +
      ',' +
      y1 +
      'V-' +
      y1 +
      'L0,-' +
      y0 +
      'Z'
    );
  },
};
