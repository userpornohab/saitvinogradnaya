<template>
  <div class="section-card">
    <div class="edit-header">
      <h3>Бронирования — {{ room.title }}</h3>
      <button @click="$emit('close')" class="btn-close">✕</button>
    </div>

    <div class="booking-workspace">
      <section class="booking-calendar-panel" ref="calendarPanel">
        <SyncDateRangePicker
          v-model:start-date="startDate"
          v-model:end-date="endDate"
          :price-periods="room.price_periods"
          :occupied-dates="occupiedDates"
          :number-of-rooms="room?.number_of_rooms"
          :highlighted-booking="hoveredBooking"
          :highlight-start-date="hoveredBooking?.check_in_date || null"
          :highlight-end-date="hoveredBooking?.check_out_date || null"
          :focus-date="calendarFocusDate"
          :months-count="calendarMonthsCount"
          @clear="onClearDates"
        />

      </section>

      <aside class="booking-side-panel">
        <div class="booking-list-toolbar">
          <div class="booking-search">
            <input
              id="booking-name-filter"
              v-model.trim="bookingNameFilter"
              type="search"
              class="form-input"
              placeholder="Поиск: по имени"
            >
          </div>
          <label class="booking-filter-toggle">
            <input type="checkbox" v-model="showOnlyNewBookings">
            <span>Актуальные</span>
          </label>
        </div>

        <div class="periods-list">
          <p v-if="!hasGroupedBookings" class="bookings-empty">
            По выбранным фильтрам заявок нет
          </p>
          <div v-for="(yearBookings, year) in groupedBookings" :key="year" class="year-group" :class="{ 'current-year': Number(year) === currentYear }">
            <div class="accordion-header" @click="toggleYear(year)">
              <h4>{{ year }} год ({{ yearBookings.length }})</h4>
              <span class="accordion-icon">{{ openYears[year] ? '▼' : '▶' }}</span>
            </div>
            <transition name="slide">
              <div v-if="openYears[year]" class="accordion-content">
                <div
                  v-for="booking in paginatedBookings(yearBookings, year)"
                  :key="booking.id"
                  class="booking-item"
                  @mouseenter="hoverBooking(booking)"
                  @mouseleave="clearHoveredBooking"
                  @focusin="hoverBooking(booking)"
                  @focusout="clearHoveredBooking"
                >
                  <div
                    class="booking-header"
                    @click="openEditModal(booking)"
                  >
                    <div class="booking-info">
                      <div class="booking-main-line">
                        <span class="guest-name">{{ booking.guest_name || 'Без имени' }}</span>
                        <span class="booking-badge" :class="bookingStatusClass(booking)">
                          {{ bookingStatusLabel(booking) }}
                        </span>
                      </div>
                      <span class="dates">{{ formatDate(booking.check_in_date) }} — {{ formatDate(booking.check_out_date) }}</span>
                      <div class="booking-meta">
                        <span class="booking-chip price">{{ booking.price ? booking.price + ' ₽' : 'Цена не указана' }}</span>
                        <span class="booking-chip nights">{{ calculateNights(booking.check_in_date, booking.check_out_date) }} ночей</span>
                        <span v-if="booking.number_of_guests" class="booking-chip">{{ booking.number_of_guests }} гостей</span>
                      </div>
                    </div>
                    <div class="booking-status">
                      <button type="button" class="btn-scroll-calendar" @click.stop="showBookingOnCalendar(booking)">К календарю</button>
                      <button type="button" @click.stop="$emit('delete-booking', booking.id)" class="btn-cancel">Удалить</button>
                    </div>
                  </div>
                </div>
                <div v-if="totalBookingPages(yearBookings) > 1" class="booking-pagination">
                  <button
                    type="button"
                    class="booking-page-btn"
                    :disabled="bookingPage(year) === 1"
                    @click="setBookingPage(year, bookingPage(year) - 1)"
                  >
                    ‹
                  </button>
                  <button
                    v-for="page in totalBookingPages(yearBookings)"
                    :key="`${year}-${page}`"
                    type="button"
                    class="booking-page-btn"
                    :class="{ 'booking-page-btn--active': bookingPage(year) === page }"
                    @click="setBookingPage(year, page)"
                  >
                    {{ page }}
                  </button>
                  <button
                    type="button"
                    class="booking-page-btn"
                    :disabled="bookingPage(year) === totalBookingPages(yearBookings)"
                    @click="setBookingPage(year, bookingPage(year) + 1)"
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

    <transition name="modal-fade">
      <div v-if="showEditBookingModal && editingModalBooking && editingModalData" class="bm-modal-backdrop" @mousedown.self="closeEditModal">
        <div class="bm-modal bm-modal--wide" role="dialog" aria-modal="true">
          <div class="bm-modal-header">
            <div>
              <h4>Редактирование заявки</h4>
              <p class="bm-modal-range">
                {{ formatDate(editingModalData.check_in_date) }} — {{ formatDate(editingModalData.check_out_date) }}
              </p>
            </div>
            <button @click="closeEditModal" class="btn-close" aria-label="Закрыть">✕</button>
          </div>

          <form @submit.prevent="saveEditedBooking" class="edit-form">
            <div class="form-row">
              <div class="form-group">
                <label>Имя</label>
                <input type="text" v-model="editingModalData.guest_name" class="form-input">
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input type="tel" v-model="editingModalData.guest_phone" class="form-input">
              </div>
            </div>
            <div class="form-group">
              <label>Комментарий</label>
              <textarea v-model="editingModalData.guest_comment" class="form-input" rows="3"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Заезд</label>
                <input type="date" v-model="editingModalData.check_in_date" class="form-input" @change="$emit('validate-dates', editingModalBooking.id)">
              </div>
              <div class="form-group">
                <label>Выезд</label>
                <input type="date" v-model="editingModalData.check_out_date" class="form-input" @change="$emit('validate-dates', editingModalBooking.id)">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Гостей</label>
                <input type="number" v-model.number="editingModalData.number_of_guests" min="1" :max="room.max_guests" class="form-input">
              </div>
              <div class="form-group">
                <label>Стоимость</label>
                <input type="number" v-model.number="editingModalData.price" min="0" step="1" class="form-input">
              </div>
            </div>

            <div class="bm-modal-actions">
              <button type="button" class="btn-outline" @click="closeEditModal">Отмена</button>
              <button type="submit" class="btn-save">Сохранить</button>
            </div>
          </form>
        </div>
      </div>
    </transition>
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
      showBookingModal: false,
      showEditBookingModal: false,
      editingBookingId: null,
      bookingNameFilter: '',
      showOnlyNewBookings: false,
      hoveredBookingId: null,
      calendarFocusDate: null,
      isMobileViewport: false,
      bookingsPerPage: 5,
      bookingPages: {}
    }
  },
  watch: {
    startDate() { this.maybeOpenModal(); },
    endDate() { this.maybeOpenModal(); },
    bookingNameFilter() { this.resetBookingPages(); },
    showOnlyNewBookings() { this.resetBookingPages(); },
    room: {
      handler() { this.resetBookingPages(); },
      deep: true
    }
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
        guests: this.guestsCount,
        guestComment: this.guestComment
      };
    },
    groupedBookings() {
      if (!this.filteredBookings.length) return {};
      return [...this.filteredBookings].reverse().reduce((groups, booking) => {
        if (!booking.check_in_date) return groups;
        const date = new Date(booking.check_in_date);
        if (isNaN(date.getTime())) return groups;
        const year = date.getFullYear().toString();
        if (!groups[year]) groups[year] = [];
        groups[year].push(booking);
        return groups;
      }, {});
    },
    filteredBookings() {
      if (!this.room?.bookings) return [];
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const nameFilter = this.bookingNameFilter.toLowerCase();

      return this.room.bookings.filter(booking => {
        const guestName = (booking.guest_name || '').toLowerCase();
        const matchesName = !nameFilter || guestName.includes(nameFilter);
        const checkOut = new Date(booking.check_out_date);
        checkOut.setHours(0, 0, 0, 0);
        const matchesFresh = !this.showOnlyNewBookings || checkOut >= today;
        return matchesName && matchesFresh;
      });
    },
    hasGroupedBookings() {
      return Object.keys(this.groupedBookings).length > 0;
    },
    hoveredBooking() {
      if (!this.hoveredBookingId || !this.room?.bookings) return null;
      return this.room.bookings.find(booking => booking.id === this.hoveredBookingId) || null;
    },
    editingModalBooking() {
      if (!this.editingBookingId || !this.room?.bookings) return null;
      return this.room.bookings.find(booking => booking.id === this.editingBookingId) || null;
    },
    editingModalData() {
      if (!this.editingModalBooking) return null;
      return this.bookingDataForEdit(this.editingModalBooking);
    },
    calendarMonthsCount() {
      return this.isMobileViewport ? 2 : 4;
    }
  },
  methods: {
    toggleYear(year) {
      this.openYears = { ...this.openYears, [year]: !this.openYears[year] };
    },
    bookingPage(year) {
      return this.bookingPages[year] || 1;
    },
    totalBookingPages(bookings) {
      return Math.max(1, Math.ceil(bookings.length / this.bookingsPerPage));
    },
    paginatedBookings(bookings, year) {
      const totalPages = this.totalBookingPages(bookings);
      const currentPage = Math.min(this.bookingPage(year), totalPages);
      const start = (currentPage - 1) * this.bookingsPerPage;
      return bookings.slice(start, start + this.bookingsPerPage);
    },
    setBookingPage(year, page) {
      const bookings = this.groupedBookings[year] || [];
      const totalPages = this.totalBookingPages(bookings);
      const nextPage = Math.min(Math.max(page, 1), totalPages);
      this.bookingPages = { ...this.bookingPages, [year]: nextPage };
    },
    resetBookingPages() {
      this.bookingPages = {};
    },
    openEditModal(booking) {
      this.editingBookingId = booking.id;
      this.hoverBooking(booking);
      this.$emit('init-edit', booking);
      this.showEditBookingModal = true;
    },
    closeEditModal() {
      this.showEditBookingModal = false;
      this.editingBookingId = null;
    },
    saveEditedBooking() {
      if (!this.editingModalBooking) return;
      this.$emit('save-booking', this.editingModalBooking);
      this.closeEditModal();
    },
    showBookingOnCalendar(booking) {
      this.hoverBooking(booking);
      this.calendarFocusDate = booking.check_in_date;
      this.$nextTick(() => {
        this.$refs.calendarPanel?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    },
    updateViewportState() {
      this.isMobileViewport = window.matchMedia('(max-width: 768px)').matches;
    },
    hoverBooking(booking) {
      this.hoveredBookingId = booking.id;
    },
    clearHoveredBooking() {
      this.hoveredBookingId = null;
    },
    isUpcomingBooking(booking) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const checkOut = new Date(booking.check_out_date);
      checkOut.setHours(0, 0, 0, 0);
      return checkOut >= today;
    },
    bookingStatusLabel(booking) {
      if (this.isUpcomingBooking(booking)) return 'Актуальная';
      return 'Завершена';
    },
    bookingStatusClass(booking) {
      return this.isUpcomingBooking(booking) ? 'booking-badge--active' : 'booking-badge--past';
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

.booking-workspace {
  display: grid;
  grid-template-columns: minmax(640px, max-content) minmax(360px, 1fr);
  gap: var(--spacing-xl);
  align-items: start;
}

.booking-calendar-panel,
.booking-side-panel {
  min-width: 0;
}

.booking-calendar-panel {
}

.booking-side-panel {
  width: 100%;
  top: var(--spacing-md);
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
.bm-modal--wide {
  max-width: 720px;
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

.booking-list-toolbar {
  width: 100%;
  display: flex;
  margin: 0 0 var(--spacing-md);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, rgba(198, 196, 253, 0.18), rgba(255, 255, 255, 0.95));
  border: 1px solid rgba(198, 196, 253, 0.45);
  border-radius: var(--radius-lg);
}

.booking-search {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.booking-search label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-gray-700);
}

.booking-filter-toggle {
  margin-left: 5px;
  height: 42px;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 0 var(--spacing-md);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  background: var(--color-white);
  color: var(--color-gray-700);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
}

.booking-filter-toggle input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

.periods-list { margin-top: var(--spacing-md); }
.bookings-empty {
  margin: 0;
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--color-gray-500);
  background: var(--color-white);
  border: 1px dashed var(--color-gray-300);
  border-radius: var(--radius-lg);
}
.year-group { margin-bottom: var(--spacing-md); }
.year-group.current-year > .accordion-header { background: var(--color-gray-50); }

.accordion-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-gray-50); border-radius: var(--radius-md); cursor: pointer;
}
.accordion-header:hover { background: var(--color-gray-100); }
.accordion-header h4 { margin: 0; font-size: var(--text-sm); font-weight: 600; }

.booking-item { margin-bottom: var(--spacing-sm); }

.booking-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) 0 0;
}

.booking-page-btn {
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

.booking-page-btn:hover:not(:disabled),
.booking-page-btn--active {
  border-color: #c6c4fd;
  background: rgba(198, 196, 253, 0.4);
  color: #3730a3;
}

.booking-page-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.booking-header {
  width: 100%;
  display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: var(--spacing-md); align-items: center;
  padding: var(--spacing-md); background: var(--color-white);
  border: 1px solid var(--color-gray-200); border-radius: var(--radius-lg);
  cursor: pointer; transition: all var(--transition-fast);
}
.booking-header:hover { border-color: #9b9aff; background-color: #dbdaff; box-shadow: 0 12px 30px rgba(76, 76, 247, 0.1); transform: translateY(-1px); }

.booking-info { display: flex; flex-direction: column; gap: var(--spacing-xs); min-width: 0; }
.booking-main-line { display: flex; flex-wrap: wrap; gap: var(--spacing-sm); align-items: center; }
.guest-name { font-weight: 700; color: var(--color-gray-900); font-size: var(--text-base); }
.dates { font-size: var(--text-sm); color: var(--color-gray-600); }
.booking-meta { display: flex; flex-wrap: wrap; gap: var(--spacing-xs); }
.booking-chip,
.booking-badge {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
}
.booking-chip {
  background: var(--color-gray-50);
  color: var(--color-gray-700);
  border: 1px solid var(--color-gray-200);
}
.price { color: var(--color-success); }
.nights { color: var(--color-gray-600); }
.booking-badge--active {
  background: rgba(198, 196, 253, 0.45);
  color: #3730a3;
}
.booking-badge--past {
  background: var(--color-gray-100);
  color: var(--color-gray-500);
}

.booking-status { display: flex; gap: var(--spacing-sm); align-items: center; }
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
  .booking-workspace { grid-template-columns: 1fr; gap: var(--spacing-lg); }
  .booking-calendar-panel { padding: var(--spacing-sm); }
  .booking-side-panel { position: static; }
  .form-row { flex-direction: column; }
  .booking-list-toolbar { grid-template-columns: 1fr; }
  .booking-header { grid-template-columns: 1fr; }
  .booking-status { justify-content: space-between; width: 100%; }
  .btn-scroll-calendar { display: inline-flex; }
  .bm-modal { padding: var(--spacing-lg); }
  .bm-modal-actions { flex-direction: column-reverse; }
  .bm-modal-actions .btn-primary, .bm-modal-actions .btn-outline { width: 100%; }
  .form-group--narrow { max-width: 100%; }
}

@media (max-width: 1180px) {
  .booking-workspace {
    grid-template-columns: 1fr;
  }

  .booking-side-panel {
    position: static;
  }
}
</style>
