import {
  acceptHMRUpdate,
  defineStore,
} from 'pinia';
import {
  AxiosResponse,
} from 'axios';
import {
  getDevicesList, TGetDevicesListResponse,
} from '@/api/devices.ts';
import {
  asyncRequestActionList,
} from '@/api/request-helper.ts';

export const useDevicesStore = defineStore('devices', {
  state: () => ({
    devicesList: undefined as TGetDevicesListResponse | undefined,
    devicesListPromise: undefined as Promise<AxiosResponse<TGetDevicesListResponse>> | undefined,
  }),
  getters: {
    isDevicesListLoading: (state) => state.devicesListPromise !== undefined,
  },
  actions: {
    async fetchDevicesList() {
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
      });
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useDevicesStore, import.meta.hot));
}
