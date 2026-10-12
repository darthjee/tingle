export function clamp(value: number, max: number): number {
  if (value > max) {
    return max;
  }
  return value;
}
