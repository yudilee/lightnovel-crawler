const _mask24 = (1 << 24) - 1;
type Theme = 'light' | 'dark';

function buildColor(code: number, theme: Theme): string {
  const start = theme === 'dark' ? 0x09 : 0xcf;
  const stop = theme === 'dark' ? 0x3f : 0xf5;

  const range = stop - start;
  const r = (code & range) + start;
  code >>= 8;
  const g = (code & range) + start;
  code >>= 8;
  const b = (code & range) + start;

  let hex = '#';
  hex += r.toString(16).padStart(2, '0');
  hex += g.toString(16).padStart(2, '0');
  hex += b.toString(16).padStart(2, '0');
  return hex;
}

/**
 * Get a random color (non-deterministic)
 */
export function getRandomColor(theme: Theme = 'dark'): string {
  const code = Math.floor(Math.random() * (_mask24 + 1));
  return buildColor(code, theme);
}

/**
 * Generate a deterministic random color based on a ID
 */
export function getColorForId(id: string = '', theme: Theme = 'dark'): string {
  let code = _mask24;
  for (let i = 0; i < id.length && i < 6; ++i) {
    code ^= (code << 4) ^ id.charCodeAt(i);
    code ^= code >>> 24;
    code = code << 4;
  }
  return buildColor(code, theme);
}
/**
 * Get a random gradient (non-deterministic)
 */
export function getRandomGradient(
  theme: Theme = 'dark',
  degress?: number
): string {
  const color1 = getRandomColor(theme);
  const color2 = getRandomColor(theme);
  degress ??= Math.floor(Math.random() * 360);
  return `linear-gradient(${degress}deg, ${color1}, ${color2})`;
}

/**
 * Generate a deterministic random gradient based on a ID
 */
export function getGradientForId(
  id: string = '',
  theme: Theme = 'dark',
  degress: number = 135
): string {
  const first = id.slice(0, 6);
  const second = id.slice(Math.max(id.length - 6, 0));
  const color1 = getColorForId(first, theme);
  const color2 = getColorForId(second, theme);
  return `linear-gradient(${degress}deg, ${color1}, ${color2})`;
}
