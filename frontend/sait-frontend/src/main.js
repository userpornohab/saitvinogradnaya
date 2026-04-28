import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import './assets/main.css';
import VueApexCharts from 'vue3-apexcharts';

const app = createApp(App);
app.use(router);

// VueApexCharts — объект { default: <Component> }
// При app.use() install() регистрирует компонент 'apexchart' глобально
app.use(VueApexCharts);

// Регистрируем компонент графиков с multi-word именем (для ESLint)
const ApexChartComp = VueApexCharts.default || VueApexCharts;
if (ApexChartComp) {
  app.component('ApexChartComponent', ApexChartComp);
}

// Добавляем интерсептор для JWT
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

app.mount('#app');