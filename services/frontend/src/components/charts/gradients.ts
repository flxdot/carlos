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
    color: '#366DEA',
  },
  {
    atValue: -6, // °C
    color: '#56A2F5',
  },
  {
    atValue: 5, // °C
    color: '#7DCCE1',
  },
  {
    atValue: 11, // °C
    color: '#8AD1C0',
  },
  {
    atValue: 16, // °C
    color: '#BCCF71',
  },
  {
    atValue: 21, // °C
    color: '#F0CE47',
  },
  {
    atValue: 38, // °C
    color: '#C73E2F',
  },
  {
    atValue: 43, // °C
    color: '#AB3124',
  },
];

export const pastelHumidityGradient: ColorStop[] = [
  {
    atValue: 0, // %
    color: '#f29595',
  },
  {
    atValue: 25, // %
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
    atValue: 75, // %
    color: '#8ab6d6',
  },
  {
    atValue: 100, // %
    color: '#8ab6d6',
  },
];

export const vividHumidityGradient: ColorStop[] = [
  {
    atValue: 0, // %
    color: '#56A2F5',
  },
  {
    atValue: 10, // %
    color: '#56A2F5',
  },
  {
    atValue: 30, // %
    color: '#65DB7C',
  },
  {
    atValue: 70, // %
    color: '#65DB7C',
  },
  {
    atValue: 90, // %
    color: '#F0CE47',
  },
  {
    atValue: 100, // %
    color: '#F0CE47',
  },
];
