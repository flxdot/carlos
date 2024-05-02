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
  LineWidth,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';
import {
  ITimeseries, toChartJsData,
} from '@/components/charts/timeseries.ts';
import i18n from '@/plugins/i18n';

interface IChartAnalogProps {
  timeseries: ITimeseries;
  color: string | GradientDefinition | DiscreteGradientDefinition;
  height?: string;
  showXTicks?: boolean;
}

const props = withDefaults(defineProps<IChartAnalogProps>(), {
  height: '10rem',
  tickStepSize: 5,
  showXTicks: true,
});

const limits: [number, number] = [
  0,
  1,
];

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
  const axis = buildAxis(
    'right',
    props.timeseries,
    limits,
    limits,
  );

  axis.ticks = axis.ticks || {};
  axis.ticks.callback = (value: number) => {
    return value > 0.5 ? i18n.global.t('chart.boolean.high') : i18n.global.t('chart.boolean.low');
  };

  return {
    [props.timeseries.displayName]: axis,
  } as TLineAxisProps;
});

</script>
