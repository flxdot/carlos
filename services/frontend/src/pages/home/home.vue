<template>
  <fancy-panel
    class="home-container"
  >
    <div class="welcome">
      <h1 style="font-weight: 200;">
        Welcome to
      </h1>
      <img
        src="@/assets/carlos-logo-type-white.png"
        alt="Carlos"
        class="logo"
      >
      <p style="font-weight: 600;">
        Your friendly greenhouse manager.
      </p>
    </div>
  </fancy-panel>
</template>

<script setup lang="ts">
import {
  useRouter,
} from 'vue-router';
import FancyPanel from '@/components/containers/fancy-panel.vue';
import {
  useDevicesStore,
} from '@/store/devices.ts';
import {
  ERouteName,
} from '@/router/route-name.ts';

const router = useRouter();
const devicesStore = useDevicesStore();

devicesStore.$subscribe(() => {
  if (devicesStore.devicesList) {
    if (devicesStore.devicesList.length === 1) {
      router.push({
        name: ERouteName.DEVICES_DETAIL,
        params: {
          deviceId: devicesStore.devicesList[0].deviceId,
        },
      });
    } else {
      router.push({
        name: ERouteName.DEVICES_OVERVIEW,
      });
    }
  }
});

</script>

<style scoped lang="scss">

.home-container {
  --padding: 48px;

  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.welcome {
  margin-left: -20%;
  display: flex;
  gap: 1rem;
  flex-flow: column wrap;
}

.logo {
  width: 450px;
  height: auto;
}

@media only screen and (width <= 769px) {
  .welcome {
    margin: 0;
    align-items: flex-end;
  }

  .logo {
    width: 80%;
  }
}
</style>
