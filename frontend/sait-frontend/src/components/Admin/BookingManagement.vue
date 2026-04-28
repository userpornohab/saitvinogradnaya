<template>
  <div class="section-card">
    <div class="edit-header">
      <h3>Бронирования — {{ room.title }}</h3>
      <button @click="$emit('close')" class="btn-close">✕</button>
    </div>

    <SyncDateRangePicker
      v-model:start-date="startDate"
      v-model:end-date="endDate"
      :price-periods="room.price_periods"
      :occupied-dates="occupiedDates"
      :number-of-rooms="room?.number_of_rooms"
      @clear="onClearDates"
    />

    <p class="booking-hint">Выберите диапазон дат в календаре — откроется форма создания бронирования.</p>

    <!-- Модальное окно с формой бронирования -->
    <transition name="modal-fade">
      <div v-if="showBookingModal" class="bm-modal-backdrop" @mousedown.self="closeModal">
        <div class="bm-modal" role="dialog" aria-modal="true">
          <div class="bm-modal-header">
            <div>
              <h4>Новое бронирование</h4>
              <p class="bm-modal-range">{{ formattedRange }} · {{ nights }} ночей</p>
            </div>
            <button @click="closeModal" class="btn-close" aria-label="Закрыть">✕</button>
          </div>

          <div class="booking-form">
            <div class="form-row">
              <div class="form-group">
                <label>Имя гостя</label>
                <input type="text" v-model="guestName" placeholder="Иван Иванов" class="form-input" ref="guestNameInput">
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input type="tel" v-model="guestPhone" placeholder="+7 (___) ___-__-__" class="form-input">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group form-group--narrow">
                <label>Гостей</label>
                <input type="number" v-model.number="guestsCount" min="1" :max="room.max_guests" placeholder="1" class="form-input">
              </div>
            </div>
            <div class="form-group">
              <label>Комментарий</label>
              <textarea v-model="guestComment" placeholder="Пожелания, источник брони..." class="form-input" rows="3"></textarea>
            </div>
          </div>

          <div class="bm-modal-actions">
            <button class="btn-outline" @click="closeModal">Отмена</button>
            <button class="btn-primary" @click="submitBooking" :disabled="!isFormValid">Создать бронирование</button>
          </div>
        </div>
      </div>
    </transition>

    <div class="periods-list">
      <div v-for="(yearBookings, year) in groupedBookings" :key="year" class="year-group" :class="{ 'current-year': Number(year) === currentYear }">
        <div class="accordion-header" @click="toggleYear(year)">
          <h4>{{ year }} год ({{ yearBookings.length }})</h4>
          <span class="accordion-icon">{{ openYears[year] ? '▼' : '▶' }}</span>
        </div>
        <transition name="slide">
          <div v-if="openYears[year]" class="accordion-content">
            <div v-for="booking in yearBookings" :key="booking.id" class="booking-item">
              <div class="booking-header" :class="{ active: activeBookingId === booking.id }" @click="toggleBooking(booking)">
                <div class="booking-info">
                  <span class="guest-name">{{ booking.guest_name || 'Без имени' }}</span>
                  <span class="dates">{{ formatDate(booking.check_in_date) }} — {{ formatDate(booking.check_out_date) }}</span>
                  <span class="price">{{ booking.price ? booking.price + ' ₽' : 'Цена не указана' }}</span>
                  <span class="nights">{{ calculateNights(booking.check_in_date, booking.check_out_date) }} ночей</span>
                </div>
                <div class="booking-status">
                  <button type="button" @click.stop="$emit('delete-booking', booking.id)" class="btn-cancel">Удалить</button>
                  <span class="accordion-icon">{{ activeBookingId === booking.id ? '▼' : '▶' }}</span>
                </div>
              </div>

              <transition name="slide">
                <div v-if="activeBookingId === booking.id" class="booking-details">
                  <form @submit.prevent="$emit('save-booking', booking)" class="edit-form">
                    <div class="form-row">
                      <div class="form-group">
                        <label>Имя</label>
                        <input type="text" v-model="bookingDataForEdit(booking).guest_name" class="form-input">
                      </div>
                      <div class="form-group">
                        <label>Телефон</label>
                        <input type="tel" v-model="bookingDataForEdit(booking).guest_phone" class="form-input">
                      </div>
                    </div>
                    <div class="form-group">
                      <label>Комментарий</label>
                      <textarea v-model="bookingDataForEdit(booking).guest_comment" class="form-input"></textarea>
                    </div>
                    <div class="form-row">
                      <div class="form-group">
                        <label>Заезд</label>
                        <input type="date" v-model="bookingDataForEdit(booking).check_in_date" class="form-input" @change="$emit('validate-dates', booking.id)">
                      </div>
                      <div class="form-group">
                        <label>Выезд</label>
                        <input type="date" v-model="bookingDataForEdit(booking).check_out_date" class="form-input" @change="$emit('validate-dates', booking.id)">
                      </div>
                    </div>
                    <div class="form-row">
                      <div class="form-group">
                        <label>Гостей</label>
                        <input type="number" v-model.number="bookingDataForEdit(booking).number_of_guests" min="1" :max="room.max_guests" class="form-input">
                      </div>
                      <div class="form-group">
                        <label>Стоимость</label>
                        <input type="number" v-model.number="bookingDataForEdit(booking).price" min="0" step="1" class="form-input">
                      </div>
                    </div>
                    <div class="form-actions">
                      <button type="submit" class="btn-save">Сохранить</button>
                    </div>
                  </form>
                </div>
              </transition>
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
  name: 'BookingManagement',
  components: { SyncDateRangePicker },
  props: {
    room: { type: Object, required: true },
    occupiedDates: { type: Object, default: () => ({}) },
    editingBookings: { type: Object, default: () => ({}) }
  },
  data() {
    return {
      startDate: null,
      endDate: null,
      guestName: '',
      guestPhone: '',
      guestsCount: 1,
      guestComment: '',
      openYears: {},
      activeBookingId: null,
      showBookingModal: false
    }
  },
  watch: {
    startDate() { this.maybeOpenModal(); },
    endDate() { this.maybeOpenModal(); }
  },
  computed: {
    currentYear() { return new Date().getFullYear(); },
    isFormValid() { return this.startDate && this.endDate && this.startDate <= this.endDate; },
    formattedRange() {
      if (!this.startDate || !this.endDate) return '';
      return `${this.formatDate(this.startDate)} — ${this.formatDate(this.endDate)}`;
    },
    nights() {
      if (!this.startDate || !this.endDate) return 0;
      return this.calculateNights(this.startDate, this.endDate);
    },
    bookingData() {
      return {
        startDate: this.startDate,
        endDate: this.endDate,
        guestName: this.guestName,
        guestPhone: this.guestPhone,
        guestsCount: this.guestsCount,
        guestComment: this.guestComment
      };
    },
    groupedBookings() {
      if (!this.room?.bookings) return {};
      return [...this.room.bookings].reverse().reduce((groups, booking) => {
        if (!booking.check_in_date) return groups;
        const date = new Date(booking.check_in_date);
        if (isNaN(date.getTime())) return groups;
        const year = date.getFullYear().toString();
        if (!groups[year]) groups[year] = [];
        groups[year].push(booking);
        return groups;
      }, {});
    }
  },
  methods: {
    toggleYear(year) {
      this.openYears = { ...this.openYears, [year]: !this.openYears[year] };
    },
    toggleBooking(booking) {
      this.activeBookingId = this.activeBookingId === booking.id ? null : booking.id;
      if (this.activeBookingId === booking.id) {
        this.$emit('init-edit', booking);
      }
      this.$emit('toggle-booking', booking.id);
    },
    formatDate(dateString) {
      const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    },
    calculateNights(checkIn, checkOut) {
      const start = new Date(checkIn), end = new Date(checkOut);
      if (isNaN(start) || isNaN(end)) return 0;
      return Math.ceil(Math.abs(end - start) / (1000 * 60 * 60 * 24));
    },
    bookingDataForEdit(booking) {
      if (!this.editingBookings[booking.id]) {
        this.$emit('init-edit', booking);
      }
      return this.editingBookings[booking.id] || booking;
    },
    maybeOpenModal() {
      if (this.startDate && this.endDate && this.startDate <= this.endDate) {
        this.showBookingModal = true;
        this.$nextTick(() => this.$refs.guestNameInput?.focus());
      }
    },
    closeModal() {
      this.showBookingModal = false;
      this.resetForm();
      this.$emit('reset-dates');
    },
    onClearDates() {
      this.showBookingModal = false;
      this.resetForm();
      this.$emit('reset-dates');
    },
    resetForm() {
      this.startDate = null;
      this.endDate = null;
      this.guestName = '';
      this.guestPhone = '';
      this.guestsCount = 1;
      this.guestComment = '';
    },
    submitBooking() {
      if (!this.isFormValid) return;
      this.$emit('create-booking', this.bookingData);
      this.showBookingModal = false;
      this.resetForm();
    }
  },
  mounted() {
    this.openYears = { [this.currentYear]: true };
  }
}
</script>

<style scoped>
.edit-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--spacing-lg); padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-gray-200);
}
.edit-header h3 { margin: 0; font-size: var(--text-xl); font-weight: 600; color: var(--color-gray-900); }
.btn-close {
  width: 36px; height: 36px; border-radius: var(--radius-full);
  display: flex; align-items: center; justify-content: center;
  background: var(--color-gray-100); border: none; cursor: pointer; font-size: var(--text-lg);
}
.btn-close:hover { background: var(--color-error-soft); color: var(--color-error); }

.booking-hint {
  margin: var(--spacing-sm) 0 var(--spacing-lg);
  font-size: var(--text-sm); color: var(--color-gray-500); text-align: center;
}

.booking-form {
  display: flex; flex-direction: column; gap: var(--spacing-md);
}

/* === Модальное окно бронирования === */
.bm-modal-backdrop {
  position: fixed; inset: 0; z-index: 1050;
  background: rgba(20, 20, 24, 0.55);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: var(--spacing-lg);
}
.bm-modal {
  width: 100%; max-width: 540px;
  background: var(--color-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  padding: var(--spacing-xl);
  display: flex; flex-direction: column; gap: var(--spacing-lg);
  max-height: calc(100vh - 3rem);
  overflow-y: auto;
}
.bm-modal-header {
  display: flex; justify-content: space-between; align-items: flex-start; gap: var(--spacing-md);
}
.bm-modal-header h4 { margin: 0; font-size: var(--text-xl); font-weight: 700; color: var(--color-gray-900); }
.bm-modal-range { margin: 4px 0 0; font-size: var(--text-sm); color: var(--color-primary); font-weight: 600; }
.bm-modal-actions {
  display: flex; justify-content: flex-end; gap: var(--spacing-md);
}
.bm-modal-actions .btn-primary, .bm-modal-actions .btn-outline { min-width: 140px; }

.btn-outline {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px solid var(--color-gray-300); border-radius: var(--radius-md);
  background: var(--color-white); cursor: pointer; transition: all var(--transition-fast);
}
.btn-outline:hover { border-color: var(--color-primary); color: var(--color-primary); }

.form-group--narrow { max-width: 160px; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity var(--transition-base); }
.modal-fade-enter-active .bm-modal, .modal-fade-leave-active .bm-modal { transition: transform var(--transition-base); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .bm-modal, .modal-fade-leave-to .bm-modal { transform: translateY(8px) scale(0.98); }
.form-row { display: flex; gap: var(--spacing-md); flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-xs); flex: 1; }
.form-group label { font-size: var(--text-sm); font-weight: 600; color: var(--color-gray-700); }
.form-input {
  padding: var(--spacing-sm) var(--spacing-md); border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-md); font-size: var(--text-base);
  transition: all var(--transition-fast);
}
.form-input:focus { outline: none; border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-soft); }

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-primary); color: white;
  border: none; border-radius: var(--radius-md); font-weight: 500; cursor: pointer;
  align-self: flex-start;
}
.btn-primary:hover { background: var(--color-primary-dark); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.periods-list { margin-top: var(--spacing-lg); }
.year-group { margin-bottom: var(--spacing-md); }
.year-group.current-year > .accordion-header { background: var(--color-primary-soft); }

.accordion-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-gray-50); border-radius: var(--radius-md); cursor: pointer;
}
.accordion-header:hover { background: var(--color-gray-100); }
.accordion-header h4 { margin: 0; font-size: var(--text-sm); font-weight: 600; }

.booking-item { margin-bottom: var(--spacing-sm); }

.booking-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--spacing-md); background: var(--color-white);
  border: 1px solid var(--color-gray-200); border-radius: var(--radius-md);
  cursor: pointer; transition: all var(--transition-fast);
}
.booking-header:hover { border-color: var(--color-primary); }
.booking-header.active { background: var(--color-primary-soft); border-color: var(--color-primary); }

.booking-info { display: flex; flex-wrap: wrap; gap: var(--spacing-md); align-items: center; }
.guest-name { font-weight: 600; color: var(--color-gray-900); }
.dates { font-size: var(--text-sm); color: var(--color-gray-600); }
.price { font-weight: 600; color: var(--color-success); }
.nights { font-size: var(--text-sm); color: var(--color-gray-500); }

.booking-status { display: flex; gap: var(--spacing-sm); align-items: center; }
.btn-cancel {
  padding: var(--spacing-xs) var(--spacing-md); background: var(--color-error-soft);
  color: var(--color-error); border: none; border-radius: var(--radius-sm);
  font-size: var(--text-sm); cursor: pointer;
}
.btn-cancel:hover { background: var(--color-error); color: white; }

.booking-details {
  padding: var(--spacing-md); background: var(--color-white);
  border: 1px solid var(--color-gray-200); border-top: none;
  border-radius: 0 0 var(--radius-md) var(--radius-md);
}
.edit-form { display: flex; flex-direction: column; gap: var(--spacing-md); }
.form-actions { display: flex; gap: var(--spacing-md); }
.btn-save {
  padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-success);
  color: white; border: none; border-radius: var(--radius-md); font-weight: 500; cursor: pointer;
}
.btn-save:hover { background: #006b04; }

.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; max-height: 800px; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }

@media (max-width: 768px) {
  .form-row { flex-direction: column; }
  .booking-info { flex-direction: column; align-items: flex-start; }
  .booking-header { flex-direction: column; gap: var(--spacing-md); align-items: flex-start; }
  .booking-status { align-self: flex-end; }
  .bm-modal { padding: var(--spacing-lg); }
  .bm-modal-actions { flex-direction: column-reverse; }
  .bm-modal-actions .btn-primary, .bm-modal-actions .btn-outline { width: 100%; }
  .form-group--narrow { max-width: 100%; }
}
</style>
