<template>
  <chart
    type="line"
    :data="chartData"
    :options="chartOptions"
  />
</template>

<script setup lang="ts">
import Chart from 'primevue/chart';
import 'chartjs-adapter-dayjs-4/dist/chartjs-adapter-dayjs-4.esm';

import {
  computed,
} from 'vue';
import {
  ChartOptions,
  ChartData,
  ScaleOptionsByType,
  ChartTypeRegistry,
} from 'chart.js';

const props = defineProps<{
  chartData: ChartData,
  yAxes: { [p: string]: ScaleOptionsByType<ChartTypeRegistry['line']['scales']> },
}>();

const chartData = computed<ChartData>(() => props.chartData);
const chartOptions = computed<ChartOptions>(() => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue('--text-color');
  const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
  const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

  const xAxis: { [p: string]: ScaleOptionsByType<ChartTypeRegistry['line']['scales']> } = {
    x: {
      type: 'time',
      time: {
        unit: 'day',
      },
      ticks: {
        color: textColorSecondary,
      },
      grid: {
        color: surfaceBorder,
      },
    },
  };
  // explicitly set the color of the ticks and grid lines if not set in the props
  const yAxis: typeof props.yAxes = {};
  Object.keys(props.yAxes).forEach((key, index) => {
    yAxis[key] = {
      ...props.yAxes[key],
      ticks: {
        color: textColorSecondary,
      },
      grid: {
        drawOnChartArea: index === 0,
        color: surfaceBorder,
      },
    };
  });

  return {
    stacked: false,
    maintainAspectRatio: true,
    aspectRatio: 3,
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      ...xAxis,
      ...yAxis,
    },
  };
});

</script>
