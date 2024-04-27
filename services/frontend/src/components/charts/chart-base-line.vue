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
}>();

const chartData = computed<DeepPartial<TLineChartData>>(() => props.chartData);
const chartOptions = computed<DeepPartial<ChartOptions>>(() => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue('--text-color');
  const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
  const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

  const xAxis: TTimeAxisProps = {
    x: {
      // @ts-ignore - unsure why the types do not match
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
  const yAxis: TLineAxisProps = {};
  Object.keys(props.yAxes).forEach((key, index) => {
    const yAxisOverwrite: TLineAxisProps[string] = {
      title: {
        color: textColor,
      },
      ticks: {
        color: textColorSecondary,
      },
      grid: {
        drawOnChartArea: index === 0,
        color: surfaceBorder,
      },
    };

    yAxis[key] = deepUnion(props.yAxes[key], yAxisOverwrite);
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
