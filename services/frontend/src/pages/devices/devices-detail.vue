<template>
  <pre>{{ deviceDetails }}</pre>
</template>

<script setup lang="ts">
import {
  ref,
} from 'vue';
import {
  useRoute,
} from 'vue-router';
import {
  getDeviceDetail, TGetDeviceDetailResponse,
} from '@/api/devices.ts';

const route = useRoute();

const deviceDetails = ref<TGetDeviceDetailResponse | undefined>(undefined);

getDeviceDetail(
  {
    deviceId: route.params.deviceId as string,
  },
).then((response) => {
  deviceDetails.value = response.data;
});

</script>

<style scoped lang="scss">

</style>
