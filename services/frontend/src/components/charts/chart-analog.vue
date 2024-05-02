<template>
  <chart-base-line
    :chart-data="chartData"
    :y-axes="yAxes"
    :height="props.height"
    :show-x-ticks="props.showXTicks"
  />
</template>

<script setup lang="ts">
import {
  defineProps,
  withDefaults,
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
  LineWidth,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';
import {
  ITimeseries, toChartJsData,
} from '@/components/charts/timeseries.ts';

interface IChartAnalogProps {
  timeseries: ITimeseries;
  color: string | GradientDefinition | DiscreteGradientDefinition;
  limits?: TAxisLimit;
  ticks?: number[];
  height?: string;
  tickStepSize?: number;
  showXTicks?: boolean;
}

const props = withDefaults(defineProps<IChartAnalogProps>(), {
  limits: () => [
    0,
    1,
  ],
  ticks: undefined,
  height: '10rem',
  tickStepSize: 5,
  showXTicks: true,
});

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
  () => getSuitableLimit(props.limits, props.timeseries.values, props.tickStepSize),
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
      'right',
      props.timeseries,
      actualLimits.value,
    ),
  } as TLineAxisProps;
});

</script>
