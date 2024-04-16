<template>
  <device-overview
    v-for="device in deviceStore.devicesList"
    :key="device.deviceId"
    class="device-card"
    :device="device"
  />
</template>

<script setup lang="ts">
import {
  onBeforeUnmount, onMounted,
} from 'vue';
import {
  useDevicesStore,
} from '@/store/devices.ts';
import DeviceOverview from '@/components/device/device-overview.vue';

const deviceStore = useDevicesStore();

const UPDATE_INTERVAL = 1000 * 60; // 1 minute
let intervalId: ReturnType<typeof setInterval>;

function updateDevicesList() {
  deviceStore.fetchDevicesList(true);
}

onMounted(() => {
  updateDevicesList();
  intervalId = setInterval(updateDevicesList, UPDATE_INTERVAL);
});

onBeforeUnmount(() => {
  clearInterval(intervalId);
});

</script>

<style scoped lang="scss">

.device-card {
  margin-bottom: 1rem;
}

.device-card:last-child {
  margin-bottom: 0;
}

@media only screen and (width <= 769px) {
  .device-card {
    border-radius: 0;
    border: none;
    margin-bottom: 1rem;
  }
}
</style>
