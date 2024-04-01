import {
  defineConfig,
} from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import markdownRawPlugin from 'vite-raw-plugin';
import svgLoader from 'vite-svg-loader';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    markdownRawPlugin({
      fileRegex: /\.md$/,
    }),
    svgLoader({
      svgoConfig: {
        plugins: [
          {
            name: 'preset-default',
            params: {
              overrides: {
                removeViewBox: false,
              },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // server: {
  //   // host: 'carlos.local',
  //   // https: {
  //   //   key: fs.readFileSync(`${__dirname}/../../local.qmulus.ai-key.pem`),
  //   //   cert: fs.readFileSync(`${__dirname}/../../local.qmulus.ai.pem`),
  //   // },
  // },
});
