<template>
  <div>
    <!-- The current route is accessible as $route in the template -->
    User {{ route.params.deviceId }}
  </div>
</template>

<script setup lang="ts">
import {
  useRoute,
} from 'vue-router';
import {
  getDeviceDetail,
} from '@/api/devices.ts';

const route = useRoute();

const deviceDetails = getDeviceDetail(
  {
    deviceId: route.params.deviceId,
  },
);

</script>

<style scoped lang="scss">

</style>
