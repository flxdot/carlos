import {
  TGetDeviceDetailPathParams,
} from '@/api/devices.ts';

export enum EOpenapiPath {
    DEVICES_LIST_GET = '/devices',
    DEVICES_GET_PUT_POST_DELETE = '/devices/{deviceId}',
}

export const pathFactory = {
  [EOpenapiPath.DEVICES_GET_PUT_POST_DELETE]: (path: TGetDeviceDetailPathParams) => `/devices/${path.deviceId}`,
};
