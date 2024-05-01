<template>
</template>

<script setup lang="ts">

import {
  ref, defineProps, withDefaults,
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

const props = withDefaults(defineProps<{
  driver: TGetDeviceDriversResponse[number],
  signalList: TGetDeviceDriversSignalsResponse,
  duration?: Duration,
}>(), {
  duration: dayjs.duration(7, 'days'),
});

const rawData = ref<TGetTimeseriesResponse>();

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

<style scoped lang="scss">

</style>
