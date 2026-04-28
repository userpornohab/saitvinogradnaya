<template>
  <div class="admin-panel">
    <AdminHeader />

    <!-- Список номеров -->
    <div class="section-card">
      <div class="rooms-header">
        <h3>Список номеров</h3>
        <button class="btn-primary" @click="startNewRoom">+ Добавить номер</button>
      </div>
      <div class="room-list">
        <RoomListCard
          v-for="room in rooms"
          :key="room.id"
          :room="room"
          :is-selected="selectedRoomId === room.id"
          @edit="selectRoom"
          @delete="deleteRoom"
          @manage-prices="togglePriceManagement"
          @manage-bookings="toggleBookingManagement"
        />
      </div>
    </div>

    <!-- Редактор номера -->
    <RoomEditor
      v-if="selectedRoom || isNewRoom"
      :room="selectedRoom"
      :is-new="isNewRoom"
      :amenities="allAmenities"
      :bed-options="allBedOptions"
      :selected-amenities="newRoom.amenities"
      :selected-beds="newRoom.bed_options"
      :show-amenity-form="showAmenityForm"
      :show-bed-form="showBedForm"
      :file-count="selectedFiles.length"
      @submit="handleRoomSubmit"
      @cancel="cancelEdit"
      @toggle-amenity-form="showAmenityForm = !showAmenityForm"
      @toggle-bed-form="showBedForm = !showBedForm"
      @toggle-amenity="toggleAmenity"
      @toggle-bed="toggleBed"
      @add-amenity="addAmenity"
      @add-bed="addBed"
      @update-form="updateRoomForm"
      @delete-amenity="deleteAmenity"
      @delete-bed="deleteBed"
      @set-main-photo="setMainPhoto"
      @delete-photo="deletePhoto"
      @photo-upload="handlePhotoUpload"
      @upload-photos="uploadPhoto"
    />

    <!-- Управление ценами -->
    <PriceManagement
      v-if="showPriceManagement && selectedPriceRoom"
      :room="selectedPriceRoom"
      :is-copying="isCopying"
      @close="closePriceManagement"
      @reset="resetDataForm"
      @create-price="createPricePeriod"
      @copy-next-year="copyPricePeriodsToNextYear"
      @delete-price="deletePricePeriod"
    />

    <!-- Управление бронированиями -->
    <BookingManagement
      v-if="showBookingManagement && selectedBookingRoom"
      :room="selectedBookingRoom"
      :occupied-dates="occupiedDates"
      :editing-bookings="editingBookings"
      @close="closeBookingManagement"
      @reset-dates="resetDataForm"
      @create-booking="createBooking"
      @delete-booking="deleteBooking"
      @toggle-booking="toggleBookingAccordion"
      @save-booking="saveBooking"
      @validate-dates="validateDates"
      @init-edit="initBookingEdit"
    />

    <!-- Уведомления -->
    <transition name="fade">
      <div v-if="notification" :class="['notification', notification.type]">
        {{ notification.message }}
      </div>
    </transition>
  </div>
</template>

<script>
import api from '@/api';
import AdminHeader from './AdminHeader.vue';
import RoomListCard from './Admin/RoomListCard.vue';
import RoomEditor from './Admin/RoomEditor.vue';
import PriceManagement from './Admin/PriceManagement.vue';
import BookingManagement from './Admin/BookingManagement.vue';

export default {
  name: 'AdminRooms',
  components: { AdminHeader, RoomListCard, RoomEditor, PriceManagement, BookingManagement },
  data() {
    return {
      rooms: [],
      allAmenities: [],
      allBedOptions: [],
      selectedRoom: null,
      selectedRoomId: null,
      isNewRoom: false,
      showAmenityForm: false,
      showBedForm: false,
      selectedFiles: [],
      newRoom: {
        title: '', title_dop: '', description: '',
        floor: 1, max_guests: 2, number_of_rooms: 1,
        amenities: [], bed_options: []
      },
      showPriceManagement: false,
      selectedPriceRoom: null,
      showBookingManagement: false,
      selectedBookingRoom: null,
      occupiedDates: {},
      editingBookings: {},
      notification: null,
      isCopying: false
    };
  },
  async mounted() {
    window.addEventListener('keydown', this.handleKeyPress);
    await this.checkAdminStatus();
    await this.fetchData();
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyPress);
  },
  methods: {
    // === Навигация ===
    startNewRoom() {
      this.selectedRoom = null;
      this.isNewRoom = true;
      this.showPriceManagement = false;
      this.showBookingManagement = false;
      this.newRoom = { title: '', title_dop: '', description: '', floor: 1, max_guests: 2, number_of_rooms: 1, amenities: [], bed_options: [] };
    },
    selectRoom(room) {
      this.selectedRoom = room;
      this.isNewRoom = false;
      this.showPriceManagement = false;
      this.showBookingManagement = false;
      this.selectedRoomId = null;
      this.newRoom = {
        title: room.title, title_dop: room.title_dop, description: room.description,
        floor: room.floor, max_guests: room.max_guests, number_of_rooms: room.number_of_rooms,
        amenities: room.amenities.map(a => a.id), bed_options: room.bed_options.map(b => b.id)
      };
    },
    cancelEdit() {
      this.selectedRoom = null;
      this.isNewRoom = false;
      this.selectedFiles = [];
      this.showAmenityForm = false;
      this.showBedForm = false;
    },
    updateRoomForm(formData) {
      Object.assign(this.newRoom, formData);
    },

    // === Цены ===
    togglePriceManagement(room) {
      this.selectedRoomId = room.id;
      this.selectedPriceRoom = room;
      this.showPriceManagement = true;
      this.showBookingManagement = false;
      this.selectedRoom = null;
      this.resetDataForm();
    },
    closePriceManagement() {
      this.selectedRoomId = null;
      this.showPriceManagement = false;
      this.selectedPriceRoom = null;
    },
    async createPricePeriod({ startDate, endDate, price, guests }) {
      try {
        const periodData = {
          start_date: this.formatAPIDate(startDate),
          end_date: this.formatAPIDate(endDate),
          price, number_of_guests: guests
        };
        const url = `/price-periods/rooms/${this.selectedPriceRoom.id}/price-periods`;
        const response = await api.post(url, periodData, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.selectedPriceRoom.price_periods.push(response.data);
        this.resetDataForm();
        this.showSuccess('Ценовой период создан');
      } catch (error) {
        this.handleApiError(error, 'Ошибка создания периода');
      }
    },
    async deletePricePeriod(periodId) {
      try {
        await api.delete(`/price-periods/${periodId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.selectedPriceRoom.price_periods = this.selectedPriceRoom.price_periods.filter(p => p.id !== periodId);
        this.showSuccess('Период удален');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления периода');
      }
    },
    async copyPricePeriodsToNextYear() {
      if (!this.selectedPriceRoom?.id) return;
      try {
        this.isCopying = true;
        const response = await api.post(
          `/price-periods/rooms/${this.selectedPriceRoom.id}/copy-price-periods-to-next-year`,
          {}, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        await this.refreshPricePeriods();
        this.showSuccess(response.data.message);
      } catch (error) {
        this.handleApiError(error, 'Ошибка копирования периодов');
      } finally {
        this.isCopying = false;
      }
    },
    async refreshPricePeriods() {
      try {
        const response = await api.get(`/rooms/${this.selectedPriceRoom.id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.selectedPriceRoom.price_periods = response.data.price_periods;
      } catch (error) {
        this.handleApiError(error, 'Ошибка обновления периодов');
      }
    },

    // === Бронирования ===
    toggleBookingManagement(room) {
      this.selectedRoom = null;
      this.selectedRoomId = room.id;
      this.selectedBookingRoom = { ...room, bookings: room.bookings || [] };
      this.showBookingManagement = true;
      this.showPriceManagement = false;
      this.loadBookings(room.id);
    },
    closeBookingManagement() {
      this.selectedRoomId = null;
      this.showBookingManagement = false;
      this.selectedBookingRoom = null;
    },
    async loadBookings(roomId) {
      try {
        const response = await api.get(`/bookings/rooms/${roomId}/admin`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.selectedBookingRoom = { ...this.selectedBookingRoom, bookings: response.data };
        this.calculateOccupiedDates();
      } catch (error) {
        this.handleApiError(error, 'Ошибка загрузки бронирований');
      }
    },
    toggleBookingAccordion(/* bookingId */) {
      this.editingBookings = { ...this.editingBookings };
    },
    initBookingEdit(booking) {
      if (!this.editingBookings[booking.id]) {
        this.editingBookings = {
          ...this.editingBookings,
          [booking.id]: {
            ...booking,
            check_in_date: this.formatDateForInput(booking.check_in_date),
            check_out_date: this.formatDateForInput(booking.check_out_date),
            guest_name: booking.guest_name || '',
            guest_phone: booking.guest_phone || '',
            guest_comment: booking.guest_comment || ''
          }
        };
      }
    },
    async createBooking(bookingData) {
      try {
        const data = {
          room_id: this.selectedBookingRoom.id,
          check_in_date: this.formatAPIDate(bookingData.startDate),
          check_out_date: this.formatAPIDate(bookingData.endDate),
          number_of_guests: bookingData.guests || this.guestsCount || 1,
          guest_name: bookingData.guestName || '',
          guest_phone: bookingData.guestPhone || '',
          guest_comment: bookingData.guestComment || ''
        };
        const response = await api.post('/bookings/', data, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.selectedBookingRoom.bookings.push(response.data);
        this.calculateOccupiedDates();
        this.showSuccess('Бронирование создано');
        this.resetDataForm();
      } catch (error) {
        this.handleApiError(error, 'Ошибка создания бронирования');
      }
    },
    validateDates(bookingId) {
      const booking = this.editingBookings[bookingId];
      if (booking && new Date(booking.check_out_date) <= new Date(booking.check_in_date)) {
        this.showError('Дата выезда должна быть после даты заезда');
        return false;
      }
      return true;
    },
    async saveBooking(booking) {
      if (!this.validateDates(booking.id)) return;
      try {
        const editData = this.editingBookings[booking.id];
        const bookingData = {
          room_id: this.selectedBookingRoom.id,
          check_in_date: this.formatAPIDate(new Date(editData.check_in_date)),
          check_out_date: this.formatAPIDate(new Date(editData.check_out_date)),
          number_of_guests: editData.number_of_guests,
          price: editData.price,
          guest_name: editData.guest_name,
          guest_phone: editData.guest_phone,
          guest_comment: editData.guest_comment
        };
        const response = await api.patch(`/bookings/${booking.id}`, bookingData, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        const index = this.selectedBookingRoom.bookings.findIndex(b => b.id === booking.id);
        if (index !== -1) this.selectedBookingRoom.bookings.splice(index, 1, response.data);
        this.calculateOccupiedDates();
        this.showSuccess('Бронирование обновлено');
      } catch (error) {
        this.handleApiError(error, 'Ошибка обновления бронирования');
      }
    },
    async deleteBooking(bookingId) {
      if (!confirm('Удалить это бронирование?')) return;
      try {
        await api.delete(`/bookings/${bookingId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.selectedBookingRoom.bookings = this.selectedBookingRoom.bookings.filter(b => b.id !== bookingId);
        this.calculateOccupiedDates();
        this.showSuccess('Бронирование удалено');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления бронирования');
      }
    },
    calculateOccupiedDates() {
      if (!this.selectedBookingRoom?.bookings) { this.occupiedDates = {}; return; }
      const dates = {};
      this.selectedBookingRoom.bookings.forEach(booking => {
        try {
          const current = new Date(booking.check_in_date);
          const end = new Date(booking.check_out_date);
          while (current < end) {
            const dateStr = current.toISOString().split('T')[0];
            dates[dateStr] = (dates[dateStr] || 0) + 1;
            current.setDate(current.getDate() + 1);
          }
        } catch (e) { /* skip */ }
      });
      this.occupiedDates = dates;
    },

    // === Удобства и кровати ===
    toggleAmenity(id) {
      const idx = this.newRoom.amenities.indexOf(id);
      if (idx === -1) this.newRoom.amenities.push(id);
      else this.newRoom.amenities.splice(idx, 1);
    },
    toggleBed(id) {
      const idx = this.newRoom.bed_options.indexOf(id);
      if (idx === -1) this.newRoom.bed_options.push(id);
      else this.newRoom.bed_options.splice(idx, 1);
    },
    async addAmenity({ name, iconFile }) {
      if (!name || !iconFile) return;
      const formData = new FormData();
      formData.append('name', name);
      formData.append('icon', iconFile);
      try {
        const response = await api.post('/amenities/', formData, {
          headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.allAmenities.push(response.data);
        this.showAmenityForm = false;
        this.showSuccess('Удобство добавлено');
      } catch (error) { this.handleApiError(error, 'Ошибка добавления удобства'); }
    },
    async deleteAmenity(id) {
      try {
        await api.delete(`/amenities/${id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.allAmenities = this.allAmenities.filter(a => a.id !== id);
        this.showSuccess('Удобство удалено');
      } catch (error) { this.handleApiError(error, 'Ошибка удаления удобства'); }
    },
    async addBed({ name, iconFile }) {
      if (!name || !iconFile) return;
      const formData = new FormData();
      formData.append('name', name);
      formData.append('icon', iconFile);
      try {
        const response = await api.post('/bed-options/', formData, {
          headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.allBedOptions.push(response.data);
        this.showBedForm = false;
        this.showSuccess('Тип кровати добавлен');
      } catch (error) { this.handleApiError(error, 'Ошибка добавления типа кровати'); }
    },
    async deleteBed(id) {
      try {
        await api.delete(`/bed-options/${id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.allBedOptions = this.allBedOptions.filter(b => b.id !== id);
        this.showSuccess('Тип кровати удален');
      } catch (error) { this.handleApiError(error, 'Ошибка удаления типа кровати'); }
    },

    // === Фото ===
    handlePhotoUpload(event) {
      this.selectedFiles = Array.from(event.target.files);
    },
    async uploadPhoto() {
      if (!this.selectedFiles.length || !this.selectedRoom) return;
      try {
        const formData = new FormData();
        this.selectedFiles.forEach(f => formData.append('files', f));
        const response = await api.post(`/rooms/${this.selectedRoom.id}/upload-photos`, formData, {
          headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        const newPhotos = Array.isArray(response.data) ? response.data : (response.data.photos || []);
        this.selectedRoom.photos = [...(this.selectedRoom.photos || []), ...newPhotos];
        // синхронизируем список в общем массиве комнат
        const idx = this.rooms.findIndex(r => r.id === this.selectedRoom.id);
        if (idx !== -1) this.rooms.splice(idx, 1, { ...this.rooms[idx], photos: this.selectedRoom.photos });
        this.selectedFiles = [];
        this.showSuccess('Фото загружено');
      } catch (error) { this.handleApiError(error, 'Ошибка загрузки фото'); }
    },
    async setMainPhoto(photo) {
      try {
        await api.patch(
          `/rooms/${this.selectedRoom.id}/photos/${photo.id}`,
          { is_main: true },
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        this.selectedRoom.photos = this.selectedRoom.photos.map(p => ({ ...p, is_main: p.id === photo.id }));
        const idx = this.rooms.findIndex(r => r.id === this.selectedRoom.id);
        if (idx !== -1) this.rooms.splice(idx, 1, { ...this.rooms[idx], photos: this.selectedRoom.photos });
        this.showSuccess('Главное фото установлено');
      } catch (error) { this.handleApiError(error, 'Ошибка установки главного фото'); }
    },
    async deletePhoto(photo) {
      if (!confirm('Удалить фото?')) return;
      try {
        await api.delete(`/rooms/${this.selectedRoom.id}/photos/${photo.id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.selectedRoom.photos = this.selectedRoom.photos.filter(p => p.id !== photo.id);
        this.showSuccess('Фото удалено');
      } catch (error) { this.handleApiError(error, 'Ошибка удаления фото'); }
    },

    // === CRUD номеров ===
    async handleRoomSubmit(formData) {
      try {
        const roomData = { ...this.newRoom, ...formData };
        let response;
        if (this.editingRoom || this.selectedRoom) {
          const id = this.selectedRoom?.id || this.editingRoom?.id;
          response = await api.put(`/rooms/${id}`, roomData, {
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
          });
          const updated = response.data;
          this.rooms = this.rooms.map(r => r.id === updated.id ? updated : r);
          this.selectedRoom = updated;
        } else {
          response = await api.post('/rooms/', roomData, {
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
          });
          this.rooms.push(response.data);
          this.cancelEdit();
        }
        this.showSuccess('Изменения сохранены');
      } catch (error) { this.handleApiError(error, 'Ошибка сохранения'); }
    },
    async deleteRoom(roomId) {
      if (!confirm('Удалить этот номер?')) return;
      try {
        await api.delete(`/rooms/${roomId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.rooms = this.rooms.filter(r => r.id !== roomId);
        this.showSuccess('Номер удален');
      } catch (error) { this.handleApiError(error, 'Ошибка удаления номера'); }
    },

    // === Утилиты ===
    resetDataForm() { /* reset if needed */ },
    handleKeyPress(e) { if (e.key === 'Escape') { this.closePriceManagement(); this.closeBookingManagement(); } },
    async checkAdminStatus() {
      try {
        const token = localStorage.getItem('access_token');
        const res = await api.get('/users/me/', { headers: { Authorization: `Bearer ${token}` } });
        if (!res.data.is_superuser) this.$router.push('/');
      } catch { this.$router.push('/login'); }
    },
    async fetchData() {
      try {
        const [rooms, amenities, beds] = await Promise.all([
          api.get('/rooms/'),
          api.get('/amenities/'),
          api.get('/bed-options/')
        ]);
        this.rooms = rooms.data;
        this.allAmenities = amenities.data;
        this.allBedOptions = beds.data;
      } catch { this.showError('Ошибка загрузки данных'); }
    },
    formatAPIDate(date) {
      if (!date || !(date instanceof Date)) return null;
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    formatDateForInput(dateString) {
      if (!dateString) return '';
      const d = new Date(dateString);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    },
    handleApiError(error, msg) {
      this.showError(error.response?.data?.detail || msg);
    },
    showError(message) {
      this.notification = { type: 'error', message };
      setTimeout(() => this.notification = null, 5000);
    },
    showSuccess(message) {
      this.notification = { type: 'success', message };
      setTimeout(() => this.notification = null, 5000);
    }
  }
}
</script>

<style scoped>
.admin-panel { max-width: 1200px; margin: 0 auto; padding: var(--spacing-xl); }

.section-card {
  background: var(--color-white); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm); padding: var(--spacing-xl); margin-bottom: var(--spacing-xl);
}

.rooms-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--spacing-lg); padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-gray-200);
}
.rooms-header h3 { margin: 0; font-size: var(--text-xl); font-weight: 600; color: var(--color-gray-900); }

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-primary); color: white;
  border: none; border-radius: var(--radius-md); font-weight: 500; cursor: pointer;
}
.btn-primary:hover { background: var(--color-primary-dark); transform: translateY(-1px); box-shadow: var(--shadow-md); }

.room-list { display: grid; gap: var(--spacing-md); }

.notification {
  position: fixed; bottom: var(--spacing-xl); right: var(--spacing-xl);
  padding: var(--spacing-md) var(--spacing-lg); border-radius: var(--radius-lg);
  color: white; z-index: var(--z-tooltip); box-shadow: var(--shadow-lg);
  animation: slideIn 0.3s ease;
}
.notification.success { background: var(--color-success); }
.notification.error { background: var(--color-error); }

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .admin-panel { padding: var(--spacing-md); }
  .section-card { padding: var(--spacing-md); }
  .rooms-header { flex-direction: column; gap: var(--spacing-md); align-items: flex-start; }
}
</style>
