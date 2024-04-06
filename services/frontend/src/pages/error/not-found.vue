<template>
  <div class="center">
    <h1 class="mb-4">
      {{ i18n.global.t('error.oops') }}
    </h1>
    <p class="error">
      {{ i18n.global.t('error.errorMessageTemplate', {
        code: '404',
        message: i18n.global.t('error.notFound.title')
      })
      }}
    </p>
    <p>{{ i18n.global.t('error.notFound.message') }}</p>
    <p class="mt-4">
      <a href="javascript:history.back()">
        <i class="pi pi-arrow-left" />
        {{ i18n.global.t('error.goBack') }}
      </a>
    </p>
  </div>
</template>

<script setup lang="ts">
import i18n from '@/plugins/i18n';
</script>

<style scoped lang="scss">
.center {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
  gap: .5rem;
  font-size: 1.2rem;
}

.error {
  color: red;
}
</style>
