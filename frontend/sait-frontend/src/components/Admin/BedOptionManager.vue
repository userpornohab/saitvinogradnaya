<template>
  <div class="form-group full-width border-bot">
    <div class="manage-section">
      <div class="section-header">
        <h4>Типы кроватей</h4>
        <div class="selection-grid">
          <div v-for="bed in allBedOptions" :key="bed.id" class="selection-item">
            <label>
              <input 
                type="checkbox" 
                :value="bed.id" 
                :checked="isSelected(bed.id)"
                @change="toggleBedSelection(bed.id, $event.target.checked)"
              >
              <img :src="getIconUrl(bed.icon)" :alt="bed.name" class="icon-small">
              {{ bed.name }}
              <button 
                @click.stop="$emit('delete-bed-option', bed.id)" 
                class="delete-btn"
                title="Удалить тип кровати"
              >
                ×
              </button>
            </label>
          </div>
        </div>
        <button type="button" @click="showForm = !showForm">
          {{ showForm ? 'Скрыть' : 'Добавить' }}
        </button>
      </div>
      
      <div v-if="showForm" class="add-form">
        <input v-model="newBedOption.name" placeholder="Название типа кровати">
        <div class="add-form-marg">
          <div class="custom-file-input">
            <label class="file-input-label">
              <input 
                type="file" 
                @change="handleIconChange"
                accept="image/svg+xml, image/png"
                class="hidden-input"
              >
              <span class="button-content">
                <svg class="upload-icon" viewBox="0 0 24 24">
                  <path d="M19 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5l-1-1v6a3 3 0 0 0 3 3h12a3 3 0 0 0 3-3v-6l-1 1z"/>
                  <path d="M12 15l5-6h-3V2h-4v7H7l5 6z"/>
                </svg>
                {{ newBedOption.iconFile ? newBedOption.iconFile.name : 'Выберите иконку' }}
              </span>
            </label>
          </div>
          <button type="button" @click="addNewBedOption">Добавить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    allBedOptions: Array,
    selectedBedOptions: Array
  },
  emits: ['update:selected-bed-options', 'add-bed-option', 'delete-bed-option'],
  data() {
    return {
      showForm: false,
      newBedOption: {
        name: '',
        iconFile: null
      }
    };
  },
  methods: {
    isSelected(bedId) {
      return this.selectedBedOptions.includes(bedId);
    },
    
    toggleBedSelection(bedId, isChecked) {
      const newSelection = [...this.selectedBedOptions];
      
      if (isChecked) {
        newSelection.push(bedId);
      } else {
        const index = newSelection.indexOf(bedId);
        if (index > -1) {
          newSelection.splice(index, 1);
        }
      }
      
      this.$emit('update:selected-bed-options', newSelection);
    },
    
    getIconUrl(icon) {
      return `http://127.0.0.1:8000/${icon}`;
    },
    
    handleIconChange(event) {
      this.newBedOption.iconFile = event.target.files[0];
    },
    
    addNewBedOption() {
      if (!this.newBedOption.name.trim()) {
        alert('Введите название типа кровати');
        return;
      }
      
      if (!this.newBedOption.iconFile) {
        alert('Выберите иконку');
        return;
      }
      
      this.$emit('add-bed-option', {
        name: this.newBedOption.name,
        iconFile: this.newBedOption.iconFile
      });
      
      // Сбросить форму
      this.newBedOption = {
        name: '',
        iconFile: null
      };
    }
  }
};
</script>

<style scoped>
/* Стили идентичны AmenityManager */
.manage-section {
  margin-top: 1.5rem;
}

.section-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
  min-width: 120px;
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
  flex-grow: 1;
}

.selection-item {
  position: relative;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
  background: #f8f9fa;
}

.selection-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.selection-item label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.icon-small {
  width: 30px;
  height: 30px;
  object-fit: contain;
  margin: 0 10px;
}

.delete-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  transition: transform 0.2s;
}

.delete-btn:hover {
  transform: scale(1.2);
}

.add-form {
  margin-top: 1.5rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8f9fa;
}

.add-form input {
  width: 100%;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.add-form-marg {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.custom-file-input {
  flex-grow: 1;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  padding: 0.8rem;
  background: #f0f4f8;
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
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

button {
  padding: 0.7rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background: #2980b9;
}

/* Адаптивность */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .add-form-marg {
    flex-direction: column;
  }
  
  button {
    width: 100%;
  }
}
</style>