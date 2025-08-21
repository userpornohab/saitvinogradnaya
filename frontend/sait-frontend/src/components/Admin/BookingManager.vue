<template>
  <div class="section-card booking-management" v-if="showBookingManagement">
    <div class="edit-header">
      <h3>Управление бронированиями {{ selectedBookingRoom.title }}</h3>
      <button @click="closeBookingManagement">×</button>
    </div>

    <SyncDateRangePicker
      v-model:start-date="startDate"
      v-model:end-date="endDate"
      :price-periods="selectedBookingRoom.price_periods"
      :occupied-dates="occupiedDates"
      :number-of-rooms="selectedBookingRoom?.number_of_rooms"
      @clear="resetdataForm()"
    />

    <div class="booking-controls">
      <div class="flex">
        <div class="form-group">
          <input 
            type="text" 
            v-model="guest_name"
            placeholder="Имя гостя"
          >
        </div>
        
        <div class="form-group">
          <input 
            type="tel" 
            v-model="guest_phone"
            placeholder="Телефон +7(___)___-__-__"
            title="Формат: +7(___)___-__-__"
          >
        </div>
        <div class="form-group">
          <input 
            style="width: 120px;"
            type="number" 
            v-model.number="number_of_guests"
            min="1"
            :max="selectedBookingRoom.max_guests"
            placeholder="Гостей"
          >
        </div>
      </div>
      
      <div class="form-group">
        <textarea v-model="guest_comment" placeholder="Комментарий"></textarea>
      </div>
      <button 
        class="copy-button"
        @click="createBooking"
        :disabled="!isBookingFormValid"
        placeholder="Телефон"
      >
        Создать бронирование
      </button>
    </div>

    <div class="periods-list">
      <div 
        v-for="(yearBookings, year) in groupedBookings" 
        :key="year" 
        class="year-group"
        :class="{ 'current-year': Number(year) === currentYear }"
      >
        <div class="accordion-header" @click="toggleBookingYear(year)">
          <h4>Бронирования за {{ year }} год ({{ yearBookings.length }})</h4>
          <span class="accordion-icon">
            {{ openBookingYears[year] ? '▼' : '▶' }}
          </span>
        </div>
        
        <transition name="slide">
          <div v-if="openBookingYears[year]" class="accordion-content">
            <div 
              v-for="booking in yearBookings" 
              :key="booking.id" 
              class="booking-item"
            >
              <div 
                class="booking-header" 
                :class="{ 'active-booking': activeBookingId === booking.id }"
                @click="toggleBookingAccordion(booking.id)"
              >
                <div class="booking-info">
                  <span class="guest-name">
                    {{ booking.guest_name || 'Без имени' }}
                  </span>
                  <span class="dates">
                    {{ formatDate(booking.check_in_date) }} - {{ formatDate(booking.check_out_date) }}
                  </span>
                  <span class="price">
                    {{ booking.price ? booking.price + ' руб.' : 'Цена не указана' }}
                  </span>
                  <span class="nights">
                    {{ calculateNights(booking.check_in_date, booking.check_out_date) }} ночей
                  </span>
                </div>
                
                <div class="booking-status">
                  <button 
                    type="button" 
                    @click="deleteBooking(booking.id)"              
                    class="cancel-btn"
                  >
                    Удалить
                  </button>
                  <span class="accordion-icon">
                    {{ activeAccordion === booking.id ? '▼' : '▶' }}
                  </span>
                </div>
              </div>
              
              <transition name="slide">
                <div v-if="activeAccordion === booking.id"
                  class="booking-details"
                  :class="{ 'active-booking': activeBookingId === booking.id }">
                  <form @submit.prevent="saveBooking(booking)" class="booking-form">
                    <div class="form-row">
                      <div class="form-group">
                        <label>Имя гостя:</label>
                        <input 
                          type="text" 
                          v-model="editingBookings[booking.id].guest_name"
                          placeholder="Имя гостя"
                        >
                      </div>
                      <div class="form-group">
                        <label>Телефон:</label>
                        <input 
                          type="tel" 
                          v-model="editingBookings[booking.id].guest_phone"
                          placeholder="+7(___)___-__-__"
                          title="Формат: +7(___)___-__-__"
                        >
                      </div>
                    </div>
                    <div class="form-group">
                      <label>Комментарий:</label>
                      <textarea 
                        v-model="editingBookings[booking.id].guest_comment" 
                        placeholder="Комментарий"
                      ></textarea>
                    </div>
                    
                    <div class="form-row">
                      <div class="form-group">
                        <label>Дата заезда:</label>
                        <input 
                          type="date" 
                          v-model="editingBookings[booking.id].check_in_date"
                          required
                          @change="validateDates(booking.id)"
                        >
                      </div>
                      
                      <div class="form-group">
                        <label>Дата выезда:</label>
                        <input 
                          type="date" 
                          v-model="editingBookings[booking.id].check_out_date"
                          required
                          @change="validateDates(booking.id)"
                        >
                      </div>
                    </div>
                    
                    <div class="form-row">
                      <div class="form-group">
                        <label>Количество гостей:</label>
                        <input 
                          type="number" 
                          v-model.number="editingBookings[booking.id].number_of_guests"
                          min="1"
                          :max="selectedBookingRoom.max_guests"
                        >
                      </div>
                      
                      <div class="form-group">
                        <label>Стоимость:</label>
                        <input 
                          type="number" 
                          v-model.number="editingBookings[booking.id].price"
                          min="0"
                          step="1"
                          placeholder="Общая стоимость"
                        >
                      </div>
                    </div>
                    
                    <div class="form-actions">
                      <button type="submit" class="save-btn">Сохранить</button>
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
import axios from 'axios';
import SyncDateRangePicker from './SyncDateRangePicker.vue';

export default {
  components: {
    SyncDateRangePicker
  },
  props: {
    showBookingManagement: Boolean,
    selectedBookingRoom: Object
  },
  data() {
    return {
      activeBookingId: null,
      currentYear: new Date().getFullYear(),
      openBookingYears: {},
      activeAccordion: null,
      editingBookings: {},
      originalBookings: {},
      startDate: null,
      endDate: null,
      guest_name: '',
      guest_phone: '',
      guest_comment: '',
      number_of_guests: 1,
      occupiedDates: {},
      // Локальная копия бронирований
      localBookings: []
    };
  },
  computed: {
    isBookingFormValid() {
      return this.startDate && 
             this.endDate && 
             this.startDate <= this.endDate;
    },
    
    groupedBookings() {
      if (!this.localBookings.length) return {};
      
      const bookings = [...this.localBookings].reverse();
      
      return bookings.reduce((groups, booking) => {
        try {
          if (!booking.check_in_date) return groups;
          const date = new Date(booking.check_in_date);
          if (isNaN(date.getTime())) return groups;
          const year = date.getFullYear().toString();
          if (!groups[year]) groups[year] = [];
          groups[year].push(booking);
        } catch (e) {
          console.error('Error processing booking:', e);
        }
        return groups;
      }, {});
    }
  },
  watch: {
    selectedBookingRoom: {
      immediate: true,
      handler(newVal) {
        if (newVal && newVal.bookings) {
          this.localBookings = [...newVal.bookings];
          this.calculateOccupiedDates();
        }
      }
    }
  },
  methods: {
    calculateNights(checkIn, checkOut) {
      try {
        const start = new Date(checkIn);
        const end = new Date(checkOut);
        
        if (isNaN(start) || isNaN(end)) return 0;
        
        const diffTime = Math.abs(end - start);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      } catch (e) {
        console.error('Error calculating nights:', e);
        return 0;
      }
    },
    
    formatDateForInput(dateString) {
      try {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      } catch (e) {
        return '';
      }
    },
    
    toggleBookingYear(year) {
      this.openBookingYears = {
        ...this.openBookingYears,
        [year]: !this.openBookingYears[year]
      };
    },
    
    closeBookingManagement() {
      this.$emit('close');
    },
    
    toggleBookingAccordion(bookingId) {
      if (this.activeAccordion === bookingId) {
        this.activeAccordion = null;
        this.activeBookingId = null;
        return;
      }
      
      const booking = this.localBookings.find(b => b.id === bookingId);
      if (booking) {
        this.editingBookings = {
          ...this.editingBookings,
          [bookingId]: {
            ...booking,
            check_in_date: this.formatDateForInput(booking.check_in_date),
            check_out_date: this.formatDateForInput(booking.check_out_date),
            guest_name: booking.guest_name || '',
            guest_phone: booking.guest_phone || '',
            guest_comment: booking.guest_comment || ''
          }
        };
        
        this.originalBookings = {
          ...this.originalBookings,
          [bookingId]: { ...booking }
        };
      }
      this.activeBookingId = bookingId;
      this.activeAccordion = bookingId;
    },
    
    validateDates(bookingId) {
      const booking = this.editingBookings[bookingId];
      if (new Date(booking.check_out_date) <= new Date(booking.check_in_date)) {
        this.showError('Дата выезда должна быть после даты заезда');
        return false;
      }
      return true;
    },
    
    validatePhone(phone) {
      if (!phone) {
        return true;
      }
      const phoneRegex = /^(\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/;
      return phoneRegex.test(phone);
    },
    
    async createBooking() {
      try {
        const bookingData = {
          room_id: this.selectedBookingRoom.id,
          check_in_date: this.formatAPIDate(this.startDate),
          check_out_date: this.formatAPIDate(this.endDate),
          number_of_guests: this.number_of_guests,
          guest_name: this.guest_name,
          guest_phone: this.guest_phone,
          guest_comment: this.guest_comment,
        };

        const response = await axios.post(
          'http://localhost:8000/bookings/', 
          bookingData,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        // Обновляем локальные данные вместо пропа
        this.localBookings.push(response.data);
        this.$emit('update-bookings', {
          roomId: this.selectedBookingRoom.id,
          bookings: this.localBookings
        });
        
        this.calculateOccupiedDates();
        this.showSuccess('Бронирование создано');
        this.toggleBookingAccordion(response.data.id);
        this.resetdataForm();
      } catch (error) {
        this.resetdataForm();
        this.handleApiError(error, 'Ошибка создания бронирования');
      }
    },
    
    async saveBooking(booking) {
      if (!this.validateDates(booking.id)) return;
      
      if (!this.validatePhone(this.editingBookings[booking.id].guest_phone)) {
        this.showError('Введите корректный номер телефона в формате +7(___)___-__-__');
        return;
      }

      try {
        const bookingData = {
          room_id: this.selectedBookingRoom.id,
          check_in_date: this.formatAPIDate(new Date(this.editingBookings[booking.id].check_in_date)),
          check_out_date: this.formatAPIDate(new Date(this.editingBookings[booking.id].check_out_date)),
          number_of_guests: this.editingBookings[booking.id].number_of_guests,
          price: this.editingBookings[booking.id].price,
          guest_name: this.editingBookings[booking.id].guest_name,
          guest_phone: this.editingBookings[booking.id].guest_phone,
          guest_comment: this.editingBookings[booking.id].guest_comment
        };
        
        const response = await axios.patch(
          `http://localhost:8000/bookings/${booking.id}`,
          bookingData,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        // Обновляем локальные данные
        const index = this.localBookings.findIndex(b => b.id === booking.id);
        if (index !== -1) {
          this.localBookings.splice(index, 1, response.data);
          this.$emit('update-bookings', {
            roomId: this.selectedBookingRoom.id,
            bookings: this.localBookings
          });
        }

        this.calculateOccupiedDates();
        this.showSuccess('Бронирование обновлено');
        this.activeAccordion = null;
      } catch (error) {
        this.handleApiError(error, 'Ошибка обновления бронирования');
      }
    },
    
    async deleteBooking(bookingId) {
      if (confirm('Вы уверены, что хотите удалить это бронирование?')) {
        try {
          await axios.delete(`http://localhost:8000/bookings/${bookingId}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          
          // Обновляем локальные данные
          this.localBookings = this.localBookings.filter(b => b.id !== bookingId);
          this.$emit('update-bookings', {
            roomId: this.selectedBookingRoom.id,
            bookings: this.localBookings
          });
          
          this.calculateOccupiedDates();
          this.showSuccess('Бронирование удалено');
        } catch (error) {
          this.handleApiError(error, 'Ошибка удаления бронирования');
        }
      }
    },
    
    async loadBookings(roomId) {
      try {
        const response = await axios.get(`http://localhost:8000/bookings/rooms/${roomId}/admin`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        // Сохраняем в локальные данные
        this.localBookings = response.data;
        this.$emit('update-bookings', {
          roomId: this.selectedBookingRoom.id,
          bookings: this.localBookings
        });
        
        this.calculateOccupiedDates();
      } catch (error) {
        this.handleApiError(error, 'Ошибка загрузки бронирований');
      }
    },
    
    calculateOccupiedDates() {
      if (!this.localBookings.length) {
        this.occupiedDates = {};
        return;
      }
      
      const dates = {};
      this.localBookings.forEach(booking => {
        try {
          const current = new Date(booking.check_in_date);
          const end = new Date(booking.check_out_date);
          
          let date = current;
          while (date < end) {
            const dateStr = date.toISOString().split('T')[0];
            dates[dateStr] = (dates[dateStr] || 0) + 1;
            date = new Date(date.setDate(date.getDate() + 1));
          }
        } catch (e) {
          console.error('Error processing booking:', booking.id, e);
        }
      });
      
      this.occupiedDates = dates;
    },
    
    formatAPIDate(date) {
      if (!date || !(date instanceof Date)) return null;
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      return `${year}-${month}-${day}`;
    },
    
    formatDate(dateString) {
      const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    },
    
    resetdataForm() {
      this.startDate = null;
      this.endDate = null;
      this.guest_name = '';
      this.guest_phone = '';
      this.guest_comment = '';
      this.number_of_guests = 1;
    },
    
    handleApiError(error, defaultMessage) {
      const message = error.response?.data?.detail || defaultMessage;
      this.showError(message);
    },
    
    showError(message) {
      this.$emit('notification', { type: 'error', message });
    },
    
    showSuccess(message) {
      this.$emit('notification', { type: 'success', message });
    }
  }
};
</script>

<style scoped>
.booking-management {
  position: relative;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.edit-header h3 {
  padding: 0;
  margin: 0;
}

.booking-controls {
  margin-top: 1.5rem;
}

.flex {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.flex input {
  width: 170px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-group textarea {
  min-height: 80px;
}

.copy-button {
  background-color: #9b59b6;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 1rem;
}

.copy-button:hover:not(:disabled) {
  background-color: #8e44ad;
}

.copy-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.periods-list {
  margin-top: 2rem;
}

.year-group {
  margin-bottom: 1rem;
  border: 1px solid #eee;
  border-radius: 6px;
  overflow: hidden;
}

.year-group.current-year {
  border-left: 3px solid #3498db;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background: #f8f9fa;
  cursor: pointer;
}

.accordion-header h4 {
  margin: 0;
  font-size: 1rem;
}

.accordion-icon {
  font-size: 0.8rem;
}

.accordion-content {
  padding: 0;
}

.booking-item {
  border-bottom: 1px solid #eee;
}

.booking-item:last-child {
  border-bottom: none;
}

.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  cursor: pointer;
}

.booking-header:hover {
  background-color: #f8f9fa;
}

.active-booking {
  background-color: #f8f9fa;
}

.booking-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  flex: 1;
}

.guest-name,
.dates,
.price,
.nights {
  font-size: 0.9rem;
}

.price {
  color: #2e7d32;
  font-weight: 500;
}

.booking-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cancel-btn {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #c0392b;
}

.booking-details {
  padding: 1rem;
  background: #fff;
}

.booking-form {
  display: grid;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-actions {
  margin-top: 1rem;
  text-align: right;
}

.save-btn {
  background: #4CAF50;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover {
  background: #45a049;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0;
}

@media (max-width: 768px) {
  .booking-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .flex {
    flex-direction: column;
    gap: 1rem;
  }
  
  .flex input {
    width: 100%;
  }
}
</style>