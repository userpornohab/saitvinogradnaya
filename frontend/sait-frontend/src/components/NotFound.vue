<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1 class="not-found-code">404</h1>
      <p class="not-found-text">Страница не найдена</p>
      <p class="not-found-desc">Запрашиваемая страница не существует или была перемещена</p>
      <router-link to="/" class="not-found-btn">На главную</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
};
</script>

<style scoped>
.not-found {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.not-found-content {
  text-align: center;
}

.not-found-code {
  font-size: 8rem;
  font-weight: 700;
  color: var(--color-gray-200, #e5e7eb);
  line-height: 1;
  margin: 0;
}

.not-found-text {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-gray-900, #111827);
  margin: 0.5rem 0;
}

.not-found-desc {
  font-size: 1rem;
  color: var(--color-gray-500, #6b7280);
  margin: 0 0 2rem;
}

.not-found-btn {
  display: inline-block;
  padding: 0.75rem 2rem;
  background: var(--color-primary, #4c4cf7);
  color: #fff;
  border-radius: var(--radius-full, 9999px);
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  transition: background 0.2s ease, transform 0.15s ease;
}

.not-found-btn:hover {
  background: var(--color-primary-dark, #3b3bd4);
  transform: translateY(-1px);
}
</style>
