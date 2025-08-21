<template>
  <div class="section-card">
    <div class="rooms-header">
      <h3>Список номеров</h3>
      <button class="add-button" @click="$emit('add-room')">+ Добавить номер</button>
    </div>
    
    <div class="room-list">
      <div 
        v-for="room in rooms" 
        :key="room.id" 
        class="room-card"
        :class="{selected: selectedRoomId === room.id}"
      >
        <div class="room-header">
          <h4>{{ room.title }}</h4>
          <button @click.stop="$emit('delete-room', room.id)" title="Удалить">🗑</button>
        </div>
        <img 
          v-if="room.photos.length" 
          :src="getMainPhoto(room.photos)" 
          class="room-thumb"
        >
        <div class="room-actions">
          <button @click.stop="$emit('toggle-price', room)" title="Управление ценами">💰</button>
          <button @click.stop="$emit('toggle-booking', room)" title="Бронирования">📅</button>
          <button @click="$emit('select-room', room)" title="Редактировать">✏️</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    rooms: Array,
    selectedRoomId: Number
  },
  methods: {
    getMainPhoto(photos) {
      const main = photos.find(p => p.is_main);
      return main ? this.getPhotoUrl(main.url) : this.getPhotoUrl(photos[0]?.url);
    },
    getPhotoUrl(url) {
      return `http://localhost:8000${url}`;
    }
  }
};
</script>

<style scoped>
.section-card {
  background: #fff;
  border-radius: 10px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.1);
  border: 1px solid #eee;
}

.rooms-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.add-button {
  background: #4CAF50;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
  font-weight: 500;
}

.add-button:hover {
  background: #45a049;
}

.room-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.room-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  background: #fff;
}

.room-card.selected {
  box-shadow: 0 0 0 2px #2196F3;
  transform: translateY(-2px);
}

.room-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.room-header {
  padding: 1rem;
  background: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.room-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
}

.room-header button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #e74c3c;
  transition: transform 0.2s;
}

.room-header button:hover {
  transform: scale(1.1);
}

.room-thumb {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}

.room-actions {
  display: flex;
  justify-content: center;
  padding: 0.8rem;
  background: #f8f9fa;
  border-top: 1px solid #eee;
}

.room-actions button {
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 0.8rem;
  margin: 0 0.3rem;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 1rem;
}

.room-actions button:hover {
  background: #2980b9;
}

/* Адаптивность */
@media (max-width: 768px) {
  .rooms-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .room-list {
    grid-template-columns: 1fr;
  }
  
  .add-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .section-card {
    padding: 15px;
  }
  
  .room-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .room-actions button {
    flex: 1;
    min-width: 60px;
  }
}
</style>