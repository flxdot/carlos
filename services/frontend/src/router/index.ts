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
  {
    path: '/accept-login',
    name: ERouteName.ACCEPT_LOGIN,
    component: () => import('@/pages/auth/accept-login.vue'),
  },
  // This route should be the last one
  {
    path: '/:pathMatch(.*)*',
    name: ERouteName.NOT_FOUND,
    component: () => import('@/pages/error/not-found.vue'),
  },
];

const router = createRouter({
  history: createWebHistory('/'),
  routes,
});

export default router;
