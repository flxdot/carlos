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
 * Represents a single sample in a timeseries.
 *
 * @property x - The timestamp of the sample. Value needs to be representable by dayjs.
 * @property y - The value of the sample.
 */
export interface ITimeseriesSample {
    x: string;
    y: number;
}

/**
 * Defines a timeseries with all information required to render it.
 *
 * @property displayName - The name of the timeseries - this is used as the label plot.
 * @property unitSymbol - The unit symbol of the timeseries values. If undefined, no unit is displayed.
 * @property samples - The samples of the timeseries.
 * @property valueType - The type of values in the timeseries. This determines how the timeseries is rendered.
 */
export interface ITimeseries {
    displayName: string;
    unitSymbol?: string;
    samples: ITimeseriesSample[];
    valueType: ETimeseriesValueType;
}
