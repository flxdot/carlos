<template>
  <page-header />
  <router-view />
</template>

<script setup lang="ts">
import {
  RouterView,
} from 'vue-router';
import PageHeader from './components/main-layout/header.vue';
</script>

<style lang="scss">
@use '@/styles/font.scss';
</style>
