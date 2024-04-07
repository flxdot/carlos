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
  // Unfortunately Safari has some issues rendering the original SVG under certain
  // conditions. So we use a PNG instead.
  background-image: url('@/assets/fancy-bg.png');
  background-repeat: no-repeat;
  background-size: cover;
}
</style>
