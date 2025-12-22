const _mask24 = (1 << 24) - 1;
type Theme = 'light' | 'dark';

function buildHex(code: number, start = 0x09, stop = 0x3f): string {
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

function buildGradient(code1: number, code2: number, theme: Theme): string {
  const start = theme === 'dark' ? 0x09 : 0xcf;
  const stop = theme === 'dark' ? 0x3f : 0xf5;
  const color1 = buildHex(code1, start, stop);
  const color2 = buildHex(code2, start, stop);
  return `linear-gradient(135deg, ${color1}, ${color2})`;
}

/**
 * Get a random gradient (non-deterministic)
 */
export function getRandomGradient(theme: Theme = 'dark'): string {
  const code1 = Math.floor(Math.random() * (_mask24 + 1));
  const code2 = Math.floor(Math.random() * (_mask24 + 1));
  return buildGradient(code1, code2, theme);
}

/**
 * Generate a deterministic random gradient based on a ID
 */
export function getGradientForId(
  id: string = '',
  theme: Theme = 'dark'
): string {
  let code1 = _mask24;
  for (let i = 0; i < 6; ++i) {
    const c = id.charCodeAt(i % id.length);
    code1 ^= (code1 << 4) ^ c;
    code1 ^= code1 >>> 24;
    code1 = code1 << 4;
  }
  let code2 = code1;
  for (let i = 6; i < 12; ++i) {
    const c = id.charCodeAt(i % id.length);
    code2 ^= (code2 << 4) ^ c;
    code2 ^= code2 >>> 24;
    code2 = code2 << 4;
  }
  return buildGradient(code1, code2, theme);
}
