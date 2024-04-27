import {
  ColorStop,
} from '@/components/charts/chart-utils.ts';

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
    atValue: 67, // %
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