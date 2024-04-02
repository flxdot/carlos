<template>
  <fancy-panel
    class="container"
  >
    <div class="welcome">
      <h1 style="font-weight: 200;">
        Welcome to
      </h1>
      <img
        :src="logo"
        alt="Carlos"
        class="logo"
      >
      <p style="font-weight: 600;">
        🌱 Your friendly greenhouse manager. 🌱
      </p>
    </div>
  </fancy-panel>
</template>

<script setup lang="ts">
import logo from '@/assets/logo-type-white.png';
import FancyPanel from '@/components/containers/fancy-panel.vue';

</script>

<style scoped lang="scss">

.container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.welcome {
  color: #fff;
  margin-left: -20%;
  display: flex;
  gap: 1rem;
  flex-direction: column;
  flex-wrap: wrap;
}

.logo {
  width: 450px;
  height: auto;
}

@media only screen and (max-width: 769px) {
  .container {
    border-radius: 0;
    border: none;
  }

  .welcome {
    margin: 0;
    align-items: flex-end;
  }

  .logo {
    width: 80%;
  }
}
</style>
