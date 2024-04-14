<template>
  <div>
    <!-- The current route is accessible as $route in the template -->
    User {{ route.params.id }}
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
    device_id: route.params.id,
  },
);

</script>

<style scoped lang="scss">

</style>
