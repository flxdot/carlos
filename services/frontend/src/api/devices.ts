import {
  AxiosResponse,
} from 'axios';
import {
  EOpenapiPath,
} from '@/api/paths.ts';
import {
  paths,
} from '@/api/openapi.ts';
import carlosApi from '@/api/axios.ts';

export type TGetDevicesListResponse = paths[EOpenapiPath.DEVICES_LIST_GET]['get']['responses']['200']['content']['application/json'];
export async function getDevicesList(abortSignal?: AbortSignal): Promise<AxiosResponse<TGetDevicesListResponse>> {
  return carlosApi.get(EOpenapiPath.DEVICES_LIST_GET, {
    signal: abortSignal,
  });
}
