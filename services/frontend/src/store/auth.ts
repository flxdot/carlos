import {
  acceptHMRUpdate,
  defineStore,
} from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null as string | null,
  }),
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot));
}
