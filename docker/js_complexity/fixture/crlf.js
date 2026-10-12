export function clamp(value, max) {
  if (value > max) {
    return max;
  }
  return value;
}
