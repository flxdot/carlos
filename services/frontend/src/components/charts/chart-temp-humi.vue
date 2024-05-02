<template>
  <chart-base-line
    :chart-data="chartData"
    :y-axes="yAxes"
    height="20rem"
  />
</template>

<script setup lang="ts">
import {
  defineProps,
  computed,
  ref,
} from 'vue';
import ChartBaseLine from '@/components/charts/chart-base-line.vue';
import {
  TAxisLimit,
  TLineAxisProps, TLineChartData,
} from '@/components/charts/chart-types.ts';
import {
  chartJsGradient,
  getSuitableLimit,
  buildAxis,
  toPoints,
} from '@/components/charts/chart-utils.ts';
import {
  pastelHumidityGradient,
  outdoorTemperatureGradientCelsius, GradientCache,
} from '@/components/charts/gradients.ts';
import {
  humidEmojis, tempEmojis,
} from '@/utils/value-render.ts';
import {
  humidityLimits,
  humidityTicks, LineWidth,
  tempLimits,
  tempTicks,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';
import {
  ITimeseries,
} from '@/components/charts/timeseries.ts';

const props = defineProps<{temperature: ITimeseries, humidity: ITimeseries}>();

const tempGradient = ref<GradientCache>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempBgGradient = ref<GradientCache>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempYLimit = computed<TAxisLimit>(() => getSuitableLimit(tempLimits, props.temperature.values));

const humidGradient = ref<GradientCache>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidBgGradient = ref<GradientCache>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidYLimit = computed<TAxisLimit>(() => getSuitableLimit(humidityLimits, props.humidity.values));

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  const tempColor = chartJsGradient(tempGradient.value, outdoorTemperatureGradientCelsius, tempYLimit.value);
  const tempBgColor = chartJsGradient(tempBgGradient.value, outdoorTemperatureGradientCelsius, tempYLimit.value, true);
  const humidColor = chartJsGradient(humidGradient.value, pastelHumidityGradient, humidYLimit.value);
  const humidBgColor = chartJsGradient(humidBgGradient.value, pastelHumidityGradient, humidYLimit.value, true);

  return {
    datasets: [
      {
        label: 'Temperature',
        data: toPoints(props.temperature),
        borderWidth: LineWidth,
        borderColor: tempColor,
        backgroundColor: tempBgColor,
        pointHoverBackgroundColor: tempColor,
        pointHoverRadius: 5,
        pointRadius: 0,
        fill: true,
        pointStyle: false,
        yAxisID: 'temp',
        // The tension helps to smooth the line in case of oversampling
        tension: 0.1,
      },
      {
        label: 'Humidity',
        data: toPoints(props.humidity),
        borderWidth: LineWidth,
        borderColor: humidColor,
        backgroundColor: humidBgColor,
        fill: true,
        pointStyle: false,
        yAxisID: 'humid',
        // The tension helps to smooth the line in case of oversampling
        tension: 0.1,
      },
    ],
  } as DeepPartial<TLineChartData>;
});

const yAxes = computed<TLineAxisProps>(() => {
  return {
    temp: buildAxis('left', props.temperature, tempYLimit.value, tempTicks, tempEmojis),
    humid: buildAxis('right', props.humidity, humidYLimit.value, humidityTicks, humidEmojis),
  } as TLineAxisProps;
});

</script>
