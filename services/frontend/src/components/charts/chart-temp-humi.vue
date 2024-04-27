<template>
  <chart-base-line
    :chart-data="chartData"
    :y-axes="yAxes"
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
  setConstantTicks,
  toPoints,
} from '@/components/charts/chart-utils.ts';
import {
  pastelHumidityGradient,
  vividTemperatureGradient,
} from '@/components/charts/gradients.ts';
import {
  humidEmojis, tempEmojis,
} from '@/utils/value-render.ts';
import {
  DASHED,
  humidityLimits,
  humidityTicks,
  tempLimits,
  tempTicks,
} from '@/components/charts/constants.ts';
import {
  DeepPartial,
} from '@/utils/types.ts';
import {
  getMediaCategory, MediaSize,
} from '@/utils/window.ts';
import i18n from '@/plugins/i18n';

const props = defineProps<{temperature: ITimeseries, humidity: ITimeseries}>();

const tempGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const tempYLimit = computed<TAxisLimit>(() => getSuitableLimit(tempLimits, props.temperature.values));

const humidGradient = ref<Gradient>({
  chartWidth: undefined,
  chartHeight: undefined,
  gradient: undefined,
});
const humidYLimit = computed<TAxisLimit>(() => getSuitableLimit(humidityLimits, props.humidity.values));

const chartData = computed<DeepPartial<TLineChartData>>(() => {
  const tempColor = borderColor(tempGradient.value, tempYLimit.value, vividTemperatureGradient);
  const humidColor = borderColor(humidGradient.value, humidYLimit.value, pastelHumidityGradient);

  return {
    datasets: [
      {
        label: 'Temperature',
        data: toPoints(props.temperature),
        borderWidth: 2,
        backgroundColor: tempColor,
        borderColor: tempColor,
        pointStyle: false,
        yAxisID: 'temp',
        // The tension helps to smooth the line in case of oversampling
        tension: 0.1,
      },
      {
        label: 'Humidity',
        data: toPoints(props.humidity),
        borderWidth: 3,
        backgroundColor: humidColor,
        borderColor: humidColor,
        borderDash: DASHED,
        pointStyle: false,
        yAxisID: 'humid',
        // The tension helps to smooth the line in case of oversampling
        tension: 0.1,
      },
    ],
  } as DeepPartial<TLineChartData>;
});

function buildAxis(position: 'left' | 'right', timeseries: ITimeseries, limits: TAxisLimit, ticks: number[], tickPrefix: (arg0: number) => string): TLineAxisProps[string] {
  const mediaSize = getMediaCategory();

  return {
    // @ts-ignore - unsure why the types do not match
    type: 'linear',
    display: true,
    position,
    title: {
      display: mediaSize >= MediaSize.DESKTOP,
      text: i18n.global.t('data.labelWithUnit', {
        label: timeseries.label,
        unit: timeseries.unitSymbol,
      }),
    },
    min: limits[0],
    max: limits[1],
    ticks: {
      callback: (value: number) => {
        if (mediaSize >= MediaSize.DESKTOP) {
          return `${tickPrefix(value)} ${value} ${timeseries.unitSymbol}`;
        }
        if (mediaSize >= MediaSize.TABLET) {
          return `${value} ${timeseries.unitSymbol}`;
        }
        return `${value}`;
      },
    },
    afterBuildTicks: setConstantTicks(ticks),
  };
}

const yAxes = computed<TLineAxisProps>(() => {
  return {
    temp: buildAxis('left', props.temperature, tempYLimit.value, tempTicks, tempEmojis),
    humid: buildAxis('right', props.humidity, humidYLimit.value, humidityTicks, humidEmojis),
  } as TLineAxisProps;
});

</script>
