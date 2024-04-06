<template>
  <div class="footer">
    <p>
      Made with ❤️ by <a
        href="https://fanghanel.dev/"
        target="_blank"
        class="fanghanel-dev"
      >fanghanel.dev</a>
    </p>
    <p>
      <a
        href="https://github.com/flxdot/carlos"
        target="_blank"
        class="icon-link"
      ><git-hub-icon class="icon" />GitHub</a>
      <a
        href="https://fanghanel.dev/carlos"
        target="_blank"
        class="icon-link"
      ><material-for-mk-docs-icon class="icon" />Documentation</a>
    </p>
  </div>
</template>

<script setup lang="ts">
import GitHubIcon from '@/assets/icons/github.svg';
import MaterialForMkDocsIcon from '@/assets/icons/materialformkdocs.svg';
</script>

<style scoped lang="scss">
.footer {
  font-weight: 300;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

// for mobile view
@media only screen and (width <= 769px) {
  .footer {
    flex-direction: column;
    align-items: center;
  }
}

.footer > a {
  text-decoration: none;
  font-weight: var(--default-font-weight);
}

.icon-link {
  font-weight: 300;
  color: var(--text-color);
  fill: var(--text-color);

  svg {
    display: inline;
  }
}

.icon-link:not(:last-child) {
  margin-right: 1rem;
}

.icon-link:hover {
  color: var(--primary-color--light);
  fill: var(--primary-color--light);
}

.icon {
  height: 1rem;
  width: auto;
  margin-right: 0.3rem;
  vertical-align: text-top;
}
</style>
