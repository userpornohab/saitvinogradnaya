<template>
    <div class="auth-form">
      <h2>Регистрация</h2>
      <form @submit.prevent="handleSignUp">
        <div class="form-group">
          <label>Email:</label>
          <input v-model="email" type="email" required>
        </div>
        <div class="form-group">
          <label>Пароль:</label>
          <input v-model="password" type="password" required>
        </div>
        <button type="submit">Зарегистрироваться</button>
        <p>Уже есть аккаунт? <router-link to="/login">Войдите</router-link></p>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        email: '',
        password: ''
      }
    },
    methods: {
      async handleSignUp() {
        try {
          await axios.post('http://127.0.0.1:8000/register/', {
            email: this.email,
            password: this.password
          });
          
          this.$router.push('/login');
        } catch (error) {
          console.error('Ошибка регистрации:', error.response.data.detail);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  /* Аналогично стилям из Login.vue */
  </style>