<template>
  <div class="page">
    <img
      :src="logo"
      alt="Carlos"
      class="logo"
    >
    <h1>Welcome to Carlos</h1>
    <p>🌱 Your friendly greenhouse manager. 🌱</p>
  </div>
</template>

<script setup lang="ts">
import logo from '@/assets/logo-type-black.png';

</script>

<style scoped lang="scss">
.page {
  height: calc(100% - var(--header-height));
  width: 100%;
  display: flex;
  place-items: center;
  gap: 1rem;
  align-content: center;
  justify-content: center;
  align-items: center;
  justify-items: center;
  flex-direction: column;
  flex-wrap: wrap;
}

img.logo {
  width: 50%;
  max-width: 450px;
  height: auto;
}
</style>
