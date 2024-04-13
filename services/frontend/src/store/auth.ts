import {
  acceptHMRUpdate,
  defineStore,
} from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: undefined as string | undefined,
  }),
  getters: {
    isAuthenticated: (state) => state.token !== undefined,
  },
  actions: {
    setToken(token: string) {
      this.token = token;
    },
    clearToken() {
      this.token = undefined;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot));
}
