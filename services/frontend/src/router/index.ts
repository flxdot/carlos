import {
  createWebHistory,
  createRouter,
  RouteRecordRaw,
} from 'vue-router';
import {
  ERouteName,
} from '@/router/route-name.ts';

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: ERouteName.LANDING_PAGE,
    component: () => import('@/pages/landing-page/landing-page.vue'),
  },
  {
    path: '/',
    name: ERouteName.HOME,
    component: () => import('@/pages/landing-page/landing-page.vue'),
  },
];

const router = createRouter({
  history: createWebHistory('/'),
  routes,
});

export default router;
