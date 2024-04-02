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
    name: ERouteName.HOME,
    component: () => import('@/pages/home/home.vue'),
  },
];

const router = createRouter({
  history: createWebHistory('/'),
  routes,
});

export default router;
