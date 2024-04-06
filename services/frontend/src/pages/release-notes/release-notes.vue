<template>
  <markdown-text :content="ChangelogContent" />
</template>

<script setup lang="ts">
import MarkdownText from '@/components/markdown-text/markdown-text.vue';
import ChangelogContent from '@/../PUBLIC_CHANGELOG.md';
</script>
