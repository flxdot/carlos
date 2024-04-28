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
    values: number[];
}

export interface ITimeseriesSample {
    x: string;
    y: number;
}

export function toChartJsData(timeseries: ITimeseries): ITimeseriesSample[] {
  return timeseries.timestamps.map(
    (timestamp, index) => ({
      x: timestamp,
      y: timeseries.values[index],
    }
    ),
  );
}
