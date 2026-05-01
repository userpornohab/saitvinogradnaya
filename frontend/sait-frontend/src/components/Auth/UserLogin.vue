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
        <router-link to="/" class="btn-home">На главную</router-link>
      </form>
    </div>
  </template>
  
  <script>
  import api from '@/api';
  
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

          const response = await api.post(
            '/token/',
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }
          );
          
          localStorage.setItem('access_token', response.data.access_token);
          this.$router.push('/admin/rooms');
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

  .btn-home {
    display: block;
    text-align: center;
    margin-top: 1rem;
    padding: 0.75rem;
    color: #4c4cf7;
    text-decoration: none;
    font-size: 0.95rem;
    border-radius: 6px;
    transition: background 0.2s;
  }

  .btn-home:hover {
    background: #f3f4f6;
  }
  </style>