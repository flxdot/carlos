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
  ChartTypeRegistry,
  ScaleOptionsByType,
} from 'chart.js';
import ChartBase from '@/components/charts/chart-base.vue';
import {
  Timeseries,
} from '@/components/charts/chart-types.ts';
import {
  borderColor,
  Gradient,
  ColorStop, setConstantTicks,
} from '@/components/charts/chart-utils.ts';
import {
  tempEmojis,
  humidEmojis,
} from '@/utils/value-render.ts';

const props = defineProps<{temperature: Timeseries, humidity: Timeseries}>();

const tempColorStops: ColorStop[] = [
  {
    atValue: 10, // °C
    color: '#8ab6d6',
  },
  {
    atValue: 16, // °C
    color: '#a9d6e2',
  },
  {
    atValue: 26, // °C
    color: '#d5e8d4',
  },
  {
    atValue: 35, // °C
    color: '#f6d6c9',
  },
  {
    atValue: 40, // °C
    color: '#f29595',
  },
];
const tempGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempYLimit = [
  0,
  40,
] as [number, number];

const humidColorStops: ColorStop[] = [
  {
    atValue: 0, // %
    color: '#f29595',
  },
  {
    atValue: 25, // %
    color: '#f29595',
  },
  {
    atValue: 30, // %
    color: '#d5e8d4',
  },
  {
    atValue: 67, // %
    color: '#d5e8d4',
  },
  {
    atValue: 75, // %
    color: '#8ab6d6',
  },
  {
    atValue: 100, // %
    color: '#8ab6d6',
  },
];
const humidGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidYLimit = [
  0,
  100,
] as [number, number];

const chartData = computed(() => {
  return {
    datasets: [
      {
        label: 'Temperature',
        data: props.temperature.timestamps.map((timestamp, index) => ({
          x: timestamp,
          y: props.temperature.values[index],
        })),
        borderColor: borderColor(tempGradient.value, tempYLimit, tempColorStops),
        pointStyle: false,
        yAxisID: 'temp',
      },
      {
        label: 'Humidity',
        data: props.humidity.timestamps.map((timestamp, index) => ({
          x: timestamp,
          y: props.humidity.values[index],
        })),
        borderColor: borderColor(humidGradient.value, humidYLimit, humidColorStops),
        borderDash: [
          2,
          4,
        ],
        pointStyle: false,
        yAxisID: 'humid',
      },
    ],
  };
});

// Tomatoes: Tomatoes prefer temperatures between 70°F to 85°F (21°C to 29°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night for optimal growth and fruit production.
// Peppers (Paprika): Peppers, including paprika, also prefer temperatures similar to tomatoes. They grow best in temperatures around 70°F to 85°F (21°C to 29°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night.
// Zucchini: Zucchini plants prefer slightly warmer temperatures compared to tomatoes and peppers. They grow best in temperatures around 70°F to 90°F (21°C to 32°C) during the day and slightly cooler temperatures around 60°F to 70°F (15°C to 21°C) during the night.

const yAxes: { [p: string]: ScaleOptionsByType<ChartTypeRegistry['line']['scales']> } = {
  temp: {
    type: 'linear',
    display: true,
    position: 'left',
    title: {
      display: true,
      text: 'Temperature in °C',
    },
    min: tempYLimit[0],
    max: tempYLimit[1],
    ticks: {
      callback: (value: number) => `${tempEmojis(value)} ${value} °C`,
    },
    afterBuildTicks: setConstantTicks([
      0,
      10,
      20,
      30,
      40,
    ]),
  },
  humid: {
    type: 'linear',
    display: true,
    position: 'right',
    title: {
      display: true,
      text: 'Humidity in %',
    },
    min: humidYLimit[0],
    max: humidYLimit[1],
    ticks: {
      callback: (value: number) => `${humidEmojis(value)} ${value} %`,
    },
    afterBuildTicks: setConstantTicks([
      0,
      25,
      50,
      75,
      100,
    ]),
  },
};

</script>
