module.exports = {
  extends: [
    'stylelint-config-standard-scss',
    'stylelint-config-html/vue',
  ],
  rules: {
    'no-duplicate-selectors': null,
    'declaration-no-important': null,
    'no-descending-specificity': null,
    'custom-property-pattern': '^[a-z]+[a-z0-9]*(--?[a-z0-9]+)*$', // kebab-case with --
  },
};
