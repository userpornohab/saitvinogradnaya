<template>
  <div class="photo-management">
    <h4>Фотографии номера</h4>
    
    <div class="photo-grid">
      <div v-for="photo in photos" :key="photo.id" class="photo-card">
        <img :src="getPhotoUrl(photo.url)" class="photo-preview">
        <div class="photo-controls">
          <button 
            @click="$emit('set-main-photo', photo)" 
            :class="{active: photo.is_main}"
            title="Сделать главной"
          >
            ★
          </button>
          <button 
            @click="$emit('delete-photo', photo)"
            title="Удалить"
          >
            ×
          </button>
        </div>
      </div>
    </div>
    
    <div class="upload-section">
      <label class="file-input-label">
        <input 
          type="file" 
          @change="handleFileSelect" 
          accept="image/*" 
          multiple
          class="hidden-input"
        >
        <span class="button-content">
          <svg class="upload-icon" viewBox="0 0 24 24">
            <path d="M19 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5l-1-1v6a3 3 0 0 0 3 3h12a3 3 0 0 0 3-3v-6l-1 1z"/>
            <path d="M12 15l5-6h-3V2h-4v7H7l5 6z"/>
          </svg>
          {{ selectedFiles.length > 0 ? `Выбрано: ${selectedFiles.length}` : 'Выберите фотографии' }}
        </span>
      </label>
      <button 
        @click="uploadPhotos" 
        :disabled="selectedFiles.length === 0"  
        class="upload-button"
      >
        Загрузить
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    photos: Array
  },
  emits: ['upload-photo', 'set-main-photo', 'delete-photo'],
  data() {
    return {
      selectedFiles: []
    };
  },
  methods: {
    getPhotoUrl(url) {
      return `http://localhost:8000${url}`;
    },
    
    handleFileSelect(event) {
      this.selectedFiles = Array.from(event.target.files);
    },
    
    uploadPhotos() {
      if (this.selectedFiles.length === 0) return;
      
      this.$emit('upload-photo', this.selectedFiles);
      this.selectedFiles = [];
    }
  }
};
</script>

<style scoped>
.photo-management {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

h4 {
  margin-top: 0;
  margin-bottom: 1.2rem;
  color: #2c3e50;
  font-size: 1.2rem;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.2rem;
  margin-bottom: 1.5rem;
}

.photo-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
  aspect-ratio: 4/3;
}

.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s;
}

.photo-card:hover .photo-preview {
  transform: scale(1.05);
}

.photo-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.8rem;
  background: rgba(0,0,0,0.6);
  opacity: 0;
  transition: opacity 0.3s;
}

.photo-card:hover .photo-controls {
  opacity: 1;
}

.photo-controls button {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(255,255,255,0.9);
  color: #333;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.photo-controls button:hover {
  background: white;
  transform: scale(1.1);
}

.photo-controls button.active {
  background: #f1c40f;
  color: white;
}

.upload-section {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  padding: 0.8rem 1.2rem;
  background: #f0f4f8;
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-grow: 1;
}

.file-input-label:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  color: #4a5568;
  font-weight: 500;
}

.upload-icon {
  width: 20px;
  height: 20px;
  fill: #4a5568;
}

.hidden-input {
  display: none;
}

.upload-button {
  padding: 0.8rem 1.8rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
  font-weight: 500;
}

.upload-button:hover:not(:disabled) {
  background: #2980b9;
}

.upload-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* Адаптивность */
@media (max-width: 768px) {
  .upload-section {
    flex-direction: column;
  }
  
  .upload-button {
    width: 100%;
  }
  
  .photo-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style> 