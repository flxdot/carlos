<template>
  <menubar :model="menuItems" class="menubar">
    <template
      #start
    >
      <div class="logo">
        <img
          alt="logo"
          src="@/assets/logo-type-white.png"
        >
      </div>
    </template>
  </menubar>
</template>

<script setup lang="ts">
import {
  ref,
} from 'vue';
import Menubar from 'primevue/menubar';
import {
  MenuItem,
} from 'primevue/menuitem';

const menuItems: MenuItem[] = ref([]);
</script>


<style scoped lang="scss">

.menubar {
  height: 48px;
  background-color: var(--primary-color);
  border: none;
  color: var(--primary-color-text);
}

.logo {
  display: flex;
  align-items: center;
}

.logo > img {
  height: 1.2rem;
  width: auto;
  margin-left: 0.5rem;
  margin-right: 1rem;
}
</style>
