<template>
  <div class="overlay">
    <img
      src="/carlos-logo-round-transparent.png"
      alt="loading"
      class="spinner"
    >
  </div>
</template>

<script setup lang="ts">

</script>

<style scoped lang="scss">
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.spinner {
  display: inline-block;
  animation: spin 3s cubic-bezier(0.87, 0, 0.13, 1) infinite;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100dvw;
  height: 100dvh;
  z-index: 10;
  display: flex;
  place-content: center center;
  align-items: center;
  background-color: var(--bg-color);

  img {
    width: 150px;
    height: 150px;
  }
}
</style>
