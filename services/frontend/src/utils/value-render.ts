export function renderNumber(value: number | undefined | null): string {
  if (value !== undefined && value !== null) {
    return value.toFixed(1);
  }
  return '-';
}

export function tempEmojis(temp: number): string {
  if (temp <= 0) {
    return '❄️';
  }
  if (temp < 10) {
    return '🥶';
  }
  if (temp < 15) {
    return '😨';
  }
  if (temp < 21) {
    return '😬';
  }
  if (temp < 32) {
    return '😊';
  }
  if (temp < 35) {
    return '🫠';
  }
  return '🥵';
}

export function humidEmojis(humid: number): string {
  if (humid < 10) {
    return '🔥';
  }
  if (humid < 30) {
    return '🌵';
  }
  if (humid <= 70) {
    return '👌';
  }
  if (humid <= 90) {
    return '🌴';
  }
  return '💦';
}
