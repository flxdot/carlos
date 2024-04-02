<template>
  <div class="app">
    <page-header class="app__header" />
    <main class="app__main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import {
  RouterView,
} from 'vue-router';
import PageHeader from './components/main-layout/header.vue';
</script>

<style lang="scss">
@use '@/styles/font.scss';

.app {
  width: 100dvw;
  min-height: 100dvh;
  padding: 1.5rem;
  display: grid;
  gap: 1rem 0;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto 1fr;
  grid-template-areas:
    'header header'
    'navbar main';

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

  &__main {
    position: relative;
    grid-area: main;
    overflow: auto;
  }
}

// for mobile view
@media only screen and (width <= 481px) {

}

// for tablet view
@media only screen and (width <= 769px) {
  .app {
    padding: 0;
    gap: 0;

    &__header {
      border-radius: 0;
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
