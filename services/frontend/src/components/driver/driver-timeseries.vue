<template>
  <div
    :style="{
      display: 'flex',
      flexDirection: 'row',
      justifyContent: 'space-between',
    }"
  >
    <div>
      <div
        v-for="ts in signalTimeseries"
        :key="ts.displayName"
      >
        {{ renderTimeseries(ts, selectSuffix(ts)) }}
      </div>
    </div>
    <div>
      {{
        lastDataAt !== undefined
          ? dayjs.duration(lastDataAt.diff(dayjs())).humanize(true)
          : ''
      }}, {{ lastDataAt !== undefined ? lastDataAt.format('lll') : '' }}
    </div>
  </div>
  <chart-temp-humi
    v-if="rawData !== undefined && driver.driverIdentifier.startsWith('temp-humi')"
    :temperature="signalTimeseries.find((ts) => ts.displayName === 'temperature')!"
    :humidity="signalTimeseries.find((ts) => ts.displayName === 'humidity')!"
  />
  <div
    v-for="ts in signalTimeseries"
    v-else
    :key="ts.displayName"
  >
    <chart-analog
      v-if="ts.isVisibleOnDashboard"
      :timeseries="ts"
      :color="nextColor()"
    />
  </div>
</template>

<script setup lang="ts">
import {
  ref, defineProps, withDefaults, computed, watchEffect,
} from 'vue';
import dayjs, {
  Dayjs,
} from 'dayjs';
import {
  Duration,
} from 'dayjs/plugin/duration';
import {
  TimeUnit,
} from 'chart.js';
import {
  TGetDeviceDriversResponse,
  TGetDeviceDriversSignalsResponse,
} from '@/api/devices.ts';
import {
  getTimeseries, TGetTimeseriesQueryParams,
  TGetTimeseriesResponse,
} from '@/api/timeseries.ts';
import {
  getLastTimestamp,
  ITimeseries,
} from '@/components/charts/timeseries.ts';
import {
  UnitOfMeasurementSymbol,
} from '@/api/unit-of-measurement.ts';
import ChartTempHumi from '@/components/charts/chart-temp-humi.vue';
import ChartAnalog from '@/components/charts/chart-analog.vue';
import {
  nextColor,
} from '@/components/charts/chart-utils.ts';
import {
  humidEmojis,
  renderTimeseries, tempEmojis,
} from '@/utils/value-render.ts';

const props = withDefaults(defineProps<{
  driver: TGetDeviceDriversResponse[number],
  signalList: TGetDeviceDriversSignalsResponse,
  duration?: Duration,
}>(), {
  duration: dayjs.duration(7, 'days'),
});

const rawData = ref<TGetTimeseriesResponse | undefined>();

type LocalTs = (ITimeseries & {isVisibleOnDashboard: boolean})[];

const signalTimeseries = computed<LocalTs>(() => {
  const timeseries: LocalTs = [];

  if (rawData.value === undefined) {
    return timeseries;
  }

  for (const signal of props.signalList) {
    const tsData = rawData.value.find((data) => data.timeseriesId === signal.timeseriesId);

    const ts = {
      displayName: signal.displayName,
      unitSymbol: UnitOfMeasurementSymbol[signal.unitOfMeasurement],
      timestamps: tsData?.timestamps || [],
      values: tsData?.values || [],
      isVisibleOnDashboard: signal.isVisibleOnDashboard,
    };
    timeseries.push(ts);
  }

  return timeseries;
});

const lastDataAt = computed<Dayjs | undefined>(() => getLastTimestamp(signalTimeseries.value));
const xTickUnit = computed<TimeUnit>(() => {
  if (props.duration >= dayjs.duration(2, 'days')) {
    return 'day';
  }
  return 'hour';
});

function updateData() {
  const now = dayjs();

  const params: TGetTimeseriesQueryParams = {
    timeseriesId: props.signalList.map((signal) => signal.timeseriesId),
    endAtUtc: now.toISOString(),
    startAtUtc: now.subtract(props.duration).toISOString(),
  };
  getTimeseries(params).then((response) => {
    rawData.value = response.data;
  });
}

watchEffect(async () => updateData());

function selectSuffix(signal: ITimeseries) {
  if (props.driver.driverIdentifier.startsWith('temp-humi')) {
    if (signal.displayName === 'temperature') {
      return tempEmojis;
    }
    if (signal.displayName === 'humidity') {
      return humidEmojis;
    }
  }
  return undefined;
}

updateData();
</script>
