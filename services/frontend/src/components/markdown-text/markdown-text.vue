<template>
  <!-- eslint-disable vue/no-v-html -->
  <div
    class="markdown-body"
    v-html="markdownConvertedToHTML"
  />
</template>

<script setup lang="ts">
import {
  defineProps, computed,
} from 'vue';
import MarkdownIt from 'markdown-it';

const props = defineProps<{
  content: string;
}>();

const md = new MarkdownIt();
const markdownConvertedToHTML = computed(() => md.render(props.content));
</script>

<style lang="scss">
/*
Reset some styles to actually show a difference.
This is required because some style in this project resets all of this.
*/
.markdown-body {
  h1,
  h2,
  h3 {
    display: block;
    font-weight: bold;
  }

  h1 {
    font-size: 1.5em;
    margin: 0.67em 0;
  }

  h2 {
    font-size: 1.2em;
    margin: 0.83em 0;
    border-bottom: 1px solid var(--primary);
  }

  h3 {
    margin: 1em 0;
  }

  a {
    color: var(--primary);
  }

  a:hover {
    color: var(--primary-highlight);
  }

  ul {
    display: block;
    list-style-type: disc;
    margin: 1em 0;
    padding-left: 40px;
  }

  /* nested lists */
  li > ul {
    margin: 0;
  }
}
</style>
