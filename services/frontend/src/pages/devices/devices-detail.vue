<template>
  <div class="container-group">
    <page-action-bar>
      <router-link
        v-slot="{ href, navigate }"
        :to="{
          name: ERouteName.DEVICES_OVERVIEW,
        }"
      >
        <a
          :href="href"
          title="Carlos"
          class="input-group subnav-link"
          @click="navigate"
        >
          <i class="pi pi-arrow-left" />
          <span>{{ i18n.global.t(`pages.${ERouteName.DEVICES_OVERVIEW}`) }}</span>
        </a>
      </router-link>
      <template #actions>
        <prm-button
          label="Refresh"
          type="button"
          icon="pi pi-replay"
          text
        />
        <duration-picker v-model="timeRange" />
      </template>
    </page-action-bar>
    <card class="device-card">
      <template #title>
        <skeleton
          v-if="deviceDetails === undefined"
          height="1.875rem"
        />
        <div
          v-else
          class="card-title"
        >
          <device-status-badge
            v-if="deviceDetails !== undefined"
            :device="deviceDetails"
          />
          <span>{{ deviceDetails?.displayName }}</span>
        </div>
      </template>
      <template #content>
        <skeleton
          v-if="deviceDetails === undefined"
        />
        <markdown-text
          v-else
          :content="deviceDetails?.description || ''"
        />
      </template>
    </card>
    <div
      v-for="driver in deviceDriver || []"
      :key="driver.driverIdentifier"
    >
      <template
        v-if="driver.isVisibleOnDashboard"
      >
        <div class="font-bold text-xl mb-4">
          {{ driver.driverIdentifier }}
        </div>
        <driver-timeseries
          v-if="deviceSignals !== undefined && deviceSignals.get(driver.driverIdentifier) !== undefined"
          :driver="driver"
          :signal-list="deviceSignals.get(driver.driverIdentifier) || []"
          :duration="timeRange"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  reactive,
  onMounted,
  onBeforeUnmount, computed,
} from 'vue';
import {
  useRoute,
} from 'vue-router';
import PrmButton from 'primevue/button';
import Card from 'primevue/card';
import Skeleton from 'primevue/skeleton';
import {
  Duration,
} from 'dayjs/plugin/duration';
import dayjs from 'dayjs';
import {
  getDeviceDetail,
  TGetDeviceDetailResponse,
  TGetDeviceDriversResponse,
  TGetDeviceDriversSignalsResponse,
} from '@/api/devices.ts';
import {
  ERouteName,
} from '@/router/route-name.ts';
import i18n from '@/plugins/i18n';
import DeviceStatusBadge from '@/components/device/device-status-badge.vue';
import MarkdownText from '@/components/markdown-text/markdown-text.vue';
import {
  useDevicesStore,
} from '@/store/devices.ts';
import DriverTimeseries from '@/components/driver/driver-timeseries.vue';
import PageActionBar from '@/components/page-action-bar/page-action-bar.vue';
import DurationPicker from '@/components/duration-picker/duration-picker.vue';

const UPDATE_INTERVAL = 1000 * 60; // 1 minute
let intervalId: ReturnType<typeof setInterval>;

const route = useRoute();
const deviceStore = useDevicesStore();

const currentDeviceId = computed<string>(() => route.params.deviceId as string);

const deviceDetails = ref<TGetDeviceDetailResponse | undefined>();
const deviceDriver = ref<TGetDeviceDriversResponse | undefined>();
const deviceSignals = reactive<Map<string, TGetDeviceDriversSignalsResponse | undefined>>(new Map());

const timeRange = ref<Duration>(dayjs.duration(7, 'days'));

function updateDevice() {
  getDeviceDetail(
    {
      deviceId: currentDeviceId.value,
    },
  ).then((response) => {
    deviceDetails.value = response.data;
  });

  deviceStore.fetchDeviceDrivers(currentDeviceId.value).then((driverList) => {
    deviceDriver.value = driverList;
    for (const driver of (driverList || [])) {
      deviceStore.fetchDeviceDriverSignals(currentDeviceId.value, driver.driverIdentifier)
        .then((signalList) => {
          deviceSignals.set(driver.driverIdentifier, signalList);
        });
    }
  });
}

onMounted(() => {
  updateDevice();
  intervalId = setInterval(updateDevice, UPDATE_INTERVAL);
});

onBeforeUnmount(() => {
  clearInterval(intervalId);
});

</script>

<style  lang="scss">
.p-card,
.p-accordion .p-accordion-tab .p-accordion-header a,
.p-accordion .p-accordion-content{
  background: var(--carlos-bg-color);
  color: var(--carlos-text-color);
}

.p-card {
  box-shadow: none;
}
</style>

<style scoped lang="scss">

.card-title {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;

  &__sub {
    font-size: 0.875rem;
    line-height: 1.25rem;
    font-weight: 400;
  }
}

@media only screen and (width <= 481px) {
  .card-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media only screen and (width <= 769px) {
  .container-group {
    margin-top: 1rem;
  }

  .device-card {
    border-radius: 0;
    border: none;
  }

  .subnav-link {
    margin-left: 1rem;
  }
}
</style>
