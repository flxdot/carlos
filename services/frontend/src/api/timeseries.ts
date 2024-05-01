import {
  AxiosResponse,
} from 'axios';
import {
  paths,
} from '@/api/openapi.ts';
import {
  EOpenapiPath,
} from '@/api/paths.ts';
import carlosApi from '@/api/axios.ts';

export type TGetTimeseriesResponse = paths[EOpenapiPath.TIMESERIES_GET]['get']['responses']['200']['content']['application/json'];
export type TGetTimeseriesQueryParams = paths[EOpenapiPath.TIMESERIES_GET]['get']['parameters']['query'];
export async function getTimeseries(params: TGetTimeseriesQueryParams, abortSignal?: AbortSignal): Promise<AxiosResponse<TGetTimeseriesResponse>> {
  return carlosApi.get(EOpenapiPath.TIMESERIES_GET, {
    params,
    signal: abortSignal,
  });
}
