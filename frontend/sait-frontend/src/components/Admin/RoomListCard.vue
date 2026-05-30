<template>
  <div class="room-card" :class="{ selected: isSelected }">
    <img
      v-if="room.photos.length"
      :src="mainPhoto"
      class="room-thumb"
      alt="Фото номера"
    >
    <div class="room-info">
      <div class="room-header">
        <h4>{{ room.title }}</h4>
        <button @click.stop="$emit('delete', room.id)" title="Удалить" class="btn-delete">🗑</button>
      </div>
      <div class="room-actions">
        <button @click.stop="$emit('manage-prices', room)" title="Управление ценами">💰</button>
        <button @click.stop="$emit('manage-bookings', room)" title="Бронирования">📅</button>
        <button @click.stop="$emit('edit', room)" title="Редактировать">✏️</button>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '@/api';

export default {
  name: 'RoomListCard',
  props: {
    room: { type: Object, required: true },
    isSelected: { type: Boolean, default: false }
  },
  computed: {
    mainPhoto() {
      const photos = [...(this.room.photos || [])].sort((a, b) => {
        const orderDiff = (a.sort_order || 0) - (b.sort_order || 0);
        return orderDiff || a.id - b.id;
      });
      const main = photos.find(p => p.is_main);
      const photo = main || photos[0];
      return photo ? `${API_BASE_URL}${photo.url}` : '';
    }
  }
}
</script>

<style scoped>
.room-card {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.room-card:hover {
  background: var(--color-white);
  border-color: var(--color-gray-300);
  box-shadow: var(--shadow-sm);
}

.room-card.selected {
  background: var(--color-white);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.room-thumb {
  width: 68px;
  height: 54px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.room-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.room-header h4 {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-gray-900);
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-delete {
  background: none;
  border: none;
  font-size: var(--text-base);
  cursor: pointer;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.btn-delete:hover {
  opacity: 1;
}

.room-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.room-actions button {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-white);
  border: 1px solid var(--color-gray-300);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: var(--text-sm);
}

.room-actions button:hover {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
}
</style>
