<template>
  <overlay-loading />
</template>

<script setup lang="ts">
import {
  useAuth0,
} from '@auth0/auth0-vue';
import {
  setAuthTokens,
} from 'axios-jwt';
import OverlayLoading from '@/components/overlay-loading/overlay-loading.vue';
import router from '@/router/index.ts';
import {
  ERouteName,
} from '@/router/route-name.ts';

const {
  isLoading,
  getAccessTokenSilently,
} = useAuth0();

const handleAcceptLogin = async () => {
  while (isLoading.value) {
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  const token = await getAccessTokenSilently();
  await setAuthTokens({
    accessToken: token,
    refreshToken: '',
  });
  await router.replace({
    name: ERouteName.HOME,
  });
};

handleAcceptLogin();
</script>
