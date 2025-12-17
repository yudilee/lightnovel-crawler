/**
 * Predefined beautiful gradient combinations
 */
const gradients = [
  'linear-gradient(135deg, #232526 0%, #414345 100%)',
  'linear-gradient(135deg, #0f2027 0%, #2c5364 100%)',
  'linear-gradient(135deg, #1e130c 0%, #9a8478 100%)',
  'linear-gradient(135deg, #232526 0%, #3a3a3a 100%)',
  'linear-gradient(135deg, #434343 0%, #000000 100%)',
  'linear-gradient(135deg, #141e30 0%, #243b55 100%)',
  'linear-gradient(135deg, #283e51 0%, #485563 100%)',
  'linear-gradient(135deg, #485563 0%, #29323c 100%)',
  'linear-gradient(135deg, #232526 0%, #302b63 100%)',
  'linear-gradient(135deg, #000428 0%, #004e92 100%)',
  'linear-gradient(135deg, #232526 0%, #232526 100%)',
  'linear-gradient(135deg, #093028 0%, #237a57 100%)',
  'linear-gradient(135deg, #2C3E50 0%, #4CA1AF 100%)',
  'linear-gradient(135deg, #1a2980 0%, #026485 100%)',
  'linear-gradient(135deg, #232526 0%, #1a1a2e 100%)',
  'linear-gradient(135deg, #1D4350 0%, #A43931 100%)',
  'linear-gradient(135deg, #000000 0%, #4b6cb7 100%)',
  'linear-gradient(135deg, #232526 0%, #24243e 100%)',
  'linear-gradient(135deg, #141e30 0%, #35577d 100%)',
  'linear-gradient(135deg, #000000 0%, #434343 100%)',
];

/**
 * Generate a deterministic random gradient based on a ID
 */
export function getGradientForId(id: string): string {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    const char = id.charCodeAt(i);
    hash = (hash << 3) - hash + char;
    hash = hash & hash;
  }

  const index = Math.abs(hash) % gradients.length;
  return gradients[index];
}

/**
 * Get a random gradient (non-deterministic)
 */
export function getRandomGradient(): string {
  const index = Math.floor(Math.random() * gradients.length);
  return gradients[index];
}
