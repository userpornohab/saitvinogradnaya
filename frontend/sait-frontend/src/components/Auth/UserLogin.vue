<template>
    <div class="auth-form">
      <h2>Вход</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email:</label>
          <input v-model="email" type="email" required>
        </div>
        <div class="form-group">
          <label>Пароль:</label>
          <input v-model="password" type="password" required>
        </div>
        <button type="submit">Войти</button>
        <p>Нет аккаунта? <router-link to="/signup">Зарегистрируйтесь</router-link></p>
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
      async handleLogin() {
        try {
          const formData = new FormData();
          formData.append('username', this.email);
          formData.append('password', this.password);

          const response = await axios.post(
            'http://127.0.0.1:8000/token/',
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }
          );
          
          localStorage.setItem('access_token', response.data.access_token);
          this.$router.push('/');
        } catch (error) {
          console.error('Ошибка входа:', error.response.data.detail);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .auth-form {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  input {
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.3rem;
  }
  </style>