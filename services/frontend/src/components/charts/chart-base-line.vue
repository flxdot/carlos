<template>
  <chart
    type="line"
    :data="chartData"
    :options="chartOptions"
    :style="{ height: props.height || '20rem' }"
  />
</template>

<script setup lang="ts">
import Chart from 'primevue/chart';

import {
  computed,
} from 'vue';
import {
  ChartOptions,
} from 'chart.js';
import {
  deepUnion,
} from '@/utils/object.ts';
import {
  TLineAxisProps,
  TLineChartData,
  TTimeAxisProps,
} from '@/components/charts/chart-types.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';

const props = defineProps<{
  chartData: DeepPartial<TLineChartData>,
  yAxes: TLineAxisProps,
  height?: string,
}>();

const chartData = computed<DeepPartial<TLineChartData>>(() => props.chartData);
const chartOptions = computed<DeepPartial<ChartOptions>>(() => {
  const documentStyle = getComputedStyle(document.documentElement);
  const color = documentStyle.getPropertyValue('--text-color-secondary');
  const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

  const xAxis: TTimeAxisProps = {
    x: {
      // @ts-ignore - unsure why the types do not match
      type: 'time',
      time: {
        unit: 'day',
      },
      ticks: {
        display: false,
        color,
      },
      border: {
        display: false,
        color,
      },
      grid: {
        display: true,
        drawOnChartArea: true,
        drawTicks: true,
        color,
        tickColor: color,
      },
    },
  };
  // explicitly set the color of the ticks and grid lines if not set in the props
  const yAxis: TLineAxisProps = {};
  Object.keys(props.yAxes).forEach((key, index) => {
    const yAxisOverwrite: TLineAxisProps[string] = {
      title: {
        display: false,
        color,
      },
      ticks: {
        display: true,
        color,
      },
      border: {
        display: false,
        color,
      },
      grid: {
        display: false,
        drawOnChartArea: true,
        drawTicks: true,
        color,
        tickColor: color,
      },
    };

    yAxis[key] = deepUnion(props.yAxes[key], yAxisOverwrite);
  });

  return {
    stacked: false,
    maintainAspectRatio: false,
    aspectRatio: 3,
    animation: {
      duration: 0,
    },
    layout: {
      padding: 0,
    },
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
