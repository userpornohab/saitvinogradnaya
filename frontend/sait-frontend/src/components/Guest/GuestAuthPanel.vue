<template>
  <div class="guest-auth">
    <div v-if="!token" class="guest-tabs" role="tablist" aria-label="Вход или регистрация">
      <button v-for="item in tabs" :key="item.mode" role="tab" :aria-selected="mode === item.mode" @click="mode = item.mode; message = ''; error = ''">{{ item.title }}</button>
    </div>
    <h2>{{ heading }}</h2>
    <form @submit.prevent="submit" class="guest-form">
      <label v-if="mode === 'register'">Ваше имя<input v-model.trim="name" autocomplete="name" required minlength="2" maxlength="100"></label>
      <label v-if="!token">Электронная почта<input v-model.trim="email" type="email" autocomplete="email" required maxlength="255"></label>
      <label v-if="['login', 'register', 'reset'].includes(mode)">Пароль
        <span class="guest-password"><input v-model="password" :type="showPassword ? 'text' : 'password'" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" :minlength="mode === 'login' ? 1 : 12" maxlength="72" required>
          <button type="button" class="guest-icon" :title="showPassword ? 'Скрыть пароль' : 'Показать пароль'" :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'" @click="showPassword = !showPassword"><EyeOff v-if="showPassword" :size="18"/><Eye v-else :size="18"/></button>
        </span>
        <small v-if="mode !== 'login'">Не менее 12 символов</small>
      </label>
      <p v-if="error" class="guest-error" role="alert">{{ error }}</p>
      <p v-if="message" class="guest-notice" role="status">{{ message }}</p>
      <button class="guest-primary" :disabled="busy || completed">{{ busy ? 'Подождите...' : buttonTitle }}</button>
      <button v-if="mode === 'login'" type="button" class="guest-text-button" @click="mode = 'forgot'; message = ''; error = ''">Забыли пароль?</button>
      <button v-if="mode === 'forgot' || completed" type="button" class="guest-text-button" @click="$emit('token-done'); mode = 'login'; completed = false; message = ''">Вернуться ко входу</button>
    </form>
  </div>
</template>
<script>
import { Eye, EyeOff } from '@lucide/vue';
import guestApi, { acceptSession, errorText } from '@/guestApi';
export default {
  components: { Eye, EyeOff },
  props: { token: { type: String, default: '' }, action: { type: String, default: '' } },
  emits: ['authenticated', 'token-done'],
  data() { return { mode: this.action || 'login', email: '', password: '', name: '', busy: false, message: '', error: '', completed: false, showPassword: false,
    tabs: [{ mode: 'login', title: 'Вход' }, { mode: 'register', title: 'Регистрация' }] }; },
  computed: {
    heading() { return { login: 'Рады видеть вас снова', register: 'Аккаунт гостя', forgot: 'Восстановление доступа', verify: 'Подтвердите почту', reset: 'Новый пароль' }[this.mode]; },
    buttonTitle() { return { login: 'Войти', register: 'Зарегистрироваться', forgot: 'Получить ссылку', verify: 'Подтвердить почту', reset: 'Сохранить пароль' }[this.mode]; }
  },
  methods: {
    async submit() {
      this.busy = true; this.error = ''; this.message = '';
      try {
        let response;
        if (this.mode === 'login') {
          response = await guestApi.post('/guest/auth/login', { email: this.email, password: this.password });
          acceptSession(response.data); this.password = ''; this.$emit('authenticated');
        } else {
          const data = this.mode === 'register' ? { email: this.email, password: this.password, name: this.name }
            : this.mode === 'forgot' ? { email: this.email }
              : this.mode === 'reset' ? { token: this.token, password: this.password } : { token: this.token };
          response = await guestApi.post('/guest/auth/' + this.mode, data);
          this.message = response.data.message; this.password = '';
          if (this.token) this.completed = true;
        }
      } catch (error) { this.error = errorText(error); }
      finally { this.busy = false; }
    }
  }
};
</script>
