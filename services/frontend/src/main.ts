import {
  createApp,
} from 'vue';
import {
  createPinia,
} from 'pinia';
import PrimeVue from 'primevue/config';
import Tooltip from 'primevue/tooltip';
import {
  createAuth0,
} from '@auth0/auth0-vue';
import App from './app.vue';
import router from '@/router';
import 'primevue/resources/themes/aura-light-lime/theme.css';
import 'primeicons/primeicons.css';
import '@/styles/primetheme.scss';
import '@/styles/main.scss';
import '@/styles/carlos.css';
import config from '@/config.ts';
import i18n from '@/plugins/i18n';
import '@/plugins/chartjs';
import '@/plugins/dayjs';
import {
  useSentry,
} from '@/plugins/sentry.ts';

const pinia = createPinia();
const app = createApp(App);

app.use(i18n);
app.use(pinia);
app.use(PrimeVue);
app.use(
  createAuth0({
    domain: config.VITE_AUTH0_DOMAIN,
    clientId: config.VITE_AUTH0_CLIENT_ID,
    authorizationParams: {
      redirect_uri: `${window.location.origin}/accept-login`,
      scope: 'openid profile email offline_access',
      audience: config.VITE_AUTH0_AUDIENCE,
    },
    cacheLocation: 'localstorage',
  }),
);
app.use(router);

useSentry(app);

app.directive('tooltip', Tooltip);

app.mount('#app');
