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
        <skeleton
          v-if="deviceDetails === undefined"
          height="1.875rem"
        />
        <div
          v-else
          class="card-title"
        >
          <device-status-badge
            v-if="deviceDetails !== undefined"
            :device="deviceDetails"
          />
          <span>{{ deviceDetails?.displayName }}</span>
        </div>
      </template>
      <template #content>
        <skeleton
          v-if="deviceDetails === undefined"
        />
        <markdown-text
          v-else
          :content="deviceDetails?.description || ''"
        />
      </template>
    </card>
    <card class="device-card">
      <template #title>
        <div class="card-title">
          <span>{{ renderTimeseriesAsString(temperatureTs, tempEmojis) }}</span>
          <span>{{ renderTimeseriesAsString(humidityTs, humidEmojis) }}</span>
          <span
            v-tooltip="lastDataAt !== undefined ? lastDataAt.format('lll') : ''"
            class="card-title__sub"
          >{{ dataAge }}</span>
        </div>
      </template>
      <template #content>
        <message
          severity="def"
          :closable="false"
          style="margin-top: 0"
        >
          {{ i18n.global.t('device.warning.dummyData') }}
        </message>
        <chart-temp-humi
          :temperature="temperatureTs"
          :humidity="humidityTs"
        />
        <chart-temp-humi-two
          :temperature="temperatureTs"
          :humidity="humidityTs"
        />
        <chart-temp
          :temperature="temperatureTs"
        />
        <chart-humi
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
  onBeforeUnmount, computed,
} from 'vue';
import {
  useRoute,
} from 'vue-router';
import Card from 'primevue/card';
import Message from 'primevue/message';
import Skeleton from 'primevue/skeleton';
import dayjs, {
  Dayjs,
} from 'dayjs';
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
  ITimeseries,
} from '@/components/charts/chart-types.ts';
import {
  generateChartTimestamps,
  generateSinWaveFromTimestamps,
} from '@/components/charts/chart-utils.ts';
import {
  tempEmojis,
  humidEmojis,
} from '@/utils/value-render.ts';
import MarkdownText from '@/components/markdown-text/markdown-text.vue';
import ChartTemp from '@/components/charts/chart-temp.vue';
import ChartHumi from '@/components/charts/chart-humi.vue';
import ChartTempHumiTwo from '@/components/charts/chart-temp-humi-two.vue';

const UPDATE_INTERVAL = 1000 * 60; // 1 minute
let intervalId: ReturnType<typeof setInterval>;

const route = useRoute();

const deviceDetails = ref<TGetDeviceDetailResponse | undefined>(undefined);

const temperatureTs = ref<ITimeseries>({
  label: 'Temperature',
  unitSymbol: '°C',
  timestamps: [],
  values: [],
});
const humidityTs = ref<ITimeseries>({
  label: 'Humidity',
  unitSymbol: '%',
  timestamps: [],
  values: [],
});

const lastDataAt = computed<Dayjs | undefined>(() => {
  const lastTempAt = temperatureTs.value.timestamps[temperatureTs.value.timestamps.length - 1];
  const lastHumidAt = humidityTs.value.timestamps[humidityTs.value.timestamps.length - 1];

  if (lastTempAt === undefined && lastHumidAt === undefined) {
    return undefined;
  }

  return dayjs.max(dayjs(lastTempAt), dayjs(lastHumidAt))!;
});

const dataAge = computed<string | undefined>(() => {
  if (lastDataAt.value === undefined) {
    return undefined;
  }

  return dayjs.duration(lastDataAt.value!.diff(dayjs())).humanize(true);
});

function renderTimeseriesAsString(ts: ITimeseries, suffix: ((num: number) => string) | undefined = undefined, showLabel: boolean = true): string {
  const value = ts.values[ts.values.length - 1];
  let rendered = `${value !== undefined ? value.toFixed(1) : '-'} ${ts.unitSymbol}`;

  if (suffix !== undefined) {
    rendered += ` ${suffix(value)}`;
  }
  if (showLabel) {
    rendered = `${ts.label}: ${rendered}`;
  }

  return rendered;
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
.p-card {
  background: var(--carlos-bg-color);
  color: var(--carlos-text-color);
}
.card-title {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;

  &__sub {
    font-size: 0.875rem;
    line-height: 1.25rem;
    font-weight: 400;
  }
}

@media only screen and (width <= 481px) {
  .card-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

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
