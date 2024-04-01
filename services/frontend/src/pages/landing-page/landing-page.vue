<template>
  <div>
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
img.logo {
  width: 50%;
  height: auto;
}
</style>
