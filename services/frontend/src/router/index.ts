import {
  createWebHistory,
  createRouter,
  RouteRecordRaw,
} from 'vue-router';
import {
  authGuard,
} from '@auth0/auth0-vue';
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
    path: '/devices',
    name: ERouteName.DEVICES_OVERVIEW,
    component: () => import('@/pages/devices/devices-overview.vue'),
    beforeEnter: authGuard,
  },
  {
    path: '/devices/:deviceId',
    name: ERouteName.DEVICES_DETAIL,
    component: () => import('@/pages/devices/devices-detail.vue'),
    beforeEnter: authGuard,
  },
  {
    path: '/accept-login',
    name: ERouteName.ACCEPT_LOGIN,
    component: () => import('@/pages/auth/accept-login.vue'),
  },
  {
    path: '/release-notes',
    name: ERouteName.RELEASE_NOTES,
    component: () => import('@/pages/release-notes/release-notes.vue'),
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
