<template>
  <div
    v-for="ts in signalTimeseries"
    :key="ts.displayName"
  >
    {{ ts.displayName }}: {{ renderNumber(ts.values[ts.values.length - 1]) }} {{ ts.unitSymbol }}
  </div>
  <chart-temp-humi
    v-if="driver.driverIdentifier.startsWith('temp-humi')"
    :temperature="signalTimeseries.find((ts) => ts.displayName === 'temperature')!"
    :humidity="signalTimeseries.find((ts) => ts.displayName === 'humidity')!"
  />
  <div
    v-for="ts in signalTimeseries"
    v-else
    :key="ts.displayName"
  >
    <chart-analog
      :timeseries="ts"
      :color="nextColor()"
    />
  </div>
</template>

<script setup lang="ts">
import {
  ref, defineProps, withDefaults, computed,
} from 'vue';
import dayjs from 'dayjs';
import {
  Duration,
} from 'dayjs/plugin/duration';
import {
  TGetDeviceDriversResponse,
  TGetDeviceDriversSignalsResponse,
} from '@/api/devices.ts';
import {
  getTimeseries, TGetTimeseriesQueryParams,
  TGetTimeseriesResponse,
} from '@/api/timeseries.ts';
import {
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
  renderNumber,
} from '@/utils/value-render.ts';

const props = withDefaults(defineProps<{
  driver: TGetDeviceDriversResponse[number],
  signalList: TGetDeviceDriversSignalsResponse,
  duration?: Duration,
}>(), {
  duration: dayjs.duration(7, 'days'),
});

const rawData = ref<TGetTimeseriesResponse | undefined>();

const signalTimeseries = computed<ITimeseries[]>(() => {
  const timeseries: ITimeseries[] = [];

  if (rawData.value === undefined) {
    return timeseries;
  }

  for (const signal of props.signalList) {
    const tsData = rawData.value.find((data) => data.timeseriesId === signal.timeseriesId);

    const ts: ITimeseries = {
      displayName: signal.displayName,
      unitSymbol: UnitOfMeasurementSymbol[signal.unitOfMeasurement],
      timestamps: tsData?.timestamps || [],
      values: tsData?.values || [],
    };
    timeseries.push(ts);
  }

  return timeseries;
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

updateData();
</script>
