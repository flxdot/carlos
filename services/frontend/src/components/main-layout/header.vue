<template>
  <menubar
    :model="menuItems"
    class="menubar"
  >
    <template
      #start
    >
      <router-link
        v-slot="{ href, navigate }"
        :to="{
          name: ERouteName.HOME
        }"
        custom
      >
        <a
          :href="href"
          title="Carlos"
          @click="navigate"
        >
          <div class="logo">
            <img
              alt="logo"
              src="@/assets/carlos-logo-type-white.png"
            >
          </div>
        </a>
      </router-link>
    </template>
    <template #end>
      <prm-button
        text
        label="Login"
        @click="login"
      />
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
import PrmButton from 'primevue/button';
import {
  useAuth0,
} from '@auth0/auth0-vue';
import {
  ERouteName,
} from '@/router/route-name.ts';

const {
  loginWithRedirect,
} = useAuth0();
const menuItems = ref<MenuItem[]>([]);

function login() {
  loginWithRedirect();
}
</script>

<style scoped lang="scss">

.menubar {
  height: var(--header-height);
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

@media only screen and (width <= 769px) {
  .app {
    padding: 0;
  }
}

.p-button.p-button-text {
  color: var(--primary-color-text);
}
</style>
