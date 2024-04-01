<template>
  <menubar :model="menuItems" class="menubar">
    <template
      #start
    >
      <div class="logo">
        <img
          alt="logo"
          src="@/assets/logo.png"
        >
        <p>Carlos</p>
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
  background-color: var(--primary-fg-color);
  color: var(--primary-bg-color);
}

.logo {
  display: flex;
  align-items: center;
}

.logo > p {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  margin-left: 1rem;
}

.logo > img {
  height: 2.5rem;
  width: auto;
  margin-left: 1rem;
}
</style>
