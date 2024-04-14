<template>
  <div class="app">
    <page-header class="app__header" />
    <main class="app__main">
      <router-view />
    </main>
    <page-footer class="app__footer" />
  </div>
</template>

<script setup lang="ts">
import {
  watch,
} from 'vue';
import {
  RouterView,
} from 'vue-router';
import {
  useAuth0,
} from '@auth0/auth0-vue';
import PageHeader from './components/main-layout/header.vue';
import PageFooter from './components/main-layout/footer.vue';
import {
  useAuthStore,
} from '@/store/auth.ts';
import {
  setToken,
} from '@/api/axios.ts';

const authStore = useAuthStore();

const {
  isAuthenticated,
  isLoading,
  getAccessTokenSilently,
} = useAuth0();

watch([
  isAuthenticated,
  isLoading,
], async ([
  newIsAuthenticate,
  newIsLoading,
]) => {
  if (newIsAuthenticate && !newIsLoading) {
    authStore.setToken(await getAccessTokenSilently());
  } else {
    authStore.clearToken();
  }
  setToken(authStore.token);
});

</script>

<style lang="scss">
@use '@/styles/font.scss';

.app {
  width: 100dvw;
  min-height: 100dvh;
  padding: calc(1.5rem + env(safe-area-inset-top)) calc(1.5rem + env(safe-area-inset-right)) calc(1.5rem + env(safe-area-inset-bottom)) calc(1.5rem + env(safe-area-inset-left));
  display: grid;
  gap: 1rem 0;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto 1fr;
  /* stylelint-disable-next-line declaration-block-no-redundant-longhand-properties */
  grid-template-areas:
    'header header'
    'navbar main'
    'footer footer';

  &__navbar {
    grid-area: navbar;
    max-height: calc(100dvh - var(--navbar-header-height, 0));
    position: sticky;
    top: var(--navbar-header-height, 0);
  }

  &__header {
    position: sticky;
    top: 0;
    grid-area: header;
  }

  &__footer {
    grid-area: footer;
    bottom: 0;
  }

  &__main {
    grid-area: main;
    overflow: auto;
  }
}

// for mobile view
// @media only screen and (width <= 481px) {
// }

// for tablet view
@media only screen and (width <= 769px) {
  .app {
    padding: 0;
    gap: 0;

    &__header {
      border-radius: 0;
    }

    &__footer {
      margin: 1rem 0 env(safe-area-inset-bottom);
    }
  }
}

@media only screen and (width > 1249px) {
  .app {
    max-width: 1250px;
    margin: 0 auto;
  }
}

</style>
