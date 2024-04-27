export interface Timeseries {
    label: string;
    unitSymbol?: string;
    timestamps: string[];
    values: number[];
}

export type AxisLimit = [number, number];
