import {
  acceptHMRUpdate,
  defineStore,
} from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: undefined as string | undefined,
  }),
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot));
}
