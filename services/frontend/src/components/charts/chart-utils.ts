import dayjs from 'dayjs';
import {
  ChartArea, Scale, ScriptableChartContext,
} from 'chart.js';

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

export function generateSinWaveFromTimestamps(timestamps: string[], amplitude: number = 1, offset: number = 0, phaseShift: number = 0): number[] {
  const sinWave: number[] = [];

  const angularFrequency: number = 2 * Math.PI / 24;

  // Loop through the provided timestamps
  for (const timestamp of timestamps) {
    const date: dayjs.Dayjs = dayjs(timestamp);

    const timeHours: number = date.hour() + date.minute() / 60 + date.second() / 3600;

    const sineValue: number = offset + amplitude / 2 * Math.sin(angularFrequency * timeHours + phaseShift);

    sinWave.push(sineValue);
  }

  return sinWave;
}

export type Gradient = {
  chartWidth: number | undefined;
  chartHeight: number | undefined;
  gradient: CanvasGradient | undefined;
}

export type ColorStop = {
  atValue: number,
  color: string,
}

export function updateGradient(
  gradient: Gradient,
  ctx: CanvasRenderingContext2D,
  chartArea: ChartArea,
  yLim: [number, number],
  colorStops: ColorStop[],
): Gradient {
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;

  // Create the gradient because this is either the first render or the size of the chart has changed
  if (!gradient.gradient || gradient.chartWidth !== chartWidth || gradient.chartHeight !== chartHeight) {
    // eslint-disable-next-line no-param-reassign
    gradient.chartWidth = chartWidth;
    // eslint-disable-next-line no-param-reassign
    gradient.chartHeight = chartHeight;
    // eslint-disable-next-line no-param-reassign
    gradient.gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    for (const colorStop of colorStops) {
      const relativeY = (colorStop.atValue - yLim[0]) / (yLim[1] - yLim[0]);
      gradient.gradient.addColorStop(relativeY, colorStop.color);
    }
  }

  return gradient;
}

export function borderColor(gradient: Gradient, yLim: [number, number], colorStops: ColorStop[]) {
  return (context: ScriptableChartContext) => {
    const {
      ctx, chartArea,
    } = context.chart;

    if (!chartArea) {
      // This case happens on initial chart load
      return undefined;
    }

    return updateGradient(gradient, ctx, chartArea, yLim, colorStops).gradient;
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
