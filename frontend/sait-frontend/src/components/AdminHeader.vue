<template>
  <div class="admin-header">
    <div class="navigation-links">
      <h2>
        <router-link to="/admin/rooms" class="admin-link">
          Административная панель
        </router-link>
      </h2>
      <h2>
        <router-link to="/admin/site" class="admin-link">
          Панель сайта
        </router-link>
      </h2>
    </div>
    <router-link to="/" class="back-button">
      ← На главную
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'AdminHeader'
}
</script>

<style scoped>
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eaeaea;
  margin-bottom: 30px;
}

.navigation-links {
  display: flex;
  gap: 20px;
}

.admin-link {
background:none;
  text-decoration: none;
  color: #6c757d;
  font-weight: 500;
  font-size: 1.25rem;
  padding: 8px 15px;
  border-radius: 6px;
  transition: all 0.3s ease;
  position: relative;
}

.admin-link:hover {
  color: #0d6efd;
  background-color: rgba(13, 110, 253, 0.05);
}

.admin-link.router-link-exact-active {
  color: #0d6efd;
  font-weight: 600;
}

.admin-link.router-link-exact-active::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 15px;
  right: 15px;
  height: 3px;
  background-color: #0d6efd;
  border-radius: 2px;
}

.back-button {
  text-decoration: none;
  color: #495057;
  padding: 8px 15px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: white;
  font-weight: 500;
}

.back-button:hover {
  background-color: #f8f9fa;
  border-color: #0d6efd;
  color: #0d6efd;
  transform: translateX(-3px);
}

/* Анимация для активных ссылок */
.router-link-exact-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Адаптивность */
@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
  }
  
  .navigation-links {
    width: 100%;
    justify-content: center;
    gap: 10px;
  }
  
  .admin-link {
    font-size: 1rem;
    padding: 6px 12px;
  }
  
  .back-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .navigation-links {
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .admin-link {
    width: 100%;
    text-align: center;
  }
}
</style>