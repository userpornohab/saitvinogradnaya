<template>
  <div class="admin-header">
    <h2>Административная панель</h2>
    <router-link to="/" class="back-button">← На главную</router-link>
  </div>
</template>

<style scoped>
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.back-button {
  color: #666;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.back-button:hover {
  color: #333;
}
</style>