<template>
  <div class="center">
    <h1>Oops!</h1>
    <p class="error">
      Error 404 - Page not found
    </p>
    <p>The page you requested could not be found.</p>
    <p><a href="javascript:history.back()">Back to previous Page</a></p>
  </div>
</template>

<script setup lang="ts">

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

  h1 {
    margin-bottom: .5rem;
  }
}

.error {
  color: red;
}
</style>
