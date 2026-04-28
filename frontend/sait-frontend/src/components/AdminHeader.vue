<template>
  <header class="admin-header">
    <nav class="admin-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="admin-nav-link"
        :class="{ 'admin-nav-link--active': isActive(item.path) }"
      >
        <span class="admin-nav-icon">{{ item.icon }}</span>
        <span class="admin-nav-text">{{ item.label }}</span>
      </router-link>
    </nav>
    <router-link to="/" class="admin-back">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      <span>На сайт</span>
    </router-link>
  </header>
</template>

<script>
export default {
  name: 'AdminHeader',
  data() {
    return {
      navItems: [
        { path: '/admin/rooms', label: 'Номера', icon: '🏨' },
        { path: '/admin/site', label: 'Сайт', icon: '🌐' },
        { path: '/admin/stats', label: 'Статистика', icon: '📊' },
      ]
    }
  },
  methods: {
    isActive(path) {
      return this.$route.path === path || this.$route.path.startsWith(path + '/');
    }
  }
}
</script>

<style scoped>
.admin-header {
  margin: 10px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-white);
  border-bottom: 1px solid var(--color-gray-200);
  box-shadow: var(--shadow-sm);
}

.admin-nav {
  display: flex;
  gap: var(--spacing-xs);
}

.admin-nav-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  color: var(--color-gray-600);
  text-decoration: none;
  font-size: var(--text-base);
  font-weight: 500;
  transition: all var(--transition-fast);
  position: relative;
}

.admin-nav-link:hover {
  background: var(--color-gray-100);
  color: var(--color-gray-900);
  text-decoration: none;
}

.admin-nav-link--active {
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 600;
}

.admin-nav-link--active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: var(--spacing-md);
  right: var(--spacing-md);
  height: 2px;
  background: var(--color-primary);
  border-radius: var(--radius-sm);
}

.admin-nav-icon {
  font-size: var(--text-lg);
  line-height: 1;
}

.admin-back {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  color: var(--color-gray-600);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  border: 1px solid var(--color-gray-300);
}

.admin-back:hover {
  background: var(--color-gray-100);
  color: var(--color-gray-900);
  border-color: var(--color-gray-400);
  text-decoration: none;
  transform: translateX(-2px);
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
  }

  .admin-nav {
    width: 100%;
    justify-content: center;
  }

  .admin-nav-link {
    flex: 1;
    justify-content: center;
  }

  .admin-nav-text {
    display: none;
  }

  .admin-back {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .admin-nav {
    gap: 0;
  }

  .admin-nav-link {
    padding: var(--spacing-sm);
  }

  .admin-nav-icon {
    font-size: var(--text-xl);
  }
}
</style>
