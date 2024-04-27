export function tempEmojis(temp: number): string {
  if (temp <= 0) {
    return '❄️';
  }
  if (temp <= 10) {
    return '🥶';
  }
  if (temp < 21) {
    return '😊';
  }
  if (temp < 32) {
    return '🌞';
  }
  return '🥵';
}

export function humidEmojis(humid: number): string {
  if (humid < 25) {
    return '🏜️';
  }
  if (humid < 30) {
    return '🌵';
  }
  if (humid <= 70) {
    return '🌳';
  }
  if (humid <= 75) {
    return '🌧️';
  }
  return '💧';
}