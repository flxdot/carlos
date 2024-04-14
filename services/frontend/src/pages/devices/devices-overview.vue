<template>
  <card
    v-for="device in deviceStore.devicesList"
    :key="device.deviceId"
    class="device-card"
  >
    <template #title>
      <div class="input-group">
        <device-status-badge :device="device" />
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
            class=""
            @click="navigate"
          >
            <div class="input-group">
              <span>{{ device.displayName }}</span>
              <i class="pi pi-arrow-right" />
            </div>
          </a>
        </router-link>
      </div>
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
import DeviceStatusBadge from '@/components/device/device-status-badge.vue';

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
