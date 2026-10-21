import axios from 'axios';
import { reactive } from 'vue';
import { API_BASE_URL } from './api';

export const guestState = reactive({ user: null, csrf: '', ready: false });
const guestApi = axios.create({ baseURL: API_BASE_URL, withCredentials: true, timeout: 20000 });
guestApi.interceptors.request.use(config => {
  if (guestState.csrf && !['get', 'head', 'options'].includes(config.method)) {
    config.headers['X-CSRF-Token'] = guestState.csrf;
  }
  return config;
});
guestApi.interceptors.response.use(response => response, error => {
  if (error.response?.status === 401) {
    guestState.user = null;
    guestState.csrf = '';
  }
  return Promise.reject(error);
});
export function acceptSession(data) {
  guestState.user = data.user;
  guestState.csrf = data.csrf;
  guestState.ready = true;
}
export async function loadGuest() {
  try { acceptSession((await guestApi.get('/guest/auth/session')).data); }
  catch (error) {
    if (error.response?.status !== 401) throw error;
    acceptSession({ user: null, csrf: '' });
  }
}
export function errorText(error) {
  const detail = error.response?.data?.detail;
  return typeof detail === 'string' ? detail : Array.isArray(detail)
    ? 'Проверьте заполнение полей: ' + detail.map(item => item.msg).join('; ')
    : 'Не удалось связаться с сервером. Попробуйте ещё раз.';
}
export const money = value => (Number(value || 0) / 100).toLocaleString('ru-RU', { style: 'currency', currency: 'RUB' });
export const dayLabel = value => new Date(value + 'T12:00:00').toLocaleDateString('ru-RU');
export function requestKey() {
  return Array.from(crypto.getRandomValues(new Uint8Array(16)), value => value.toString(16).padStart(2, '0')).join('');
}
export const statusLabels = {
  awaiting_payment: 'Ожидает предоплату', confirmed: 'Бронь подтверждена', expired: 'Срок оплаты истёк',
  cancelled: 'Отменена', cancel_requested: 'Запрошена отмена', payment_review: 'Оплата требует проверки',
  refunded: 'Возврат зарегистрирован', test_paid: 'Тестовая оплата'
};
export default guestApi;
