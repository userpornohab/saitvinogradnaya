<template>
  <div class="section-card price-management">
    <div class="edit-header">
      <h3>Управление ценами для {{ room.title }}</h3>
      <button @click="$emit('close')">×</button>
    </div>

    <div class="price-controls">
      <!-- Используем оригинальный SyncDateRangePicker -->
      <SyncDateRangePicker 
        v-model:start-date="startDate"
        v-model:end-date="endDate"
        :number-of-rooms="room?.number_of_rooms"
        @clear="resetForm"
      />
      
      <div class="price-input-group">
        <input 
          type="number" 
          v-model.number="price" 
          placeholder="Цена"
          min="1"
          class="price-input"
        >
        <input 
          type="number" 
          v-model.number="guests" 
          placeholder="гостей"
          min="1"
          :max="room.max_guests"
          class="price-input"
        >
        
        <div class="price-actions">
          <button 
            class="copy-button"
            @click="createPeriod"
            :disabled="!isFormValid"
          >
            Установить цену
          </button>
          
          <button 
            class="copy-button"
            @click="$emit('copy-periods')"
            :disabled="isCopying || !room.price_periods.length"
          >
            {{ isCopying ? 'Копирование...' : 'Копировать на следующий год' }}
          </button>
        </div>
      </div>
    </div>

    <div class="periods-list">
      <div v-for="(yearPeriods, year) in groupedPricePeriods" :key="year" class="year-group">
        <div class="accordion-header" @click="toggleYear(year)">
          <h4>Ценовые периоды за {{ year }} год</h4>
          <span class="accordion-icon">
            {{ openYears[year] ? '▼' : '▶' }}
          </span>
        </div>
        
        <transition name="slide">
          <div v-if="openYears[year]" class="accordion-content">
            <div v-for="period in yearPeriods" :key="period.id" class="period-item">
              <div class="period-info">
                <span class="dates">{{ formatDate(period.start_date) }} - {{ formatDate(period.end_date) }}</span>
                <span class="guests">за {{ period.number_of_guests }} гостей</span>
                <span class="price">{{ period.price }} ₽</span>
              </div>
              <button 
                class="delete-btn"
                @click.stop="$emit('delete-period', period.id)"
                title="Удалить период"
              >
                ×
              </button>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import SyncDateRangePicker from './SyncDateRangePicker.vue';

export default {
  components: {
    SyncDateRangePicker
  },
  props: {
    room: Object,
    isCopying: Boolean
  },
  emits: ['close', 'create-period', 'delete-period', 'copy-periods'],
  data() {
    return {
      startDate: null,
      endDate: null,
      price: null,
      guests: null,
      openYears: {},
      minDate: new Date().toISOString().split('T')[0]
    };
  },
  computed: {
    isFormValid() {
      return this.price > 0 && 
             this.guests > 0 &&
             this.startDate && 
             this.endDate && 
             this.startDate <= this.endDate;
    },
    
    groupedPricePeriods() {
      if (!this.room?.price_periods) return {};
      
      return this.room.price_periods.reduce((groups, period) => {
        const year = new Date(period.start_date).getFullYear();
        if (!groups[year]) groups[year] = [];
        groups[year].push(period);
        return groups;
      }, {});
    }
  },
  methods: {
    formatDate(dateString) {
      const options = { day: '2-digit', month: '2-digit' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    },
    
    toggleYear(year) {
      this.openYears = {
        ...this.openYears,
        [year]: !this.openYears[year]
      };
    },
    
    createPeriod() {
      if (!this.isFormValid) return;
      
      const periodData = {
        start_date: this.startDate,
        end_date: this.endDate,
        price: this.price,
        number_of_guests: this.guests
      };
      
      this.$emit('create-period', periodData);
      this.resetForm();
    },
    
    resetForm() {
      this.startDate = null;
      this.endDate = null;
      this.price = null;
      this.guests = null;
    }
  },
  mounted() {
    // Открываем текущий год по умолчанию
    const currentYear = new Date().getFullYear();
    this.openYears = { [currentYear]: true };
  }
};
</script>

<style scoped>
/* Стили остаются такими же, как в предыдущей версии */
.price-management {
  position: relative;
  z-index: 100;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
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
  font-size: 1.3rem;
  color: #2c3e50;
}

.edit-header button {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #777;
  transition: color 0.2s;
  line-height: 1;
}

.edit-header button:hover {
  color: #e74c3c;
}

.price-controls {
  padding: 20ppx;
  border-bottom: 1px solid #eee;
}

@media (max-width: 900px) {
  .price-controls {
    grid-template-columns: 1fr;
  }
}

.price-input-group {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
  font-size: 0.9rem;
}

input[type="number"] {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input[type="number"]:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.price-input {
  width: 100%;
}

.price-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.copy-button {
  background-color: #9b59b6;
  color: white;
  padding: 0.9rem 1.2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-weight: 500;
  font-size: 1rem;
  text-align: center;
}

.copy-button:hover:not(:disabled) {
  background-color: #8e44ad;
}

.copy-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.7;
}

.periods-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

.year-group {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.2rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #f8f9fa;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}

.accordion-header:hover {
  background: #e9ecef;
}

.accordion-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
  font-weight: 600;
}

.accordion-icon {
  font-size: 14px;
  color: #666;
  transition: transform 0.3s;
}

.accordion-content {
  padding: 10px 15px;
  background: #fff;
}

.period-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 10px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.2s;
}

.period-item:last-child {
  border-bottom: none;
}

.period-item:hover {
  background: #f8f9fa;
}

.period-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.dates {
  font-weight: 500;
  color: #333;
  min-width: 180px;
}

.guests {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.price {
  font-weight: 600;
  color: #27ae60;
  min-width: 100px;
  text-align: right;
}

.delete-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: #e74c3c;
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 1.4rem;
}

.delete-btn:hover {
  background: #ffebee;
  transform: scale(1.1);
}

/* Анимации */
.slide-enter-active {
  animation: slideDown 0.3s ease;
}

.slide-leave-active {
  animation: slideDown 0.3s ease reverse;
}

@keyframes slideDown {
  0% {
    max-height: 0;
    opacity: 0;
    transform: translateY(-10px);
  }
  100% {
    max-height: 500px;
    opacity: 1;
    transform: translateY(0);
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .price-controls {
    gap: 1.5rem;
  }
  
  .period-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .dates, .guests, .price {
    min-width: auto;
  }
}
</style>