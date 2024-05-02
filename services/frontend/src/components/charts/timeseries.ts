import dayjs from 'dayjs';
import {
  notEmpty,
} from '@/utils/filters.ts';

/**
 * Determines the type of values of the timeseries.
 *
 * - `ANALOG` - The timeseries contains continuous analog values.
 * - `DISCRETE` - The timeseries contains discrete values. Changes the chart to a step chart.
 * - `BOOLEAN` - Special case of discrete values where the values are either `0` or `1`.
 */
export enum ETimeseriesValueType {
    ANALOG = 'analog',
    DISCRETE = 'discrete',
    BOOLEAN = 'boolean',
}

/**
 * Defines a timeseries with all information required to render it.
 *
 * @property displayName - The name of the timeseries - this is used as the label plot.
 * @property unitSymbol - The unit symbol of the timeseries values. If undefined, no unit is displayed.
 * @property samples - The samples of the timeseries.
 */
export interface ITimeseries {
    displayName: string;
    unitSymbol?: string;
    timestamps: string[];
    values: (number | null)[];
}

export interface ITimeseriesSample {
    x: string;
    y: number | undefined;
}

export function toChartJsData(timeseries: ITimeseries): ITimeseriesSample[] {
  return timeseries.values.filter(notEmpty).map(
    (value, index) => ({
      x: timeseries.timestamps[index],
      y: value,
    }
    ),
  );
}

export function getLastTimestamp(timeseries: ITimeseries[]) {
  const lastDataAt = dayjs.max(timeseries
    .map((ts) => ts.timestamps[ts.timestamps.length - 1])
    .map((ts) => dayjs(ts)));
  if (lastDataAt === null) {
    return undefined;
  }

  return lastDataAt;
}
