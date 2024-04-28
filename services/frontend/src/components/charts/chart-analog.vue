<template>
  <div>
    <pre>
      <span>
        {{ props.timeseries.displayName }}
      </span>
      <span>
        {{ props.timeseries.values[props.timeseries.values.length - 1] }} {{ props.timeseries.unitSymbol }}
      </span>
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
  colorToColorStop, DiscreteGradientDefinition,
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
  ITimeseries, toChartJsData,
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
  () => getSuitableLimit(props.limits, props.timeseries.values),
);

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  let gradient: GradientDefinition | DiscreteGradientDefinition;
  if (typeof props.color === 'string') {
    gradient = colorToColorStop(props.color);
  } else {
    gradient = props.color;
  }

  const borderColor = chartJsGradient(lineGradient.value, gradient, actualLimits.value);
  const backgroundColor = chartJsGradient(LineBgGradient.value, gradient, actualLimits.value, true);

  return {
    datasets: [
      {
        label: 'Temperature',
        data: toChartJsData(props.timeseries),
        borderWidth: LineWidth,
        borderColor,
        backgroundColor,
        fill: true,
        pointStyle: false,
        yAxisID: props.timeseries.displayName,
        // The tension helps to smooth the line in case of oversampling
        tension: 0.1,
      },
    ],
  } as DeepPartial<TLineChartData>;
});

const yAxes = computed<TLineAxisProps>(() => {
  return {
    [props.timeseries.displayName]: buildAxis(
      'left',
      props.timeseries,
      actualLimits.value,
      props.ticks,
      tempEmojis,
    ),
  } as TLineAxisProps;
});

</script>
