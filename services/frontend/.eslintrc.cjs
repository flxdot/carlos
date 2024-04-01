module.exports = {
  root: true,
  extends: '@convidera-team/eslint-config-vue3-convidera',
  ignorePatterns: [
    '**/*.css',
    '**/*.scss',
  ],
  rules: {
    'no-plusplus': 'off',
    'no-underscore-dangle': [
      'error',
      {
        allow: [
          '_id', // general exception to accept accessing _id from API response objects
        ],
      },
    ],
    'vue/no-restricted-syntax': [
      'error',
      {
        message: "Please don't use global emit calls, they break types",
        selector: "CallExpression[callee.name='$emit']",
      },
    ],
    'max-len': 'off',
  },
  overrides: []
};
