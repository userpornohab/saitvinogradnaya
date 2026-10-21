import { createRouter, createWebHistory } from 'vue-router';
const RoomDetail = () => import('@/components/RoomDetail.vue');
import MainStr from '@/components/MainStr.vue';
const UserLogin = () => import('@/components/Auth/UserLogin.vue');
const AdminRooms = () => import('@/components/AdminRooms.vue');
const AdminSitePanel = () => import('@/components/AdminSitePanel.vue');
const StatisticksBooking = () => import('@/components/StatisticksBooking.vue');
const NotFound = () => import('@/components/NotFound.vue');

import api from '@/api';


const routes = [
  { path: '/account', name: 'GuestAccount', component: () => import('@/components/Guest/GuestAccount.vue') },
  {
    path: '/admin/online', name: 'AdminOnlineBookings', component: () => import('@/components/Guest/AdminOnlineBookings.vue'),
    beforeEnter: async () => {
      if (!localStorage.getItem('access_token')) return '/login';
      try { return (await api.get('/users/me/')).data.is_superuser ? true : '/'; }
      catch { return '/login'; }
    }
  },
  {
    path: '/room=:id',
    name: 'RoomDetail',
    component: RoomDetail,
  },
  {
    path: '/rooms/:roomSlug',
    name: 'RoomDetailSlug',
    component: RoomDetail,
  },
  {
    path: '/',
    name: 'Home',
    component: MainStr,
  },
  {
    path: '/login',
    name: 'UserLogin',
    component: UserLogin,
  },
  {
    path: '/admin/site',
    name: 'AdminSitePanel',
    component: AdminSitePanel,
    beforeEnter: async (to, from, next) => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        next('/login');
        return;
      }
      try {
        const response = await api.get('/users/me/')
        if (response.data.is_superuser) {
          next();
        } else {
          next('/');
        }
      } catch (error) {
        next('/login');
      }
    }
  },
    {
    path: '/admin/stats',
    name: 'StatisticksBooking',
    component: StatisticksBooking,
    beforeEnter: async (to, from, next) => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        next('/login');
        return;
      }
      try {
        const response = await api.get('/users/me/')
        if (response.data.is_superuser) {
          next();
        } else {
          next('/');
        }
      } catch (error) {
        next('/login');
      }
    }
  },
  {
    path: '/admin/rooms',
    name: 'AdminRooms',
    component: AdminRooms,
    beforeEnter: async (to, from, next) => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        next('/login');
        return;
      }
      try {
        const response = await api.get('/users/me/')
        if (response.data.is_superuser) {
          next();
        } else {
          next('/');
        }
      } catch (error) {
        next('/login');
      }
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }

    if (to.path === from.path && to.hash === from.hash) {
      return false;
    }

    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      };
    }

    return { top: 0, left: 0 };
  },
});

router.afterEach((to) => {
  const robots = document.querySelector('meta[name="robots"]');
  if (robots) robots.content = to.path.startsWith('/admin') || to.path === '/login' || to.path === '/account'
    || to.name === 'NotFound' ? 'noindex, nofollow' : 'index, follow';
});

export default router;
