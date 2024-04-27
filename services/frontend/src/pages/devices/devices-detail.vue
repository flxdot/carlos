<template>
  <div class="container-group">
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
    <card>
      <template #content>
        <message
          severity="warn"
          :closable="false"
        >
          The shown data is for presentation pruposes only. The real data is not yet connected.
        </message>
        <chart-temp-humi
          :temperature="temperatureTs"
          :humidity="humidityTs"
        />
      </template>
    </card>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  onMounted,
  onBeforeUnmount,
} from 'vue';
import {
  useRoute,
} from 'vue-router';
import Card from 'primevue/card';
import Message from 'primevue/message';
import {
  getDeviceDetail, TGetDeviceDetailResponse,
} from '@/api/devices.ts';
import {
  ERouteName,
} from '@/router/route-name.ts';
import i18n from '@/plugins/i18n';
import DeviceStatusBadge from '@/components/device/device-status-badge.vue';
import ChartTempHumi from '@/components/charts/chart-temp-humi.vue';
import {
  Timeseries,
} from '@/components/charts/chart-types.ts';
import {
  generateChartTimestamps,
  generateSinWaveFromTimestamps,
} from '@/components/charts/chart-utils.ts';

const UPDATE_INTERVAL = 1000 * 60; // 1 minute
let intervalId: ReturnType<typeof setInterval>;

const route = useRoute();

const deviceDetails = ref<TGetDeviceDetailResponse | undefined>(undefined);

const temperatureTs = ref<Timeseries>({
  label: 'Temperature',
  unitSymbol: '°C',
  timestamps: [],
  values: [],
});
const humidityTs = ref<Timeseries>({
  label: 'Humidity',
  unitSymbol: '%',
  timestamps: [],
  values: [],
});

function updateDevice() {
  getDeviceDetail(
    {
      deviceId: route.params.deviceId as string,
    },
  ).then((response) => {
    deviceDetails.value = response.data;
  });
}

onMounted(() => {
  updateDevice();
  intervalId = setInterval(updateDevice, UPDATE_INTERVAL);

  const timestamps = generateChartTimestamps(7, 1);
  const temperature = generateSinWaveFromTimestamps(timestamps, 40, 20, 0);
  const humidity = generateSinWaveFromTimestamps(timestamps, 100, 50, 1);

  temperatureTs.value.timestamps = timestamps;
  temperatureTs.value.values = temperature;

  humidityTs.value.timestamps = timestamps;
  humidityTs.value.values = humidity;
});

onBeforeUnmount(() => {
  clearInterval(intervalId);
});

</script>

<style scoped lang="scss">

@media only screen and (width <= 769px) {
  .container-group {
    margin-top: 1rem;
  }

  .device-card {
    border-radius: 0;
    border: none;
  }

  .subnav-link {
    margin-left: 1rem;
  }
}
</style>
