import {
  ITimeseries,
} from '@/components/charts/timeseries.ts';

export function renderNumber(value: number | undefined | null): string {
  if (value !== undefined && value !== null) {
    return value.toFixed(1);
  }
  return '-';
}

export function renderTimeseries(ts: ITimeseries, suffix: ((num: number) => string) | undefined = undefined, showLabel: boolean = true): string {
  const value = ts.values[ts.values.length - 1];
  let rendered = `${renderNumber(value)} ${ts.unitSymbol}`;

  if (suffix !== undefined && value !== null) {
    rendered += ` ${suffix(value)}`;
  }
  if (showLabel) {
    rendered = `${ts.displayName}: ${rendered}`;
  }

  return rendered;
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
