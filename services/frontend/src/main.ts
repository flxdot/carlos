import {
  createApp,
} from 'vue';
import {
  createPinia,
} from 'pinia';
import PrimeVue from 'primevue/config';
import {
  createAuth0,
} from '@auth0/auth0-vue';
import App from './app.vue';
import router from '@/router';
import 'primevue/resources/themes/aura-light-lime/theme.css';
import 'primeicons/primeicons.css';
import '@/styles/tailwind.css';
import '@/styles/primetheme.scss';
import '@/styles/main.css';
import '@/styles/carlos.css';
import config from '@/config.ts';

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);
app.use(PrimeVue);
app.use(
  createAuth0({
    domain: config.VITE_AUTH0_DOMAIN,
    clientId: config.VITE_AUTH0_CLIENT_ID,
    authorizationParams: {
      redirect_uri: `${window.location.origin}/accept-login`,
    },
  }),
);
app.use(router);

app.mount('#app');
