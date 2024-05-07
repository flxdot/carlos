<template>
  <div class="page-action-bar">
    <div>
      <slot />
    </div>
    <div
      v-if="$slots.actions"
      class="page-action-bar__actions"
    >
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">

</script>

<style scoped lang="scss">
.page-action-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  row-gap: 1rem;

  &__actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}
</style>
