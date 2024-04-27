<template>
  <menubar
    :model="menuItems"
    class="carlos-nav"
  >
    <template
      #start
    >
      <router-link
        v-slot="{ href, navigate }"
        :to="{
          name: ERouteName.HOME
        }"
        custom
      >
        <a
          :href="href"
          title="Carlos"
          @click="navigate"
        >
          <div class="logo">
            <img
              alt="logo"
              src="@/assets/carlos-logo-type-white.png"
            >
          </div>
        </a>
      </router-link>
    </template>
    <template #end>
      <div class="mr-2">
        <prm-skeleton
          v-if="isLoading"
          size="2rem"
          style="opacity: 0.5;"
        />
        <prm-button
          v-else-if="!isLoading && !isAuthenticated"
          text
          :label="i18n.global.t('authentication.login')"
          icon="pi pi-sign-in"
          @click="login"
        />
        <button
          v-else
          type="button"
          size="large"
          @click="userMenu!.toggle"
        >
          <prm-avatar
            :label="userInitials"
          />
        </button>
        <prm-menu
          ref="userMenu"
          popup
          :model="avatarMenuItems"
          a
          class="carlos-nav"
          style="width: 18rem;"
        >
          <template #start>
            <div class="p-4 font-semibold">
              <prm-avatar :label="userInitials" />
              <span class="pl-2">{{ userName || '' }}</span>
            </div>
          </template>
          <template #item="{ item, props }">
            <router-link
              v-if="item.routeName"
              v-slot="{ href, navigate }"
              :to="item.routeName"
              custom
            >
              <a
                :href="href"
                v-bind="props.action"
                class="menu-item"
                :style="item.style"
                @click="navigate"
              >
                <span :class="item.icon" />
                <span class="ml-2">{{ item.label }}</span>
              </a>
            </router-link>
            <button
              v-else-if="item.command"
              v-bind="props.action"
              :style="item.style"
              type="button"
              class="w-full menu-item"
            >
              <span :class="item.icon" />
              <span class="ml-2">{{ item.label }}</span>
            </button>
            <div
              v-else
              class="menu-item"
              :style="item.style"
              @hover.capture.stop
              @click.capture.stop
            >
              <span class="mx-4">{{ item.label }}</span>
            </div>
          </template>
          <template
            #end
          >
            <div
              class="p-4"
              style="display: flex; justify-content: space-between;"
            >
              <router-link
                v-slot="{ href, navigate }"
                :to="{
                  name: ERouteName.RELEASE_NOTES
                }"
                custom
              >
                <a
                  :href="href"
                  class="menu-item"
                  @click="navigate"
                >
                  <span class="font-bold">{{ packageInfo.version }}</span>
                </a>
              </router-link>
            </div>
          </template>
        </prm-menu>
      </div>
    </template>
  </menubar>
</template>

<script setup lang="ts">
import {
  ref,
  computed,
} from 'vue';
import Menubar from 'primevue/menubar';
import {
  MenuItem,
} from 'primevue/menuitem';
import PrmButton from 'primevue/button';
import PrmAvatar from 'primevue/avatar';
import PrmMenu from 'primevue/menu';
import PrmSkeleton from 'primevue/skeleton';
import {
  useAuth0,
} from '@auth0/auth0-vue';
import {
  useRouter,
} from 'vue-router';
import {
  ERouteName,
} from '@/router/route-name.ts';
import packageInfo from '@/../package.json';
import i18n from '@/plugins/i18n';
import {
  useDevicesStore,
} from '@/store/devices.ts';
import {
  useAuthStore,
} from '@/store/auth.ts';

const {
  loginWithRedirect,
  user,
  isAuthenticated,
  logout,
  isLoading,
} = useAuth0();

const router = useRouter();

const devicesStore = useDevicesStore();
const authStore = useAuthStore();

const menuItems = ref<MenuItem[]>([]);

authStore.$subscribe(() => {
  if (authStore.isAuthenticated) {
    devicesStore.fetchDevicesList().then((devices) => {
      const devicesMenu = devices.map((device) => {
        return {
          label: device.displayName,
          command() {
            router.push({
              name: ERouteName.DEVICES_DETAIL,
              params: {
                deviceId: device.deviceId,
              },
            });
          },
        };
      });
      menuItems.value = [
        {
          label: i18n.global.t('navbar.devices'),
          items: [
            {
              label: i18n.global.t(`pages.${ERouteName.DEVICES_OVERVIEW}`),
              icon: 'pi pi-th-large',
              command() {
                router.push({
                  name: ERouteName.DEVICES_OVERVIEW,
                });
              },
            },
            {
              separator: true,
            },
            ...devicesMenu,
          ],
        },
      ];
    });
  }
});

const userMenu = ref<InstanceType<typeof PrmMenu> | null>(null);

const avatarMenuItems = ref([
  {
    separator: true,
  },
  {
    label: i18n.global.t('authentication.logout'),
    icon: 'pi pi-sign-out',
    style: {
      color: 'var(--carlos-danger-color)',
    },
    command: () => logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    }),
  },
  {
    separator: true,
  },
]);

const userName = computed<string | undefined>(() => {
  return isAuthenticated && user.value && user.value.name ? user.value.name : undefined;
});

const userInitials = computed<string>(() => {
  if (userName.value) {
    const [firstName, lastName] = userName.value.split(' ');
    return `${firstName.charAt(0)}${lastName ? lastName.charAt(0) : ''}`;
  }
  return '';
});

function login() {
  loginWithRedirect();
}

</script>

<style scoped lang="scss">

.p-menu.p-menu-overlay, .p-menubar {
  background-color: var(--primary-color);
  border: none;
  color: var(--primary-color-text);
}

.p-menubar {
  height: var(--header-height);
}

.logo {
  display: flex;
  align-items: center;
}

.logo > img {
  height: 1.2rem;
  width: auto;
  margin-left: 0.5rem;
  margin-right: 1rem;
}

@media only screen and (width <= 769px) {
  .app {
    padding: 0;
  }
}

.p-button.p-button-text {
  color: var(--primary-color-text);
}

.menu-item {
  text-align: start;
  word-break: break-word;
}
</style>
