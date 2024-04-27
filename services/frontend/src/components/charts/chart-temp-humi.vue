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
} from 'vue';
import {
  ChartArea,
  ChartTypeRegistry, ScaleOptionsByType, ScriptableChartContext,
} from 'chart.js';
import ChartBase from '@/components/charts/chart-base.vue';
import {
  Timeseries,
} from '@/components/charts/chart-types.ts';

const props = defineProps<{temperature: Timeseries, humidity: Timeseries}>();

const chartData = computed(() => {
  return {
    datasets: [
      {
        label: 'Temperature',
        data: props.temperature.timestamps.map((timestamp, index) => ({
          x: timestamp,
          y: props.temperature.values[index],
        })),
        borderColor(context: ScriptableChartContext) {
          const {
            ctx, chartArea,
          } = context.chart;

          if (!chartArea) {
          // This case happens on initial chart load
            return;
          }
          return getTemperatureGradient(ctx, chartArea);
        },
        pointStyle: false,
        yAxisID: 'temp',
      },
      {
        label: 'Humidity',
        data: props.humidity.timestamps.map((timestamp, index) => ({
          x: timestamp,
          y: props.humidity.values[index],
        })),
        borderColor(context: ScriptableChartContext) {
          const {
            ctx, chartArea,
          } = context.chart;

          if (!chartArea) {
          // This case happens on initial chart load
            return;
          }
          return getHumidityGradient(ctx, chartArea);
        },
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

let tempChartWidth: number | undefined;
let tempChartheight: number | undefined;
let tempGradient: CanvasGradient | undefined;
function getTemperatureGradient(ctx: CanvasRenderingContext2D, chartArea: ChartArea): CanvasGradient {
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;
  if (!tempGradient || tempChartWidth !== chartWidth || tempChartheight !== chartHeight) {
    // Create the gradient because this is either the first render
    // or the size of the chart has changed
    tempChartWidth = chartWidth;
    tempChartheight = chartHeight;
    tempGradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    tempGradient!.addColorStop(0.01, '#8ab6d6');
    tempGradient!.addColorStop(0.25, '#a9d6e2');
    tempGradient!.addColorStop(0.50, '#d5e8d4');
    tempGradient!.addColorStop(0.75, '#f6d6c9');
    tempGradient!.addColorStop(0.99, '#f29595');
    tempGradient!.addColorStop(1.00, '#f29595');
  }

  return tempGradient;
}

let humidChartWidth: number | undefined;
let humidChartheight: number | undefined;
let humidGradient: CanvasGradient | undefined;
function getHumidityGradient(ctx: CanvasRenderingContext2D, chartArea: ChartArea): CanvasGradient {
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;
  if (!humidGradient || humidChartWidth !== chartWidth || humidChartheight !== chartHeight) {
    // Create the gradient because this is either the first render
    // or the size of the chart has changed
    humidChartWidth = chartWidth;
    humidChartheight = chartHeight;
    humidGradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    humidGradient!.addColorStop(0.00, '#f29595');
    humidGradient!.addColorStop(0.25, '#f29595');
    humidGradient!.addColorStop(0.35, '#d5e8d4');
    humidGradient!.addColorStop(0.65, '#d5e8d4');
    humidGradient!.addColorStop(0.75, '#8ab6d6');
    humidGradient!.addColorStop(1.00, '#8ab6d6');
  }

  return humidGradient;
}

const yAxes: { [p: string]: ScaleOptionsByType<ChartTypeRegistry['line']['scales']> } = {
  temp: {
    type: 'linear',
    display: true,
    position: 'left',
    title: {
      display: true,
      text: 'Temperature in °C',
    },
    min: -5,
    max: 45,
    afterBuildTicks: (axis) => axis.ticks = [
      0,
      10,
      20,
      30,
      40,
    ].map((v) => ({
      value: v,
    })),
  },
  humid: {
    type: 'linear',
    display: true,
    position: 'right',
    title: {
      display: true,
      text: 'Humidity in %',
    },
    min: -12.5,
    max: 112.5,
    afterBuildTicks: (axis) => axis.ticks = [
      0,
      25,
      50,
      75,
      100,
    ].map((v) => ({
      value: v,
    })),
  },
};

</script>

<style scoped lang="scss">

</style>
