<template>
  <div class="section-card">
    <div class="edit-header">
      <h3>{{ isNew ? 'Новый номер' : `Редактирование: ${room.title}` }}</h3>
      <button v-if="!isNew" @click="$emit('cancel')" class="btn-close">✕</button>
    </div>

    <form @submit.prevent="handleSubmit" class="room-form">
      <div class="form-grid">
        <div class="form-group">
          <label>Название</label>
          <input v-model="formData.title" required placeholder="Например: Стандарт">
        </div>

        <div class="form-group">
          <label>Доп. название</label>
          <input v-model="formData.title_dop" placeholder="Расширенное название">
        </div>

        <div class="form-group full-width">
          <label>Описание</label>
          <textarea v-model="formData.description" required rows="4" placeholder="Описание номера..."></textarea>
        </div>

        <div class="form-group">
          <label>Макс. гостей</label>
          <input type="number" v-model.number="formData.max_guests" min="1" required>
        </div>

        <div class="form-group">
          <label>Этаж</label>
          <input type="number" v-model.number="formData.floor" min="1" required>
        </div>

        <div class="form-group">
          <label>Количество номеров</label>
          <input type="number" v-model.number="formData.number_of_rooms" min="1" required>
        </div>
      </div>

      <!-- Удобства -->
      <div class="form-section">
        <div class="form-section-header">
          <h4>Удобства</h4>
          <button type="button" @click="$emit('toggle-amenity-form')" class="btn-sm">
            {{ showAmenityForm ? 'Скрыть' : 'Добавить' }}
          </button>
        </div>

        <div class="selection-grid">
          <div
            v-for="amenity in amenities"
            :key="amenity.id"
            class="selection-item"
            :class="{ selected: isSelected('amenities', amenity.id) }"
          >
            <label>
              <input
                type="checkbox"
                :value="amenity.id"
                :checked="isSelected('amenities', amenity.id)"
                @change="$emit('toggle-amenity', amenity.id)"
              >
              <img :src="getIconUrl(amenity.icon)" :alt="amenity.name" class="icon-small">
              <span>{{ amenity.name }}</span>
            </label>
            <button type="button" @click.stop="$emit('delete-amenity', amenity.id)" class="delete-badge" title="Удалить">×</button>
          </div>
        </div>

        <div v-if="showAmenityForm" class="add-form">
          <input v-model="newAmenityName" placeholder="Название удобства" class="form-input">
          <div class="add-form-row">
            <label class="file-upload">
              <input type="file" @change="onAmenityIcon" accept="image/svg+xml, image/png" hidden>
              <span class="btn-outline">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                </svg>
                {{ newAmenityIcon ? newAmenityIcon.name : 'Выбрать иконку' }}
              </span>
            </label>
            <button type="button" @click="$emit('add-amenity', { name: newAmenityName, iconFile: newAmenityIcon })" class="btn-primary btn-sm">Добавить</button>
          </div>
        </div>
      </div>

      <!-- Типы кроватей -->
      <div class="form-section">
        <div class="form-section-header">
          <h4>Типы кроватей</h4>
          <button type="button" @click="$emit('toggle-bed-form')" class="btn-sm">
            {{ showBedForm ? 'Скрыть' : 'Добавить' }}
          </button>
        </div>

        <div class="selection-grid">
          <div
            v-for="bed in bedOptions"
            :key="bed.id"
            class="selection-item"
            :class="{ selected: isSelected('bed_options', bed.id) }"
          >
            <label>
              <input
                type="checkbox"
                :value="bed.id"
                :checked="isSelected('bed_options', bed.id)"
                @change="$emit('toggle-bed', bed.id)"
              >
              <img :src="getIconUrl(bed.icon)" :alt="bed.name" class="icon-small">
              <span>{{ bed.name }}</span>
            </label>
            <button type="button" @click.stop="$emit('delete-bed', bed.id)" class="delete-badge" title="Удалить">×</button>
          </div>
        </div>

        <div v-if="showBedForm" class="add-form">
          <input v-model="newBedName" placeholder="Название типа кровати" class="form-input">
          <div class="add-form-row">
            <label class="file-upload">
              <input type="file" @change="onBedIcon" accept="image/svg+xml, image/png" hidden>
              <span class="btn-outline">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                </svg>
                {{ newBedIcon ? newBedIcon.name : 'Выбрать иконку' }}
              </span>
            </label>
            <button type="button" @click="$emit('add-bed', { name: newBedName, iconFile: newBedIcon })" class="btn-primary btn-sm">Добавить</button>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary">{{ isNew ? 'Создать' : 'Обновить' }}</button>
        <button type="button" @click="$emit('cancel')" v-if="!isNew" class="btn-outline">Отмена</button>
      </div>
    </form>

    <!-- Управление фотографиями -->
    <div v-if="!isNew && room.photos" class="photo-section">
      <h4>Фотографии номера</h4>
      <div class="photo-grid">
        <div v-for="photo in room.photos" :key="photo.id" class="photo-card">
          <img :src="getPhotoUrl(photo.url)" class="photo-preview" :alt="room.title">
          <div class="photo-controls">
            <button
              @click="$emit('set-main-photo', photo)"
              :class="{ active: photo.is_main }"
              title="Главное фото"
            >★</button>
            <button @click="$emit('delete-photo', photo)" title="Удалить">×</button>
          </div>
        </div>
      </div>
      <div class="upload-section">
        <label class="file-upload">
          <input type="file" @change="$emit('photo-upload', $event)" accept="image/*" multiple hidden ref="fileInput">
          <span class="btn-outline">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            Загрузить фото
          </span>
        </label>
        <button @click="$emit('upload-photos')" :disabled="!hasFiles" class="btn-primary">
          Загрузить ({{ fileCount }})
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '@/api';
export default {
  name: 'RoomEditor',
  emits: ['submit', 'cancel', 'toggle-amenity-form', 'toggle-bed-form', 'toggle-amenity', 'toggle-bed', 'add-amenity', 'add-bed', 'upload-photos', 'update-form'],
  props: {
    room: { type: Object, default: null },
    isNew: { type: Boolean, default: false },
    amenities: { type: Array, required: true },
    bedOptions: { type: Array, required: true },
    selectedAmenities: { type: Array, required: true },
    selectedBeds: { type: Array, required: true },
    showAmenityForm: { type: Boolean, default: false },
    showBedForm: { type: Boolean, default: false },
    fileCount: { type: Number, default: 0 }
  },
  data() {
    return {
      formData: {
        title: '',
        title_dop: '',
        description: '',
        max_guests: 2,
        floor: 1,
        number_of_rooms: 1
      },
      newAmenityName: '',
      newAmenityIcon: null,
      newBedName: '',
      newBedIcon: null
    }
  },
  watch: {
    room: {
      immediate: true,
      handler(room) {
        if (room) {
          this.formData = {
            title: room.title || '',
            title_dop: room.title_dop || '',
            description: room.description || '',
            max_guests: room.max_guests || 2,
            floor: room.floor || 1,
            number_of_rooms: room.number_of_rooms || 1
          }
        }
      }
    },
    formData: {
      deep: true,
      handler(formData) {
        this.$emit('update-form', { ...formData })
      }
    }
  },
  computed: {
    hasFiles() {
      return this.fileCount > 0;
    }
  },
  methods: {
    handleSubmit() {
      console.log('RoomEditor handleSubmit - formData:', JSON.stringify(this.formData));
      this.$emit('submit', { ...this.formData });
    },
    isSelected(type, id) {
      if (type === 'amenities') return this.selectedAmenities.includes(id);
      if (type === 'bed_options') return this.selectedBeds.includes(id);
      return false;
    },
    getIconUrl(icon) {
      return `${API_BASE_URL}/${icon}`;
    },
    getPhotoUrl(url) {
      return `${API_BASE_URL}${url}`;
    },
    onAmenityIcon(e) {
      this.newAmenityIcon = e.target.files[0];
    },
    onBedIcon(e) {
      this.newBedIcon = e.target.files[0];
    }
  },
  emits: ['submit', 'cancel', 'toggle-amenity', 'toggle-bed', 'toggle-amenity-form', 'toggle-bed-form',
          'add-amenity', 'add-bed', 'delete-amenity', 'delete-bed', 'set-main-photo', 'delete-photo',
          'photo-upload', 'upload-photos']
}
</script>

<style scoped>
.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-gray-200);
}

.edit-header h3 {
  margin: 0;
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-gray-900);
}

.btn-close {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-100);
  border: none;
  cursor: pointer;
  font-size: var(--text-lg);
  transition: all var(--transition-fast);
}

.btn-close:hover {
  background: var(--color-error-soft);
  color: var(--color-error);
}

.room-form {
  /* Form styles */
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-group label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-gray-700);
}

.form-group input,
.form-group textarea {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: all var(--transition-fast);
  font-family: var(--font-family-base);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-section {
  padding: var(--spacing-lg) 0;
  border-top: 1px solid var(--color-gray-200);
}

.form-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.form-section-header h4 {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 600;
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.selection-item {
  position: relative;
  padding: var(--spacing-md);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}

.selection-item.selected {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
}

.selection-item label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  cursor: pointer;
  font-size: var(--text-sm);
  text-align: center;
}

.icon-small {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.delete-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: var(--radius-full);
  background: var(--color-error);
  color: white;
  border: none;
  cursor: pointer;
  font-size: var(--text-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.selection-item:hover .delete-badge {
  opacity: 1;
}

.add-form {
  padding: var(--spacing-md);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.add-form-row {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.file-upload {
  flex: 1;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  background: var(--color-white);
  color: var(--color-gray-700);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-outline:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-gray-300);
  background: var(--color-white);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-sm:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-gray-200);
}

/* Photo section */
.photo-section {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-gray-200);
}

.photo-section h4 {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.photo-card {
  position: relative;
  aspect-ratio: 4/3;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.photo-card:hover .photo-controls {
  opacity: 1;
}

.photo-controls button {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--color-white);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-lg);
  transition: all var(--transition-fast);
}

.photo-controls button.active {
  background: var(--color-warning);
  color: white;
}

.upload-section {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  padding: var(--spacing-md);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .selection-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .photo-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
  }

  .upload-section {
    flex-direction: column;
  }
}
</style>
