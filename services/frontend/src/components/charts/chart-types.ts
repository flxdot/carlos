import {
  LinearScaleOptions,
  TimeScaleOptions,
  FillerControllerDatasetOptions,
  LineControllerDatasetOptions,
} from 'chart.js';
import {
  DeepPartial,
} from '@/utils/types.ts';

export type TAxisLimit = [number, number];

export type TLineAxisProps = { [p: string]: DeepPartial<LinearScaleOptions> };
export type TLineChartData = LineControllerDatasetOptions & FillerControllerDatasetOptions
export type TTimeAxisProps = { [p: string]: DeepPartial<TimeScaleOptions> };
