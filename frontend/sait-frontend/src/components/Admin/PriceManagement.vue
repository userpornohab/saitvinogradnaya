<template>
  <div class="section-card">
    <div class="edit-header">
      <h3>Управление ценами — {{ room.title }}</h3>
      <button @click="$emit('close')" class="btn-close">✕</button>
    </div>

    <div class="price-workspace">
      <section class="price-calendar-panel" ref="calendarPanel">
        <SyncDateRangePicker
          v-model:start-date="startDate"
          v-model:end-date="endDate"
          :number-of-rooms="room?.number_of_rooms"
          :price-periods="room.price_periods || []"
          :show-availability="false"
          :highlight-price-periods="true"
          :highlight-start-date="hoveredPeriod?.start_date || null"
          :highlight-end-date="hoveredPeriod?.end_date || null"
          :focus-date="calendarFocusDate"
          :months-count="calendarMonthsCount"
          @clear="onClearDates"
        />
      </section>

      <aside class="price-side-panel">
        <div class="price-list-toolbar">
          <button class="btn-outline" @click="$emit('copy-next-year')" :disabled="isCopying || !room.price_periods?.length">
            {{ isCopying ? 'Копирование...' : 'Копировать на след. год' }}
          </button>
        </div>

        <div class="periods-list">
          <p v-if="!hasGroupedPeriods" class="periods-empty">
            Ценовых периодов пока нет
          </p>
          <div v-for="(yearPeriods, year) in groupedPeriods" :key="year" class="year-group">
            <div class="accordion-header" @click="toggleYear(year)">
              <h4>{{ year }} год ({{ yearPeriods.length }})</h4>
              <span class="accordion-icon">{{ openYears[year] ? '▼' : '▶' }}</span>
            </div>
            <transition name="slide">
              <div v-if="openYears[year]" class="accordion-content">
                <div
                  v-for="period in paginatedPeriods(yearPeriods, year)"
                  :key="period.id"
                  class="period-item"
                  @mouseenter="hoverPeriod(period)"
                  @mouseleave="clearHoveredPeriod"
                  @focusin="hoverPeriod(period)"
                  @focusout="clearHoveredPeriod"
                  @click="openEditModal(period)"
                >
                  <div class="period-info">
                    <span class="dates">{{ formatDate(period.start_date) }} — {{ formatDate(period.end_date) }}</span>
                    <div class="period-meta">
                      <span class="guests-badge">{{ period.number_of_guests }} гостей</span>
                      <span class="price">{{ period.price }} ₽</span>
                    </div>
                  </div>
                  <div class="period-actions">
                    <button type="button" class="btn-scroll-calendar" @click.stop="showPeriodOnCalendar(period)">К календарю</button>
                    <button class="delete-btn" @click.stop="$emit('delete-price', period.id)">Удалить</button>
                  </div>
                </div>

                <div v-if="totalPeriodPages(yearPeriods) > 1" class="period-pagination">
                  <button
                    type="button"
                    class="period-page-btn"
                    :disabled="periodPage(year) === 1"
                    @click="setPeriodPage(year, periodPage(year) - 1)"
                  >
                    ‹
                  </button>
                  <button
                    v-for="page in totalPeriodPages(yearPeriods)"
                    :key="`${year}-${page}`"
                    type="button"
                    class="period-page-btn"
                    :class="{ 'period-page-btn--active': periodPage(year) === page }"
                    @click="setPeriodPage(year, page)"
                  >
                    {{ page }}
                  </button>
                  <button
                    type="button"
                    class="period-page-btn"
                    :disabled="periodPage(year) === totalPeriodPages(yearPeriods)"
                    @click="setPeriodPage(year, periodPage(year) + 1)"
                  >
                    ›
                  </button>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </aside>
    </div>

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

    <transition name="modal-fade">
      <div v-if="showEditPriceModal && editingPeriod" class="pm-modal-backdrop" @mousedown.self="closeEditModal">
        <div class="pm-modal" role="dialog" aria-modal="true">
          <div class="pm-modal-header">
            <div>
              <h4>Редактирование цены</h4>
              <p class="pm-modal-range">{{ formatDate(editingPeriod.start_date) }} — {{ formatDate(editingPeriod.end_date) }}</p>
            </div>
            <button @click="closeEditModal" class="btn-close" aria-label="Закрыть">✕</button>
          </div>

          <div class="price-input-group">
            <label class="field">
              <span>Начало периода</span>
              <input type="date" v-model="editPeriodForm.start_date" class="price-input">
            </label>
            <label class="field">
              <span>Конец периода</span>
              <input type="date" v-model="editPeriodForm.end_date" class="price-input">
            </label>
            <label class="field">
              <span>Цена за ночь, ₽</span>
              <input type="number" v-model.number="editPeriodForm.price" min="1" class="price-input">
            </label>
            <label class="field">
              <span>Количество гостей</span>
              <input type="number" v-model.number="editPeriodForm.number_of_guests" min="1" :max="room.max_guests" class="price-input">
            </label>
          </div>

          <div class="pm-modal-actions">
            <button class="btn-outline" @click="closeEditModal">Отмена</button>
            <button class="btn-primary" @click="submitPeriodEdit" :disabled="!isEditValid">Сохранить</button>
          </div>
        </div>
      </div>
    </transition>
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
      showPriceModal: false,
      showEditPriceModal: false,
      editingPeriodId: null,
      editPeriodForm: {
        start_date: '',
        end_date: '',
        price: null,
        number_of_guests: 1
      },
      hoveredPeriodId: null,
      calendarFocusDate: null,
      isMobileViewport: false,
      periodsPerPage: 5,
      periodPages: {}
    }
  },
  watch: {
    startDate() { this.maybeOpenModal(); },
    endDate() { this.maybeOpenModal(); },
    room: {
      handler() { this.resetPeriodPages(); },
      deep: true
    }
  },
  computed: {
    isValid() {
      return this.price > 0 && this.guests > 0 && this.startDate && this.endDate && this.startDate <= this.endDate;
    },
    isEditValid() {
      return this.editPeriodForm.price > 0
        && this.editPeriodForm.number_of_guests > 0
        && this.editPeriodForm.start_date
        && this.editPeriodForm.end_date
        && this.editPeriodForm.start_date <= this.editPeriodForm.end_date;
    },
    formattedRange() {
      if (!this.startDate || !this.endDate) return '';
      return `${this.formatDate(this.startDate)} — ${this.formatDate(this.endDate)}`;
    },
    sortedPeriods() {
      return [...(this.room?.price_periods || [])].sort((a, b) => {
        const startDiff = new Date(a.start_date) - new Date(b.start_date);
        return startDiff || (a.number_of_guests || 0) - (b.number_of_guests || 0);
      });
    },
    groupedPeriods() {
      return this.sortedPeriods.reduce((groups, period) => {
        const year = new Date(period.start_date).getFullYear().toString();
        if (!groups[year]) groups[year] = [];
        groups[year].push(period);
        return groups;
      }, {});
    },
    hasGroupedPeriods() {
      return Object.keys(this.groupedPeriods).length > 0;
    },
    hoveredPeriod() {
      if (!this.hoveredPeriodId) return null;
      return this.sortedPeriods.find(period => period.id === this.hoveredPeriodId) || null;
    },
    editingPeriod() {
      if (!this.editingPeriodId) return null;
      return this.sortedPeriods.find(period => period.id === this.editingPeriodId) || null;
    },
    calendarMonthsCount() {
      return this.isMobileViewport ? 2 : 4;
    }
  },
  methods: {
    toggleYear(year) {
      this.openYears = { ...this.openYears, [year]: !this.openYears[year] };
    },
    periodPage(year) {
      return this.periodPages[year] || 1;
    },
    totalPeriodPages(periods) {
      return Math.max(1, Math.ceil(periods.length / this.periodsPerPage));
    },
    paginatedPeriods(periods, year) {
      const totalPages = this.totalPeriodPages(periods);
      const currentPage = Math.min(this.periodPage(year), totalPages);
      const start = (currentPage - 1) * this.periodsPerPage;
      return periods.slice(start, start + this.periodsPerPage);
    },
    setPeriodPage(year, page) {
      const periods = this.groupedPeriods[year] || [];
      const totalPages = this.totalPeriodPages(periods);
      const nextPage = Math.min(Math.max(page, 1), totalPages);
      this.periodPages = { ...this.periodPages, [year]: nextPage };
    },
    resetPeriodPages() {
      this.periodPages = {};
    },
    hoverPeriod(period) {
      this.hoveredPeriodId = period.id;
    },
    clearHoveredPeriod() {
      this.hoveredPeriodId = null;
    },
    showPeriodOnCalendar(period) {
      this.hoverPeriod(period);
      this.calendarFocusDate = period.start_date;
      this.$nextTick(() => {
        this.$refs.calendarPanel?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    },
    openEditModal(period) {
      this.editingPeriodId = period.id;
      this.hoverPeriod(period);
      this.editPeriodForm = {
        start_date: this.formatDateForInput(period.start_date),
        end_date: this.formatDateForInput(period.end_date),
        price: period.price,
        number_of_guests: period.number_of_guests
      };
      this.showEditPriceModal = true;
    },
    closeEditModal() {
      this.showEditPriceModal = false;
      this.editingPeriodId = null;
    },
    submitPeriodEdit() {
      if (!this.isEditValid || !this.editingPeriod) return;
      this.$emit('update-price', {
        id: this.editingPeriod.id,
        data: { ...this.editPeriodForm }
      });
      this.closeEditModal();
    },
    updateViewportState() {
      this.isMobileViewport = window.matchMedia('(max-width: 768px)').matches;
    },
    formatDate(dateString) {
      const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    },
    formatDateForInput(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '';
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
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
    this.updateViewportState();
    window.addEventListener('resize', this.updateViewportState);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updateViewportState);
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

.price-workspace {
  display: grid;
  grid-template-columns: minmax(640px, max-content) minmax(360px, 1fr);
  gap: var(--spacing-xl);
  align-items: start;
}

.price-calendar-panel,
.price-side-panel {
  min-width: 0;
}

.price-side-panel {
  width: 100%;
}

.price-list-toolbar {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  background: linear-gradient(135deg, rgba(198, 196, 253, 0.18), rgba(255, 255, 255, 0.95));
  border: 1px solid rgba(198, 196, 253, 0.45);
  border-radius: var(--radius-lg);
}

.price-hint {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
  line-height: 1.45;
}

.price-input-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}
.price-input-group .field { display: flex; flex-direction: column; gap: var(--spacing-xs); }
.price-input-group .field span { font-size: var(--text-sm); font-weight: 600; color: var(--color-gray-700); }
.price-input-group .price-input { width: 100%; }

.pm-modal-backdrop {
  position: fixed; inset: 0; z-index: 1050;
  background: rgba(20, 20, 24, 0.55);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: var(--spacing-lg);
}
.pm-modal {
  width: 100%; max-width: 540px;
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
}
.price-input:focus { outline: none; border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-soft); }

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

.periods-list { margin-top: var(--spacing-md); }

.periods-empty {
  margin: 0;
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--color-gray-500);
  background: var(--color-white);
  border: 1px dashed var(--color-gray-300);
  border-radius: var(--radius-lg);
}

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
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--spacing-md);
  align-items: center;
  padding: var(--spacing-md);
  margin-top: var(--spacing-sm);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-lg);
  background: var(--color-white);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.period-item:hover {
  border-color: #9b9aff;
  background-color: #dbdaff;
  box-shadow: 0 12px 30px rgba(76, 76, 247, 0.1);
  transform: translateY(-1px);
}

.period-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  min-width: 0;
}

.period-meta,
.period-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  align-items: center;
}

.dates { font-size: var(--text-sm); color: var(--color-gray-600); }
.guests-badge {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 4px 9px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(198, 196, 253, 0.45);
  color: #3730a3;
  border-radius: var(--radius-full);
}
.price {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 4px 9px;
  border-radius: var(--radius-full);
  background: var(--color-gray-50);
  border: 1px solid var(--color-gray-200);
  font-size: 12px;
  font-weight: 700;
  color: var(--color-success);
}

.btn-scroll-calendar {
  display: none;
  padding: var(--spacing-xs) var(--spacing-md);
  background: rgba(198, 196, 253, 0.35);
  color: #3730a3;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
}
.btn-scroll-calendar:hover { background: rgba(198, 196, 253, 0.65); }

.delete-btn {
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--color-error-soft);
  color: var(--color-error);
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  cursor: pointer;
}
.delete-btn:hover { background: var(--color-error); color: white; }

.period-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) 0 0;
}

.period-page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 var(--spacing-xs);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-gray-700);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.period-page-btn:hover:not(:disabled),
.period-page-btn--active {
  border-color: #c6c4fd;
  background: rgba(198, 196, 253, 0.4);
  color: #3730a3;
}

.period-page-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; max-height: 700px; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }

@media (max-width: 1180px) {
  .price-workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .price-input-group { grid-template-columns: 1fr; }
  .period-item { grid-template-columns: 1fr; }
  .period-actions { justify-content: space-between; }
  .btn-scroll-calendar { display: inline-flex; }
  .pm-modal { padding: var(--spacing-lg); }
  .pm-modal-actions { flex-direction: column-reverse; }
  .pm-modal-actions .btn-primary, .pm-modal-actions .btn-outline { width: 100%; }
}
</style>
