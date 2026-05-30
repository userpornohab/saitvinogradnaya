<template>
  <main class="auth-page">
    <div class="auth-form">
      <div class="auth-header">
        <span class="auth-kicker">Админ-панель</span>
        <h2>Вход</h2>
        <p>Введите данные администратора, чтобы управлять номерами, бронями и сайтом.</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input v-model="email" type="email" required placeholder="admin@example.com">
        </div>
        <div class="form-group">
          <label>Пароль</label>
          <input v-model="password" type="password" required placeholder="Введите пароль">
        </div>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <button type="submit">Войти</button>
        <router-link to="/" class="btn-home">На главную</router-link>
      </form>
    </div>
  </main>
  </template>
  
  <script>
  import api from '@/api';
  
  export default {
    data() {
      return {
        email: '',
        password: '',
        errorMessage: ''
      }
    },
    methods: {
      async handleLogin() {
        this.errorMessage = '';
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
          const detail = error.response?.data?.detail;
          this.errorMessage = detail || 'Не удалось войти. Проверьте, что бэкенд запущен на http://127.0.0.1:8000';
          console.error('Ошибка входа:', error);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .auth-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: clamp(1.5rem, 4vw, 3rem);
    background:
      linear-gradient(135deg, rgba(198, 196, 253, 0.24), rgba(255, 255, 255, 0.9) 42%),
      #f8fafc;
  }

  .auth-form {
    width: min(100%, 430px);
    padding: clamp(1.5rem, 4vw, 2.25rem);
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(198, 196, 253, 0.55);
    border-radius: 20px;
    box-shadow: 0 24px 60px rgba(24, 24, 27, 0.11);
  }

  .auth-header {
    margin-bottom: 1.5rem;
  }

  .auth-kicker {
    display: inline-flex;
    margin-bottom: 0.6rem;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(198, 196, 253, 0.38);
    color: #3730a3;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .auth-header h2 {
    margin: 0;
    color: #111827;
    font-size: 1.9rem;
    line-height: 1.15;
  }

  .auth-header p {
    margin: 0.65rem 0 0;
    color: #64748b;
    line-height: 1.55;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.45rem;
    color: #334155;
    font-size: 0.92rem;
    font-weight: 700;
  }
  
  input {
    width: 100%;
    padding: 0.85rem 0.95rem;
    border: 1px solid #d8d9f7;
    border-radius: 12px;
    background: #fff;
    color: #111827;
    font-size: 1rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  input:focus {
    outline: none;
    border-color: #8b86ff;
    box-shadow: 0 0 0 4px rgba(198, 196, 253, 0.38);
  }

  button {
    width: 100%;
    margin-top: 0.25rem;
    padding: 0.9rem 1rem;
    border: 0;
    border-radius: 12px;
    background: #4c4cf7;
    color: #fff;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  }

  button:hover {
    background: #3f3fd7;
    box-shadow: 0 12px 26px rgba(76, 76, 247, 0.24);
    transform: translateY(-1px);
  }

  .btn-home {
    display: block;
    text-align: center;
    margin-top: 1rem;
    padding: 0.85rem;
    color: #4c4cf7;
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 700;
    border-radius: 12px;
    transition: background 0.2s;
  }

  .btn-home:hover {
    background: #f3f4f6;
  }

  .error-message {
    color: #dc2626;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 0.75rem;
    margin: 0 0 1rem;
    font-size: 0.95rem;
  }
  </style>
