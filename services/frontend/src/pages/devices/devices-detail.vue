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
          style="margin: 0"
        >
          The shown data is for presentation pruposes only. The real data is not yet connected.
        </message>
        <div class="flex gap-4 p-4">
          <span>{{ renderTimeseriesAsString(temperatureTs, tempEmojis) }}</span>
          <span>{{ renderTimeseriesAsString(humidityTs, humidEmojis) }}</span>
        </div>
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
import {
  tempEmojis,
  humidEmojis,
} from '@/utils/value-render.ts';

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

function renderTimeseriesAsString(ts: Timeseries, suffix: (num: number) => string): string {
  const value = ts.values[ts.values.length - 1];
  return `${ts.label}: ${value !== undefined ? value.toFixed(1) : '-'} ${ts.unitSymbol} ${suffix(value)}`;
}

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

  // Some representative data to showcase the full spectrum of the chart
  const timestamps = generateChartTimestamps(7, 1);
  humidityTs.value.timestamps = timestamps;
  temperatureTs.value.timestamps = timestamps;

  const dailyTemp = generateSinWaveFromTimestamps(timestamps, 8, 0, 0);
  const weeklyTemp = generateSinWaveFromTimestamps(timestamps, 32, 20, 1, 1 / 7);
  temperatureTs.value.values = dailyTemp.map((daily, index) => daily + weeklyTemp[index]);

  const dailyHumid = generateSinWaveFromTimestamps(timestamps, 7.3, 0, 0);
  const weeklyHumid = generateSinWaveFromTimestamps(timestamps, 90, 50, 3, 1 / 7);
  humidityTs.value.values = dailyHumid.map((daily, index) => daily + weeklyHumid[index]);
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
