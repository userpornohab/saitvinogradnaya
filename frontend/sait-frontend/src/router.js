import { createRouter, createWebHistory } from 'vue-router';
import RoomDetail from '@/components/RoomDetail.vue';
import MainStr from '@/components/MainStr.vue';
import UserLogin  from '@/components/Auth/UserLogin.vue';
import SignUp from '@/components/Auth/SignUp.vue';
import AdminRooms from '@/components/AdminRooms.vue';
import AdminSitePanel from '@/components/AdminSitePanel.vue';

//import AdminPanel from '@/components/Admin/AdminPanel.vue';

import axios from 'axios';


const routes = [
  {
    path: '/room/:id',
    name: 'RoomDetail',
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
        const response = await axios.get('http://localhost:8000/users/me/', { // Добавлен слеш в конце
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
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
        const response = await axios.get('http://localhost:8000/users/me/', { // Добавлен слеш в конце
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
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
    path: '/signup',
    name: 'SignUp',
    component: SignUp,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;