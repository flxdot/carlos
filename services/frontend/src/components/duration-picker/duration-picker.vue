<template>
  <prm-button-group>
    <prm-button
      v-for="duration in props.options"
      :key="duration.humanize()"
      :label="duration.humanize()"
      :outlined="duration.asMilliseconds() !== model.asMilliseconds()"
      @click="selectDuration(duration)"
    />
  </prm-button-group>
</template>

<script setup lang="ts">
import PrmButtonGroup from 'primevue/buttongroup';
import PrmButton from 'primevue/button';
import {
  Duration,
} from 'dayjs/plugin/duration';
import dayjs from 'dayjs';
import {
  ref,
  defineModel,
} from 'vue';

const model = defineModel<Duration>();

export type DurationProps = {
  options?: Duration[],
};

const props = withDefaults(defineProps<DurationProps>(), {
  options() {
    return [
      dayjs.duration(14, 'days'),
      dayjs.duration(7, 'days'),
      dayjs.duration(2, 'days'),
      dayjs.duration(24, 'hours'),
      dayjs.duration(12, 'hours'),
    ];
  },
});

const selected = ref<Duration>();

function selectDuration(duration: Duration) {
  model.value = duration;
}

</script>

<style scoped lang="scss">

</style>
