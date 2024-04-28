import {
  expect, test,
} from 'vitest';
import Color from 'colorjs.io';
import {
  AlphaStop, ColorStop, convertDiscreteToColorStops, DiscreteColorStop,
  interpolateAlpha,
} from './gradients.ts';

interface InterpAlphaParams {
    alphaStops: AlphaStop[],
    position: number,
    expectedAlpha: number
}

test.each([
  {
    alphaStops: [
      {
        position: 0.2,
        alpha: 0.5,
      },
    ] as AlphaStop[],
    position: 0.1,
    expectedAlpha: 0.5,
  },
  {
    alphaStops: [
      {
        position: 0.2,
        alpha: 0.5,
      },
    ] as AlphaStop[],
    position: 0.6,
    expectedAlpha: 0.5,
  },
  {
    alphaStops: [
      {
        position: 0,
        alpha: 0,
      },
      {
        position: 1.0,
        alpha: 1.0,
      },
    ] as AlphaStop[],
    position: 0.6,
    expectedAlpha: 0.6,
  },
] as InterpAlphaParams[])('interpolateAlpha(%o)', (params) => {
  expect(interpolateAlpha(params.alphaStops, params.position)).toBe(params.expectedAlpha);
});

test('interpolateAlpha - empty alphaStops throws error', () => {
  expect(() => interpolateAlpha([], 0.5)).toThrowError('Alpha stops array is empty');
});

interface ConvertDiscreteToColorStopsParams {
    discreteColorStops: DiscreteColorStop[],
    axisLimits: [number, number],
    expectedColorStops: ColorStop[]
}

test.each([
  {
    discreteColorStops: [
      {
        atValue: 0.2,
        color: 'red',
      },
    ] as DiscreteColorStop[],
    axisLimits: [
      0,
      1,
    ],
    expectedColorStops: [
      {
        position: 0.2,
        color: 'red',
      },
    ] as ColorStop[],
  },
  {
    discreteColorStops: [
      {
        atValue: 0.2,
        color: 'red',
      },
    ] as DiscreteColorStop[],
    axisLimits: [
      0,
      0.5,
    ],
    expectedColorStops: [
      {
        position: 0.4,
        color: 'red',
      },
    ] as ColorStop[],
  },
  {
    discreteColorStops: [
      {
        atValue: 0.2,
        color: 'red',
      },
      {
        atValue: 0.8,
        color: 'blue',
      },
    ] as DiscreteColorStop[],
    axisLimits: [
      0,
      1,
    ],
    expectedColorStops: [
      {
        position: 0.2,
        color: 'red',
      },
      {
        position: 0.8,
        color: 'blue',
      },
    ] as ColorStop[],
  },
] as ConvertDiscreteToColorStopsParams[])('convertDiscreteToColorStops(%o)', (params) => {
  expect(convertDiscreteToColorStops(params.discreteColorStops, params.axisLimits)).toEqual(params.expectedColorStops);
});
