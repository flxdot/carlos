<template>
  <chart-base-line
    :chart-data="chartData"
    :y-axes="yAxes"
    height="10rem"
  />
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
  ITimeseries, TLineAxisProps, TLineChartData,
} from '@/components/charts/chart-types.ts';
import {
  borderColor,
  Gradient,
  getSuitableLimit,
  toPoints, buildAxis,
} from '@/components/charts/chart-utils.ts';
import {
  carlosPaletteSand,
} from '@/components/charts/gradients.ts';
import {
  humidEmojis,
} from '@/utils/value-render.ts';
import {
  humidityLimits,
  humidityTicks, LineWidth,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';

const props = defineProps<{humidity: ITimeseries}>();

const humidGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidBgGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidYLimit = computed<TAxisLimit>(() => getSuitableLimit(humidityLimits, props.humidity.values));

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  const humidColor = borderColor(humidGradient.value, humidYLimit.value, carlosPaletteSand);
  const humidBgColor = borderColor(humidBgGradient.value, humidYLimit.value, carlosPaletteSand, 0.5, true);

  return {
    datasets: [
      {
        label: 'Humidity',
        data: toPoints(props.humidity),
        borderWidth: LineWidth,
        borderColor: humidColor,
        backgroundColor: humidBgColor,
        fill: true,
        pointStyle: false,
        yAxisID: 'humid',
        // The tension helps to smooth the line in case of oversampling
        tension: 0.1,
      },
    ],
  } as DeepPartial<TLineChartData>;
});

const yAxes = computed<TLineAxisProps>(() => {
  return {
    humid: buildAxis('left', props.humidity, humidYLimit.value, humidityTicks, humidEmojis),
  } as TLineAxisProps;
});

</script>
