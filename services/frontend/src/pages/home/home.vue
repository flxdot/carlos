<template>
  <fancy-panel
    class="home-container"
  >
    <div class="welcome">
      <h1 style="font-weight: 200;">
        Welcome to
      </h1>
      <img
        src="@/assets/carlos-logo-type-white.png"
        alt="Carlos"
        class="logo"
      >
      <p style="font-weight: 600;">
        Your friendly greenhouse manager.
      </p>
    </div>
  </fancy-panel>
</template>

<script setup lang="ts">
import FancyPanel from '@/components/containers/fancy-panel.vue';

</script>

<style scoped lang="scss">

.home-container {
  --padding: 48px;

  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.welcome {
  margin-left: -20%;
  display: flex;
  gap: 1rem;
  flex-flow: column wrap;
}

.logo {
  width: 450px;
  height: auto;
}

@media only screen and (width <= 769px) {
  .home-container {
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
