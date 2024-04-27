<template>
  <chart-base-line
    :chart-data="chartData"
    :y-axes="yAxes"
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
  ITimeseries, TLineAxisProps, TLineChartData,
} from '@/components/charts/chart-types.ts';
import {
  borderColor,
  Gradient,
  getSuitableLimit, setConstantTicks,
} from '@/components/charts/chart-utils.ts';
import {
  pastelHumidityGradient,
  vividTemperatureGradient,
} from '@/components/charts/gradients.ts';
import {
  humidEmojis, tempEmojis,
} from '@/utils/value-render.ts';
import {
  humidityLimits,
  humidityTicks,
  tempLimits,
  tempTicks,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';

const props = defineProps<{temperature: ITimeseries, humidity: ITimeseries}>();

const tempGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempYLimit = computed<TAxisLimit>(() => getSuitableLimit(tempLimits, props.temperature.values));

const humidGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidYLimit = computed<TAxisLimit>(() => getSuitableLimit(humidityLimits, props.humidity.values));

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  const tempColor = borderColor(tempGradient.value, tempYLimit.value, vividTemperatureGradient);
  const humidColor = borderColor(humidGradient.value, humidYLimit.value, pastelHumidityGradient);

  return {
    datasets: [
      {
        label: 'Temperature',
        data: props.temperature.timestamps.map((timestamp, index) => ({
          x: timestamp,
          y: props.temperature.values[index],
        })),
        borderWidth: 2,
        backgroundColor: tempColor,
        borderColor: tempColor,
        pointStyle: false,
        yAxisID: 'temp',
      },
      {
        label: 'Humidity',
        data: props.humidity.timestamps.map((timestamp, index) => ({
          x: timestamp,
          y: props.humidity.values[index],
        })),
        borderWidth: 3,
        backgroundColor: humidColor,
        borderColor: humidColor,
        borderDash: [10, 10],
        pointStyle: false,
        yAxisID: 'humid',
      },
    ],
  } as DeepPartial<TLineChartData>;
});

const yAxes = computed<TLineAxisProps>(() => {
  const tempAxis = {
    type: 'linear',
    display: true,
    position: 'left',
    title: {
      display: true,
      text: 'Temperature in °C',
    },
    min: tempYLimit.value[0],
    max: tempYLimit.value[1],
    ticks: {
      callback: (value: number) => `${tempEmojis(value)} ${value} °C`,
    },
    afterBuildTicks: setConstantTicks(tempTicks),
  };

  const humidAxis = {
    type: 'linear',
    display: true,
    position: 'right',
    title: {
      display: true,
      text: 'Humidity in %',
    },
    min: humidYLimit.value[0],
    max: humidYLimit.value[1],
    ticks: {
      callback: (value: number) => `${humidEmojis(value)} ${value} %`,
    },
    afterBuildTicks: setConstantTicks(humidityTicks),
  };

  return {
    temp: tempAxis,
    humid: humidAxis,
  } as TLineAxisProps;
});

</script>
