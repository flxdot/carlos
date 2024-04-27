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
  carlosPalettePrimary,
} from '@/components/charts/gradients.ts';
import {
  tempEmojis,
} from '@/utils/value-render.ts';
import {
  LineWidth,
  tempLimits,
  tempTicks,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';

const props = defineProps<{temperature: ITimeseries}>();

const tempGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempBgGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempYLimit = computed<TAxisLimit>(() => getSuitableLimit(tempLimits, props.temperature.values));

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  const tempColor = borderColor(tempGradient.value, tempYLimit.value, carlosPalettePrimary);
  const tempBgColor = borderColor(tempBgGradient.value, tempYLimit.value, carlosPalettePrimary, 0.5, true);

  return {
    datasets: [
      {
        label: 'Temperature',
        data: toPoints(props.temperature),
        borderWidth: LineWidth,
        borderColor: tempColor,
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
    temp: buildAxis('left', props.temperature, tempYLimit.value, tempTicks, tempEmojis),
  } as TLineAxisProps;
});

</script>
