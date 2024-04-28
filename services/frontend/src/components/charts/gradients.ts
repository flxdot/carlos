import {
  ChartArea,
} from 'chart.js';
import Color from 'colorjs.io';

/**
 * Holds the calculated gradient for a chart.
 *
 * This is dpne to reduce the number of calculations needed to render the chart,
 * as the gradient is only needs to be changed in case the size of the chart changes.
 */
export interface GradientCache {
  chartWidth: number | undefined;
  chartHeight: number | undefined;
  gradient: CanvasGradient | undefined;
}

/**
 * Represents a single color stop in a gradient.
 *
 * @property position - The position of the color stop in the gradient.
 *    This is a value between 0 and 1.
 * @property color - The color of the color stop.
 */
export interface ColorStop {
  position: number,
  color: string,
}

export type GradientDefinition = ColorStop[];

/**
 * Converts a single color to a gradient definitions with two color stops at 0.0 and 1.0.
 *
 * @param color - The color to convert to a gradient.
 */
export function colorToColorStop(color: string): GradientDefinition {
  return [
    {
      position: 0.0,
      color,
    },
    {
      position: 1.0,
      color,
    },
  ];
}

/**
 * Difference to the ColorStop is that this gradient stop defines colors for actual
 * values of the graph.
 *
 * @property atValue - The value at which the color should be applied.
 * @property color - The color to apply at the value.
 */
export interface DiscreteColorStop {
  atValue: number,
  color: string,
}

export type DiscreteGradientDefinition = DiscreteColorStop[];

export function convertDiscreteToColorStops(
  discreteColorStops: DiscreteColorStop[],
  axisLimits: [number, number],
): GradientDefinition {
  return discreteColorStops.map((discreteColorStop) => ({
    position: (discreteColorStop.atValue - axisLimits[0]) / (axisLimits[1] - axisLimits[0]),
    color: discreteColorStop.color,
  }));
}

/**
 * Represents a single alpha stop in a gradient.
 *
 * @property position - The position of the alpha stop in the gradient.
 *    This is a value between 0 and 1.
 * @property alpha - The alpha of the alpha stop. This is a value between 0 and 1.
 */
export interface AlphaStop {
  position: number,
  alpha: number,
}

/**
 * Interpolates the alpha value for a given position based on the given alpha stops.
 *
 * @param alphaStops - The alpha stops to use for the interpolation.
 * @param position - The position to interpolate the alpha for.
 */
export function interpolateAlpha(alphaStops: AlphaStop[], position: number): number {
  if (alphaStops.length === 0) {
    throw new Error('Alpha stops array is empty');
  }
  if (alphaStops.length === 1) {
    return alphaStops[0].alpha;
  }

  alphaStops.sort((a, b) => a.position - b.position);
  const posCapped = Math.min(Math.max(position, 0), 1);

  if (posCapped <= alphaStops[0].position) {
    return alphaStops[0].alpha;
  }

  for (let i = 1; i < alphaStops.length; i++) {
    if (posCapped < alphaStops[i].position) {
      const m = (alphaStops[i].alpha - alphaStops[i - 1].alpha) / (alphaStops[i].position - alphaStops[i - 1].position);
      const x = (posCapped - alphaStops[i - 1].position);
      const b = alphaStops[i - 1].alpha;
      return (m * x) + b;
    }
  }

  return alphaStops[alphaStops.length - 1].alpha;
}

/**
 * Creates a new canvas gradient from the given color stops.
 *
 * @param ctx - The canvas rendering context.
 * @param chartArea - The area of the chart to apply the gradient to.
 * @param colorStops - The color stops to use for the gradient.
 * @param alphaStops - The alpha stops to use for the gradient.
 */
export function buildGradient(
  ctx: CanvasRenderingContext2D,
  chartArea: ChartArea,
  colorStops: GradientDefinition,
  alphaStops: AlphaStop[] = [],
): CanvasGradient {
  const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);

  for (const colorStop of colorStops) {
    const color = new Color(colorStop.color);
    if (alphaStops.length > 0) {
      color.alpha = interpolateAlpha(alphaStops, colorStop.position);
    }

    gradient.addColorStop(Math.min(Math.max(colorStop.position, 0), 1), color.toString({
      format: 'hex',
    }));
  }
  return gradient;
}

/**
 * A nice vivid gradient to be used for outdoor temperatures
 */
export const outdoorTemperatureGradientCelsius: DiscreteGradientDefinition = [
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

export const pastelHumidityGradient: DiscreteGradientDefinition = [
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

export const xTicksGradient: GradientDefinition = [
  {
    position: 0,
    color: '#64748b',
  },
  {
    position: 0.6,
    color: '#64748b',
  },
  {
    position: 0.9,
    color: '#1f2128',
  },
];

export const carlosPalettePrimary = colorToColorStop('#98b274');
export const carlosPaletteBrown = colorToColorStop('#f4fec1');
export const carlosPaletteSand = colorToColorStop('#f4d35e');
export const lineBackgroundFade: AlphaStop[] = [
  {
    position: 0.1,
    alpha: 0.0,
  },
  {
    position: 1.0,
    alpha: 0.5,
  },
];
