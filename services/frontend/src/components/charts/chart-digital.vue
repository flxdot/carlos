<template>
  <chart-base-line
    :chart-data="chartData"
    :y-axes="yAxes"
    :height="props.height"
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
  TLineAxisProps,
  TLineChartData,
} from '@/components/charts/chart-types.ts';
import {
  chartJsGradient,
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

interface IChartAnalogProps {
  timeseries: ITimeseries;
  color: string | GradientDefinition | DiscreteGradientDefinition;
  height?: string;
}

const limits: [number, number] = [
  0,
  1,
];

const props = withDefaults(defineProps<IChartAnalogProps>(), {
  height: '10rem',
  tickStepSize: 5,
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

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  let gradient: GradientDefinition | DiscreteGradientDefinition;
  if (typeof props.color === 'string') {
    gradient = colorToColorStop(props.color);
  } else {
    gradient = props.color;
  }

  const borderColor = chartJsGradient(lineGradient.value, gradient, limits);
  const backgroundColor = chartJsGradient(LineBgGradient.value, gradient, limits, true);

  return {
    datasets: [
      {
        label: 'Temperature',
        data: toChartJsData(props.timeseries),
        borderWidth: LineWidth,
        borderColor,
        backgroundColor,
        fill: true,
        stepped: true,
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
      limits,
      limits,
      tempEmojis,
    ),
  } as TLineAxisProps;
});

</script>
