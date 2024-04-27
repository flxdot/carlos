<template>
  <tag
    v-if="props.device.isOnline"
    severity="success"
    :value="i18n.global.t('device.status.online')"
  />
  <tag
    v-else-if="!device.lastSeenAt"
    severity="contrast"
    :value="i18n.global.t('device.status.disconnected')"
  />
  <tag
    v-else
    severity="danger"
    :value="`${i18n.global.t('device.status.offlineSince', { time: dayjs(device?.lastSeenAt ).fromNow(true)})}`"
  />
</template>

<script setup lang="ts">
import {
  defineProps,
} from 'vue';
import Tag from 'primevue/tag';
import dayjs from 'dayjs';
import i18n from '@/plugins/i18n';
import {
  TGetDeviceDetailResponse,
} from '@/api/devices.ts';

const props = defineProps<{
  device: TGetDeviceDetailResponse;
}>();
</script>
