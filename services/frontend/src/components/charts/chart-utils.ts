import dayjs from 'dayjs';
import {
  ChartArea, Scale, ScriptableChartContext,
} from 'chart.js';
import {
  TAxisLimit, TLineAxisProps,
} from '@/components/charts/chart-types.ts';
import {
  getMediaCategory, MediaSize,
} from '@/utils/window.ts';
import i18n from '@/plugins/i18n';
import {
  buildGradient, convertDiscreteToColorStops, DiscreteGradientDefinition,
  GradientCache,
  GradientDefinition, lineBackgroundFade,
} from '@/components/charts/gradients.ts';
import {ITimeseries} from "@/components/charts/timeseries.ts";

export function generateChartTimestamps(days: number, minutesBetweenSamples: number): string[] {
  const timestamps: string[] = [];

  const currentDate: dayjs.Dayjs = dayjs();

  for (let i: number = 0; i < days; i++) {
    const date: dayjs.Dayjs = currentDate.subtract(i, 'day');

    for (let j: number = 0; j < (24 * 60) / minutesBetweenSamples; j++) {
      const timestamp: dayjs.Dayjs = date.subtract(j * minutesBetweenSamples, 'minute');

      const formattedTimestamp: string = timestamp.format('YYYY-MM-DDTHH:mm:ss');

      timestamps.push(formattedTimestamp);
    }
  }

  // Reverse the array to have the timestamps in ascending order
  return timestamps.reverse();
}

export function generateSinWaveFromTimestamps(timestamps: string[], amplitude: number = 1, offset: number = 0, phaseShift: number = 0, frequency: number = 1): number[] {
  const sinWave: number[] = [];

  const angularFrequency: number = 2 * Math.PI;

  // Loop through the provided timestamps
  const firstTimestamp: dayjs.Dayjs = dayjs(timestamps[0]);
  for (const timestamp of timestamps) {
    const date: dayjs.Dayjs = dayjs(timestamp);

    const days: number = date.diff(firstTimestamp) / (24 * 60 * 60 * 1000);

    const sineValue: number = offset + amplitude / 2 * Math.sin(angularFrequency * days * frequency + phaseShift);

    sinWave.push(sineValue);
  }

  return sinWave;
}

export function updateGradient(
  gradient: GradientCache,
  ctx: CanvasRenderingContext2D,
  chartArea: ChartArea,
  yLim: [number, number],
  colorStops: GradientDefinition | DiscreteGradientDefinition,
  alphaGradient: boolean = false,
): GradientCache {
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;

  // Create the gradient because this is either the first render or the size of the chart has changed
  if (!gradient.gradient || gradient.chartWidth !== chartWidth || gradient.chartHeight !== chartHeight) {
    /* eslint-disable no-param-reassign */
    gradient.chartWidth = chartWidth;
    gradient.chartHeight = chartHeight;

    if ('atValue' in colorStops[0]) {
      colorStops = convertDiscreteToColorStops(colorStops as DiscreteGradientDefinition, yLim);
    }

    gradient.gradient = buildGradient(
      ctx,
      chartArea,
      colorStops as GradientDefinition,
      alphaGradient ? lineBackgroundFade : [],
    );
  }

  return gradient;
}

export function chartJsGradient(
  gradient: GradientCache,
  yLim: [number, number],
  colorStops: GradientDefinition | DiscreteGradientDefinition,
  alphaGradient: boolean = false,
) {
  return (context: ScriptableChartContext) => {
    const {
      ctx, chartArea,
    } = context.chart;

    if (!chartArea) {
      // This case happens on initial chart load
      return undefined;
    }

    return updateGradient(
      gradient,
      ctx,
      chartArea,
      yLim,
      colorStops,
      alphaGradient,
    ).gradient;
  };
}

export function setConstantTicks(ticks: number[]) {
  return (axis: Scale) => {
    // eslint-disable-next-line no-param-reassign
    axis.ticks = ticks.map((v) => ({
      value: v,
    }));
  };
}

export function roundToNearestMultiple(value: number, n: number): number {
  return Math.sign(value) * Math.ceil(Math.abs(value / n)) * n;
}

export function getSuitableLimit(staticLimits: [number, number], values: number[], n: number = 5): [number, number] {
  if (values.length === 0) {
    return staticLimits;
  }
  return [
    // eslint-disable-next-line array-element-newline
    Math.min(staticLimits[0], roundToNearestMultiple(Math.min(...values), n)),
    Math.max(staticLimits[1], roundToNearestMultiple(Math.max(...values), n)),
  ];
}

export function toPoints(timeseries: ITimeseries): {x: string, y: number}[] {
  return timeseries.timestamps.map((timestamp, index) => ({
    x: timestamp,
    y: timeseries.values[index],
  }));
}

export function buildAxis(position: 'left' | 'right', timeseries: ITimeseries, limits: TAxisLimit, ticks: number[], tickPrefix: (arg0: number) => string): TLineAxisProps[string] {
  const mediaSize = getMediaCategory();

  return {
    // @ts-ignore - unsure why the types do not match
    type: 'linear',
    display: true,
    position,
    title: {
      display: mediaSize >= MediaSize.DESKTOP,
      text: i18n.global.t('data.labelWithUnit', {
        label: timeseries.label,
        unit: timeseries.unitSymbol,
      }),
    },
    min: limits[0],
    max: limits[1],
    ticks: {
      callback: (value: number) => {
        return `${value}`;
        if (mediaSize >= MediaSize.DESKTOP) {
          return `${tickPrefix(value)} ${value} ${timeseries.unitSymbol}`;
        }
        if (mediaSize >= MediaSize.TABLET) {
          return `${value} ${timeseries.unitSymbol}`;
        }
        return `${value}`;
      },
    },
    afterBuildTicks: setConstantTicks(ticks),
  };
}
