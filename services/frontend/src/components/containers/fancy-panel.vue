<template>
  <div class="fancy-panel">
    <slot />
  </div>
</template>

<script setup lang="ts">

</script>

<style scoped lang="scss">
.fancy-panel {
  padding: 1.5rem;
  border: 1px solid #ececec;
  border-radius: 6px;
  background-image: url('@/assets/fancy-bg.svg');
  background-repeat: no-repeat;
  background-size: cover;
}
</style>
