<template>
  <chart-base
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
import {
  LinearScaleOptions,
} from 'chart.js';
import ChartBase from '@/components/charts/chart-base.vue';
import {
  AxisLimit,
  Timeseries,
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

const props = defineProps<{temperature: Timeseries, humidity: Timeseries}>();

const tempGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempYLimit = computed<AxisLimit>(() => getSuitableLimit(tempLimits, props.temperature.values));

const humidGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidYLimit = computed<AxisLimit>(() => getSuitableLimit(humidityLimits, props.humidity.values));

const chartData = computed(() => {
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
  };
});

// Tomatoes: Tomatoes prefer temperatures between 70°F to 85°F (21°C to 29°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night for optimal growth and fruit production.
// Peppers (Paprika): Peppers, including paprika, also prefer temperatures similar to tomatoes. They grow best in temperatures around 70°F to 85°F (21°C to 29°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night.
// Zucchini: Zucchini plants prefer slightly warmer temperatures compared to tomatoes and peppers. They grow best in temperatures around 70°F to 90°F (21°C to 32°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night.

export type TAxis = { [p: string]: Partial<LinearScaleOptions> };

const yAxes = computed<TAxis>(() => {
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
  };
});

</script>
