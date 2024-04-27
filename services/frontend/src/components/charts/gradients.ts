import {
  ColorStop,
} from '@/components/charts/chart-utils.ts';

// Tomatoes: Tomatoes prefer temperatures between 70°F to 85°F (21°C to 29°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night for optimal growth and fruit production.
// Peppers (Paprika): Peppers, including paprika, also prefer temperatures similar to tomatoes. They grow best in temperatures around 70°F to 85°F (21°C to 29°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night.
// Zucchini: Zucchini plants prefer slightly warmer temperatures compared to tomatoes and peppers. They grow best in temperatures around 70°F to 90°F (21°C to 32°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night.
export const pastelTemperatureGradient: ColorStop[] = [
  {
    atValue: 10, // °C
    color: '#8ab6d6',
  },
  {
    atValue: 16, // °C
    color: '#a9d6e2',
  },
  {
    atValue: 26, // °C
    color: '#d5e8d4',
  },
  {
    atValue: 35, // °C
    color: '#f6d6c9',
  },
  {
    atValue: 40, // °C
    color: '#f29595',
  },
];

export const vividTemperatureGradient: ColorStop[] = [
  {
    atValue: -16, // °C
    color: '#366dea',
  },
  {
    atValue: -6, // °C
    color: '#56a2f5',
  },
  {
    atValue: 5, // °C
    color: '#7dcce1',
  },
  {
    atValue: 11, // °C
    color: '#8ad1c0',
  },
  {
    atValue: 16, // °C
    color: '#bccf71',
  },
  {
    atValue: 21, // °C
    color: '#f0ce47',
  },
  {
    atValue: 38, // °C
    color: '#c73e2f',
  },
  {
    atValue: 43, // °C
    color: '#ab3124',
  },
];

export const pastelHumidityGradient: ColorStop[] = [
  {
    atValue: 0, // %
    color: '#f29595',
  },
  {
    atValue: 30, // %
    color: '#d5e8d4',
  },
  {
    atValue: 70, // %
    color: '#d5e8d4',
  },
  {
    atValue: 100, // %
    color: '#8ab6d6',
  },
];

export const vividHumidityGradient: ColorStop[] = [
  {
    atValue: 0, // %
    color: '#56a2f5',
  },
  {
    atValue: 10, // %
    color: '#56a2f5',
  },
  {
    atValue: 30, // %
    color: '#65db7c',
  },
  {
    atValue: 70, // %
    color: '#65db7c',
  },
  {
    atValue: 90, // %
    color: '#f0ce47',
  },
  {
    atValue: 100, // %
    color: '#f0ce47',
  },
];

export const carlosPalettePrimary: ColorStop[] = [
  {
    atValue: 0,
    color: '#98b274',
  },
  {
    atValue: 40,
    color: '#98b274',
  },
];

const col = '#f0ce47';

export const carlosPaletteSand: ColorStop[] = [
  {
    atValue: 0,
    color: col,
  },
  {
    atValue: 100,
    color: col,
  },
];

export const carlosPaletteBrown: ColorStop[] = [
  {
    atValue: 0,
    color: '#7f7750',
  },
  {
    atValue: 100,
    color: '#7f7750',
  },
];
