import {
  TGetDeviceDetailPathParams,
  TGetDeviceDriversPathParams,
  TGetDeviceDriversSignalsPathParams,
} from '@/api/devices.ts';

export enum EOpenapiPath {
    DEVICES_LIST_GET = '/devices',
    DEVICES_GET_PUT_POST_DELETE = '/devices/{deviceId}',
    DEVICE_DRIVERS_GET = '/devices/{deviceId}/drivers',
    DEVICE_DRIVERS_SIGNALS_GET = '/devices/{deviceId}/drivers/{driverIdentifier}/signals',
}

export const pathFactory = {
  [EOpenapiPath.DEVICES_GET_PUT_POST_DELETE]: (path: TGetDeviceDetailPathParams) => `/devices/${path.deviceId}`,
  [EOpenapiPath.DEVICE_DRIVERS_GET]: (path: TGetDeviceDriversPathParams) => `/devices/${path.deviceId}/drivers`,
  [EOpenapiPath.DEVICE_DRIVERS_SIGNALS_GET]: (path: TGetDeviceDriversSignalsPathParams) => `/devices/${path.deviceId}/drivers/${path.driverIdentifier}/signals`,
};
