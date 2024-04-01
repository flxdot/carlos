import {
  createApp,
} from 'vue';
import PrimeVue from 'primevue/config';
import App from './app.vue';
import router from '@/router';
import 'primevue/resources/themes/aura-light-lime/theme.css';
import 'primeicons/primeicons.css';
import './style.css';

const app = createApp(App);

app.use(PrimeVue);

app.use(router);

app.mount('#app');
