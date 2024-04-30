import {
  AxiosResponse,
} from 'axios';
import {
  EOpenapiPath, pathFactory,
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

export type TGetDeviceDetailResponse = paths[EOpenapiPath.DEVICES_GET_PUT_POST_DELETE]['get']['responses']['200']['content']['application/json'];
export type TGetDeviceDetailPathParams = paths[EOpenapiPath.DEVICES_GET_PUT_POST_DELETE]['get']['parameters']['path'];
export async function getDeviceDetail(path: TGetDeviceDetailPathParams, abortSignal?: AbortSignal): Promise<AxiosResponse<TGetDeviceDetailResponse>> {
  return carlosApi.get(pathFactory[EOpenapiPath.DEVICES_GET_PUT_POST_DELETE](path), {
    signal: abortSignal,
  });
}

export type TGetDeviceDriversPathParams = paths[EOpenapiPath.DEVICE_DRIVERS_GET]['get']['parameters']['path'];
export type TGetDeviceDriversResponse = paths[EOpenapiPath.DEVICE_DRIVERS_GET]['get']['responses']['200']['content']['application/json'];
export async function getDeviceDrivers(path: TGetDeviceDriversPathParams, abortSignal?: AbortSignal): Promise<AxiosResponse<TGetDeviceDriversResponse>> {
  return carlosApi.get(pathFactory[EOpenapiPath.DEVICE_DRIVERS_GET](path), {
    signal: abortSignal,
  });
}

export type TGetDeviceDriversSignalsPathParams = paths[EOpenapiPath.DEVICE_DRIVERS_SIGNALS_GET]['get']['parameters']['path'];
export type TGetDeviceDriversSignalsResponse = paths[EOpenapiPath.DEVICE_DRIVERS_SIGNALS_GET]['get']['responses']['200']['content']['application/json'];
export async function getDeviceDriversSignals(path: TGetDeviceDriversSignalsPathParams, abortSignal?: AbortSignal): Promise<AxiosResponse<TGetDeviceDriversSignalsResponse>> {
  return carlosApi.get(pathFactory[EOpenapiPath.DEVICE_DRIVERS_SIGNALS_GET](path), {
    signal: abortSignal,
  });
}
