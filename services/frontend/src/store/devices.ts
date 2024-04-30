import {
  acceptHMRUpdate,
  defineStore,
} from 'pinia';
import {
  AxiosResponse,
} from 'axios';
import {
  getDeviceDrivers, getDeviceDriversSignals,
  getDevicesList,
  TGetDeviceDriversResponse,
  TGetDeviceDriversSignalsResponse,
  TGetDevicesListResponse,
} from '@/api/devices.ts';
import {
  asyncRequestActionList,
} from '@/api/request-helper.ts';

export const useDevicesStore = defineStore('devices', {
  state: () => ({
    devicesList: undefined as TGetDevicesListResponse | undefined,
    devicesListPromise: undefined as Promise<AxiosResponse<TGetDevicesListResponse>> | undefined,
    deviceDriverMap: new Map<string, TGetDeviceDriversResponse>(),
    deviceDriverMapPromise: new Map<string, Promise<AxiosResponse<TGetDeviceDriversResponse>> | undefined>(),
    deviceDriverSignalMap: new Map<string, Map<string, TGetDeviceDriversSignalsResponse>>(),
    deviceDriverSignalMapPromise: new Map<string, Map<string, Promise<AxiosResponse<TGetDeviceDriversSignalsResponse>> | undefined>>(),
  }),
  getters: {
    isDevicesListLoading: (state) => state.devicesListPromise !== undefined,
  },
  actions: {
    async fetchDevicesList(force: boolean = false) {
      return asyncRequestActionList({
        callback: () => getDevicesList(),
        list: this.devicesList,
        promise: this.devicesListPromise,
        setList: (data) => {
          this.devicesList = data;
        },
        setPromise: (promise) => {
          this.devicesListPromise = promise;
        },
        force,
      });
    },
    async fetchDeviceDrivers(deviceId: string, force: boolean = false) {
      return asyncRequestActionList({
        callback: () => getDeviceDrivers({
          deviceId,
        }),
        list: this.deviceDriverMap.get(deviceId),
        promise: this.deviceDriverMapPromise.get(deviceId),
        setList: (data) => {
          this.deviceDriverMap.set(deviceId, data);
        },
        setPromise: (promise) => {
          this.deviceDriverMapPromise.set(deviceId, promise);
        },
        force,
      });
    },
    async fetchDeviceDriverSignals(deviceId: string, driverIdentifier: string, force: boolean = false) {
      return asyncRequestActionList({
        callback: () => getDeviceDriversSignals({
          deviceId,
          driverIdentifier,
        }),
        list: this.deviceDriverSignalMap.get(deviceId)?.get(driverIdentifier),
        promise: this.deviceDriverSignalMapPromise.get(deviceId)?.get(driverIdentifier),
        setList: (data) => {
          if (!this.deviceDriverSignalMap.has(deviceId)) {
            this.deviceDriverSignalMap.set(deviceId, new Map());
          }
          this.deviceDriverSignalMap.get(deviceId)!.set(driverIdentifier, data);
        },
        setPromise: (promise) => {
          if (!this.deviceDriverSignalMapPromise.has(deviceId)) {
            this.deviceDriverSignalMapPromise.set(deviceId, new Map());
          }
          this.deviceDriverSignalMapPromise.get(deviceId)!.set(driverIdentifier, promise);
        },
        force,
      });
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useDevicesStore, import.meta.hot));
}
