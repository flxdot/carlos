<template>
  <div>
    <div v-for="device in deviceStore.devicesList">
      <h1>{{ device.displayName }}</h1>
      <pre>{{ device }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  useDevicesStore,
} from '@/store/devices.ts';

const deviceStore = useDevicesStore();

</script>

<style scoped lang="scss">

</style>
