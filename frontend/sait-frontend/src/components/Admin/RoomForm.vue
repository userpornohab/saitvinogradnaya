<template>
  <div class="section-card">
    <div class="edit-header">
      <h3>{{ isNewRoom ? 'Новый номер' : `Редактирование: ${room.title}` }}</h3>
      <button v-if="!isNewRoom" @click="$emit('cancel')">×</button>
    </div>

    <form @submit.prevent="submitForm" class="border-bot">
      <div class="form-grid">
        <!-- Основные поля -->
        <div class="form-group">
          <label>Название:</label>
          <input v-model="formData.title" required>
        </div>
        
        <div class="form-group">
          <label>Доп. название:</label>
          <input v-model="formData.title_dop">
        </div>
        
        <div class="form-group">
          <label>Описание:</label>
          <textarea v-model="formData.description" required rows="4"></textarea>
        </div>
        
        <div class="form-group">
          <label>Макс. гостей:</label>
          <input type="number" v-model.number="formData.max_guests" min="1" required>
        </div>
        
        <div class="form-group">
          <label>Этаж:</label>
          <input type="number" v-model.number="formData.floor" min="1" required>
        </div>
        
        <div class="form-group">
          <label>Количество номеров:</label>
          <input type="number" v-model.number="formData.number_of_rooms" min="1" required>
        </div>

        <!-- Управление удобствами -->
        <AmenityManager
          :all-amenities="allAmenities"
          :selected-amenities="formData.amenities"
          @update:selected-amenities="formData.amenities = $event"
          @add-amenity="addAmenity"
          @delete-amenity="$emit('delete-amenity', $event)"
        />

        <!-- Управление типами кроватей -->
        <BedOptionManager
          :all-bed-options="allBedOptions"
          :selected-bed-options="formData.bed_options"
          @update:selected-bed-options="formData.bed_options = $event"
          @add-bed-option="addBedOption"
          @delete-bed-option="$emit('delete-bed-option', $event)"
        />
      </div>

      <div class="form-actions">
        <button type="submit" class="submit-button">
          {{ isNewRoom ? 'Создать' : 'Обновить' }}
        </button>
        <button type="button" @click="$emit('cancel')" v-if="!isNewRoom">Отмена</button>
      </div>
    </form>

    <!-- Управление фотографиями -->
    <PhotoManager 
      v-if="!isNewRoom"
      :photos="room.photos"
      @set-main-photo="$emit('set-main-photo', $event)"
      @delete-photo="$emit('delete-photo', $event)"
      @upload-photo="$emit('upload-photo', $event)"
    />
  </div>
</template>

<script>
import AmenityManager from './AmenityManager.vue';
import BedOptionManager from './BedOptionManager.vue';
import PhotoManager from './PhotoManager.vue';

export default {
  components: {
    AmenityManager,
    BedOptionManager,
    PhotoManager
  },
  props: {
    room: Object,
    isNewRoom: Boolean,
    allAmenities: Array,
    allBedOptions: Array
  },
  data() {
    return {
      formData: {
        title: '',
        title_dop: '',
        description: '',
        max_guests: 2,
        floor: 1,
        number_of_rooms: 1,
        amenities: [],
        bed_options: []
      }
    };
  },
  watch: {
    room: {
      immediate: true,
      handler(newRoom) {
        if (newRoom) {
          this.formData = {
            title: newRoom.title,
            title_dop: newRoom.title_dop || '',
            description: newRoom.description,
            max_guests: newRoom.max_guests,
            floor: newRoom.floor || 1,
            number_of_rooms: newRoom.number_of_rooms,
            amenities: newRoom.amenities?.map(a => a.id) || [],
            bed_options: newRoom.bed_options?.map(b => b.id) || []
          };
        }
      }
    }
  },
  methods: {
    submitForm() {
      this.$emit('submit', this.formData);
    },
    
    async addAmenity(amenity) {
      try {
        const newAmenity = await this.$emit('add-amenity', amenity);
        if (newAmenity) {
          this.formData.amenities.push(newAmenity.id);
        }
      } catch (error) {
        console.error('Error adding amenity:', error);
      }
    },
    
    async addBedOption(bedOption) {
      try {
        const newBedOption = await this.$emit('add-bed-option', bedOption);
        if (newBedOption) {
          this.formData.bed_options.push(newBedOption.id);
        }
      } catch (error) {
        console.error('Error adding bed option:', error);
      }
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

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.edit-header h3 {
  margin: 0;
  font-size: 1.4rem;
  color: #2c3e50;
}

.edit-header button {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #777;
  transition: color 0.2s;
}

.edit-header button:hover {
  color: #e74c3c;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
  font-size: 0.95rem;
}

input, textarea, select {
  box-sizing: border-box;
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

input:focus, textarea:focus, select:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

textarea {
  min-height: 100px;
  resize: vertical;
}

.border-bot {
  padding-bottom: 20px;
  border-bottom: 2px solid #eee;
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  gap: 15px;
  margin-top: 1.5rem;
}

.submit-button {
  background: #3498db;
  color: white;
  padding: 0.8rem 1.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: background 0.3s;
}

.submit-button:hover {
  background: #2980b9;
}

.form-actions button[type="button"] {
  background: #e0e0e0;
  color: #555;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: background 0.3s;
}

.form-actions button[type="button"]:hover {
  background: #d0d0d0;
}

/* Адаптивность */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .form-actions button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .section-card {
    padding: 15px;
  }
  
  .edit-header h3 {
    font-size: 1.2rem;
  }
}
</style>