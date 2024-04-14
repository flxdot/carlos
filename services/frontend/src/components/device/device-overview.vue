<template>
  <card
    class="device-card"
  >
    <template #title>
      <div class="input-group">
        <device-status-badge :device="props.device" />
        <router-link
          v-slot="{ href, navigate }"
          :to="{
            name: ERouteName.DEVICES_DETAIL,
            params: {
              deviceId: props.device.deviceId,
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
              <span>{{ props.device.displayName }}</span>
              <i class="pi pi-arrow-right" />
            </div>
          </a>
        </router-link>
      </div>
    </template>
    <template #content>
      <pre>{{ props.device }}</pre>
    </template>
  </card>
</template>

<script setup lang="ts">
import {
  defineProps,
} from 'vue';
import Card from 'primevue/card';
import {
  ERouteName,
} from '@/router/route-name.ts';

import DeviceStatusBadge from '@/components/device/device-status-badge.vue';
import {
  TGetDevicesListResponse,
} from '@/api/devices.ts';

const props = defineProps<{
  device: TGetDevicesListResponse[number]
}>();

</script>
