<template>
  <card
    v-for="device in deviceStore.devicesList"
    :key="device.deviceId"
    class="device-card"
  >
    <template #title>
      <router-link
        v-slot="{ href, navigate }"
        :to="{
          name: ERouteName.DEVICES_DETAIL,
          params: {
            deviceId: device.deviceId,
          },
        }"
      >
        <a
          :href="href"
          title="Carlos"
          class="input-group"
          @click="navigate"
        >
          <span>{{ device.displayName }}</span>
          <i class="pi pi-arrow-right" />
        </a>
      </router-link>
    </template>
    <template #content>
      <pre>{{ device }}</pre>
    </template>
  </card>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
import {
  useDevicesStore,
} from '@/store/devices.ts';
import {
  ERouteName,
} from '@/router/route-name.ts';

const deviceStore = useDevicesStore();

</script>

<style scoped lang="scss">
@media only screen and (width <= 769px) {
  .device-card {
    border-radius: 0;
    border: none;
    margin-bottom: 1rem;
  }

  .device-card:last-child {
    margin-bottom: 0;
  }
}
</style>
