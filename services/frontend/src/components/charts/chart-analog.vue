<template>
  <div>
    <pre>
      {{ props.timeseries.displayName }}
    </pre>
    <chart-base-line
      :chart-data="chartData"
      :y-axes="yAxes"
      height="10rem"
    />
  </div>
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
  TLineAxisProps,
  TLineChartData,
} from '@/components/charts/chart-types.ts';
import {
  chartJsGradient,
  getSuitableLimit,
  buildAxis,
} from '@/components/charts/chart-utils.ts';
import {
  carlosPalettePrimary, DiscreteGradientDefinition,
  GradientCache, GradientDefinition,
} from '@/components/charts/gradients.ts';
import {
  tempEmojis,
} from '@/utils/value-render.ts';
import {
  LineWidth,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';
import {
  ITimeseries,
} from '@/components/charts/timeseries.ts';

const props = defineProps<{
  timeseries: ITimeseries,
  limits: TAxisLimit,
  ticks: number[],
  color: string | GradientDefinition | DiscreteGradientDefinition
}>();

const lineGradient = ref<GradientCache>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const LineBgGradient = ref<GradientCache>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const actualLimits = computed<TAxisLimit>(
  () => getSuitableLimit(props.limits, props.timeseries.samples.map((x) => x.y)),
);

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  const tempColor = chartJsGradient(lineGradient.value, actualLimits.value, carlosPalettePrimary);
  const tempBgColor = chartJsGradient(LineBgGradient.value, actualLimits.value, carlosPalettePrimary, true);

  return {
    datasets: [
      {
        label: 'Temperature',
        data: props.timeseries.samples,
        borderWidth: LineWidth,
        chartJsGradient: tempColor,
        backgroundColor: tempBgColor,
        fill: true,
        pointStyle: false,
        yAxisID: 'temp',
        // The tension helps to smooth the line in case of oversampling
        tension: 0.1,
      },
    ],
  } as DeepPartial<TLineChartData>;
});

const yAxes = computed<TLineAxisProps>(() => {
  return {
    temp: buildAxis(
      'left',
      props.timeseries,
      actualLimits.value,
      props.ticks,
      tempEmojis,
    ),
  } as TLineAxisProps;
});

</script>
