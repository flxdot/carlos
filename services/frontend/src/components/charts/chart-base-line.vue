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
  computed, ref,
} from 'vue';
import {
  ChartOptions,
  Scale,
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
import {
  borderColor, Gradient,
} from '@/components/charts/chart-utils.ts';
import {
  carlosPaletteBrown,
  pastelHumidityGradient, xTicksGradient,
} from '@/components/charts/gradients.ts';

const props = defineProps<{
  chartData: DeepPartial<TLineChartData>,
  yAxes: TLineAxisProps,
  height?: string,
}>();

const humidGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});

const chartData = computed<DeepPartial<TLineChartData>>(() => props.chartData);
const chartOptions = computed<DeepPartial<ChartOptions>>(() => {
  const documentStyle = getComputedStyle(document.documentElement);
  const color = documentStyle.getPropertyValue('--carlos-bg-text--dark');
  // const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

  const xAxis: TTimeAxisProps = {
    x: {
      // @ts-ignore - unsure why the types do not match
      type: 'time',
      time: {
        unit: 'day',
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
        display: true,
        drawOnChartArea: true,
        drawTicks: true,
        color: borderColor(humidGradient.value, [
          0,
          1,
        ], xTicksGradient),
        tickColor: borderColor(humidGradient.value, [
          0,
          1,
        ], xTicksGradient),
      },
    },
  };
  // explicitly set the color of the ticks and grid lines if not set in the props
  const yAxis: TLineAxisProps = {};
  Object.keys(props.yAxes).forEach((key) => {
    const yAxisOverwrite: TLineAxisProps[string] = {
      title: {
        display: true,
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
      afterFit: (scale: Scale) => {
        // This line ensures that all Y axis have the same width and
        // therefore all charts are synchronized
        scale.width = 60; // eslint-disable-line no-param-reassign
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
    interaction: {
      mode: 'x',
      intersect: false,
    },
    hover: {
      mode: 'x',
      intersect: false,
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
