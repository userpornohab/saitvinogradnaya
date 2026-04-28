<template>
  <div class="section-card">
    <div class="edit-header">
      <h3>Управление ценами — {{ room.title }}</h3>
      <button @click="$emit('close')" class="btn-close">✕</button>
    </div>

    <div class="price-controls">
      <SyncDateRangePicker
        v-model:start-date="startDate"
        v-model:end-date="endDate"
        :number-of-rooms="room?.number_of_rooms"
        :price-periods="room.price_periods || []"
        :show-availability="false"
        :highlight-price-periods="true"
        @clear="onClearDates"
      />

      <div class="price-controls-row">
        <button class="btn-outline" @click="$emit('copy-next-year')" :disabled="isCopying || !room.price_periods?.length">
          {{ isCopying ? 'Копирование...' : 'Копировать на след. год' }}
        </button>
        <span class="price-hint">Выберите диапазон дат в календаре — откроется форма установки цены.</span>
      </div>
    </div>

    <!-- Модальное окно с формой цены -->
    <transition name="modal-fade">
      <div v-if="showPriceModal" class="pm-modal-backdrop" @mousedown.self="closeModal">
        <div class="pm-modal" role="dialog" aria-modal="true">
          <div class="pm-modal-header">
            <div>
              <h4>Установить цену</h4>
              <p class="pm-modal-range">{{ formattedRange }}</p>
            </div>
            <button @click="closeModal" class="btn-close" aria-label="Закрыть">✕</button>
          </div>

          <div class="price-input-group">
            <label class="field">
              <span>Цена за ночь, ₽</span>
              <input type="number" v-model.number="price" placeholder="Например, 3500" min="1" class="price-input" ref="priceInput">
            </label>
            <label class="field">
              <span>Количество гостей</span>
              <input type="number" v-model.number="guests" placeholder="1" min="1" :max="room.max_guests" class="price-input">
            </label>
          </div>

          <div class="pm-modal-actions">
            <button class="btn-outline" @click="closeModal">Отмена</button>
            <button class="btn-primary" @click="submitPrice" :disabled="!isValid">Сохранить</button>
          </div>
        </div>
      </div>
    </transition>

    <div class="periods-list">
      <div v-for="(yearPeriods, year) in groupedPeriods" :key="year" class="year-group">
        <div class="accordion-header" @click="toggleYear(year)">
          <h4>{{ year }} год ({{ yearPeriods.length }})</h4>
          <span class="accordion-icon">{{ openYears[year] ? '▼' : '▶' }}</span>
        </div>
        <transition name="slide">
          <div v-if="openYears[year]" class="accordion-content">
            <div v-for="period in yearPeriods" :key="period.id" class="period-item">
              <span class="dates">{{ formatDate(period.start_date) }} — {{ formatDate(period.end_date) }}</span>
              <span class="guests-badge">{{ period.number_of_guests }} гостей</span>
              <span class="price">{{ period.price }} ₽</span>
              <button class="delete-btn" @click.stop="$emit('delete-price', period.id)">×</button>
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
  name: 'PriceManagement',
  components: { SyncDateRangePicker },
  props: {
    room: { type: Object, required: true },
    isCopying: { type: Boolean, default: false }
  },
  data() {
    return {
      startDate: null,
      endDate: null,
      price: null,
      guests: null,
      openYears: {},
      showPriceModal: false
    }
  },
  watch: {
    startDate() { this.maybeOpenModal(); },
    endDate() { this.maybeOpenModal(); }
  },
  computed: {
    isValid() {
      return this.price > 0 && this.guests > 0 && this.startDate && this.endDate && this.startDate <= this.endDate;
    },
    formattedRange() {
      if (!this.startDate || !this.endDate) return '';
      return `${this.formatDate(this.startDate)} — ${this.formatDate(this.endDate)}`;
    },
    groupedPeriods() {
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
    toggleYear(year) {
      this.openYears = { ...this.openYears, [year]: !this.openYears[year] };
    },
    formatDate(dateString) {
      const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    },
    maybeOpenModal() {
      if (this.startDate && this.endDate && this.startDate <= this.endDate) {
        this.showPriceModal = true;
        this.$nextTick(() => this.$refs.priceInput?.focus());
      }
    },
    closeModal() {
      this.showPriceModal = false;
      this.resetForm();
      this.$emit('reset');
    },
    onClearDates() {
      this.showPriceModal = false;
      this.resetForm();
      this.$emit('reset');
    },
    resetForm() {
      this.startDate = null;
      this.endDate = null;
      this.price = null;
      this.guests = null;
    },
    submitPrice() {
      if (!this.isValid) return;
      this.$emit('create-price', {
        startDate: this.startDate,
        endDate: this.endDate,
        price: this.price,
        guests: this.guests
      });
      this.showPriceModal = false;
      this.resetForm();
    }
  },
  mounted() {
    const currentYear = new Date().getFullYear();
    this.openYears = { [currentYear]: true };
  }
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

.edit-header h3 { margin: 0; font-size: var(--text-xl); font-weight: 600; color: var(--color-gray-900); }

.btn-close {
  width: 36px; height: 36px; border-radius: var(--radius-full);
  display: flex; align-items: center; justify-content: center;
  background: var(--color-gray-100); border: none; cursor: pointer; font-size: var(--text-lg);
}
.btn-close:hover { background: var(--color-error-soft); color: var(--color-error); }

.price-controls { display: flex; flex-direction: column; gap: var(--spacing-lg); margin-bottom: var(--spacing-xl); }

.price-controls-row {
  display: flex; flex-wrap: wrap; gap: var(--spacing-md); align-items: center; justify-content: space-between;
}
.price-hint {
  font-size: var(--text-sm); color: var(--color-gray-500);
}

.price-input-group {
  display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);
}
.price-input-group .field { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.price-input-group .field span { font-size: var(--text-sm); font-weight: 600; color: var(--color-gray-700); }
.price-input-group .price-input { width: 100%; }

/* === Модальное окно цены === */
.pm-modal-backdrop {
  position: fixed; inset: 0; z-index: 1050;
  background: rgba(20, 20, 24, 0.55);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: var(--spacing-lg);
}
.pm-modal {
  width: 100%; max-width: 480px;
  background: var(--color-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  padding: var(--spacing-xl);
  display: flex; flex-direction: column; gap: var(--spacing-lg);
}
.pm-modal-header {
  display: flex; justify-content: space-between; align-items: flex-start; gap: var(--spacing-md);
}
.pm-modal-header h4 { margin: 0; font-size: var(--text-xl); font-weight: 700; color: var(--color-gray-900); }
.pm-modal-range { margin: 4px 0 0; font-size: var(--text-sm); color: var(--color-primary); font-weight: 600; }
.pm-modal-actions {
  display: flex; justify-content: flex-end; gap: var(--spacing-md);
}
.pm-modal-actions .btn-primary, .pm-modal-actions .btn-outline { min-width: 120px; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity var(--transition-base); }
.modal-fade-enter-active .pm-modal, .modal-fade-leave-active .pm-modal { transition: transform var(--transition-base); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .pm-modal, .modal-fade-leave-to .pm-modal { transform: translateY(8px) scale(0.98); }

.price-input {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  width: 120px;
}
.price-input:focus { outline: none; border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-soft); }

.price-actions { display: flex; gap: var(--spacing-md); flex-wrap: wrap; }

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary); color: white; border: none; border-radius: var(--radius-md);
  font-weight: 500; cursor: pointer; transition: all var(--transition-fast);
}
.btn-primary:hover { background: var(--color-primary-dark); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-outline {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px solid var(--color-gray-300); border-radius: var(--radius-md);
  background: var(--color-white); cursor: pointer; transition: all var(--transition-fast);
}
.btn-outline:hover { border-color: var(--color-primary); color: var(--color-primary); }
.btn-outline:disabled { opacity: 0.5; cursor: not-allowed; }

.periods-list { margin-top: var(--spacing-lg); }

.year-group { margin-bottom: var(--spacing-md); }

.accordion-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-gray-50); border-radius: var(--radius-md);
  cursor: pointer; transition: background var(--transition-fast);
}
.accordion-header:hover { background: var(--color-gray-100); }
.accordion-header h4 { margin: 0; font-size: var(--text-sm); font-weight: 600; }

.period-item {
  display: flex; align-items: center; gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-gray-200); border-top: none;
  border-radius: 0 0 var(--radius-md) var(--radius-md);
}

.dates { font-size: var(--text-sm); color: var(--color-gray-600); }
.guests-badge { font-size: var(--text-xs); padding: 2px 8px; background: var(--color-info-soft); color: var(--color-info); border-radius: var(--radius-full); }
.price { font-weight: 600; color: var(--color-gray-900); margin-left: auto; }

.delete-btn {
  width: 28px; height: 28px; border-radius: var(--radius-full);
  background: var(--color-error-soft); color: var(--color-error); border: none;
  cursor: pointer; font-size: var(--text-lg); display: flex; align-items: center; justify-content: center;
}
.delete-btn:hover { background: var(--color-error); color: white; }

.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; max-height: 500px; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }

@media (max-width: 768px) {
  .price-input-group { grid-template-columns: 1fr; }
  .pm-modal { padding: var(--spacing-lg); }
  .pm-modal-actions { flex-direction: column-reverse; }
  .pm-modal-actions .btn-primary, .pm-modal-actions .btn-outline { width: 100%; }
  .price-controls-row { flex-direction: column; align-items: stretch; }
}
</style>
