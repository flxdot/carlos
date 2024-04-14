<template>
  <div class="container-group mt-4">
    <router-link
      v-slot="{ href, navigate }"
      :to="{
        name: ERouteName.DEVICES_OVERVIEW,
      }"
    >
      <a
        :href="href"
        title="Carlos"
        class="input-group subnav-link"
        @click="navigate"
      >
        <i class="pi pi-arrow-left" />
        <span>{{ i18n.global.t(`pages.${ERouteName.DEVICES_OVERVIEW}`) }}</span>
      </a>
    </router-link>
    <card class="device-card">
      <template #title>
        <div class="input-group">
          <device-status-badge
            v-if="deviceDetails !== undefined"
            :device="deviceDetails"
          />
          <span>{{ deviceDetails?.displayName }}</span>
        </div>
      </template>
      <template #content>
        <pre>{{ deviceDetails }}</pre>
      </template>
    </card>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
} from 'vue';
import {
  useRoute,
} from 'vue-router';
import Card from 'primevue/card';
import {
  getDeviceDetail, TGetDeviceDetailResponse,
} from '@/api/devices.ts';
import {
  ERouteName,
} from '@/router/route-name.ts';
import i18n from '@/plugins/i18n';
import DeviceStatusBadge from '@/components/device/device-status-badge.vue';

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

@media only screen and (width <= 769px) {
  .device-card {
    border-radius: 0;
    border: none;
  }

  .subnav-link {
    margin-left: 1rem;
  }
}
</style>
