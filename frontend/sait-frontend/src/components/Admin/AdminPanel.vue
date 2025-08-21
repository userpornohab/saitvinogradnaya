<template>
  <div class="admin-panel">
    <!-- Заголовок -->
    <div class="admin-header">
      <h2>Административная панель</h2>
      <router-link to="/" class="back-button">← На главную</router-link>
    </div>

    <!-- Список номеров -->
    <RoomList 
      :rooms="rooms"
      :selected-room-id="selectedRoomId"
      @add-room="startNewRoom"
      @select-room="selectRoom"
      @delete-room="deleteRoom"
      @toggle-price="togglePriceManagement"
      @toggle-booking="toggleBookingManagement"
    />

    <!-- Форма редактирования номера -->
    <RoomForm 
      v-if="selectedRoom || isNewRoom"
      :room="selectedRoom"
      :is-new-room="isNewRoom"
      :all-amenities="allAmenities"
      :all-bed-options="allBedOptions"
      @submit="handleRoomSubmit"
      @cancel="cancelEdit"
      @add-amenity="addAmenity"
      @delete-amenity="deleteAmenity"
      @add-bed-option="addBedOption"
      @delete-bed-option="deleteBedOption"
      @set-main-photo="setMainPhoto"
      @delete-photo="deletePhoto"
      @upload-photo="uploadPhoto"
    />

    <!-- Управление ценами -->
    <PriceManager 
      v-if="showPriceManagement"
      :room="selectedPriceRoom"
      @close="closePriceManagement"
      @create-period="createPricePeriod"
      @delete-period="deletePricePeriod"
      @copy-periods="copyPricePeriodsToNextYear"
    />

    <!-- Управление бронированиями -->
    <BookingManager 
      :show-booking-management="showBookingManagement"
      :selected-booking-room="selectedBookingRoom"
      @update-bookings="handleBookingsUpdate"
      @close="closeBookingManagement"
      @create-booking="createBooking"
      @save-booking="saveBooking"
      @delete-booking="deleteBooking"
    />

    <!-- Уведомления -->
    <NotiFicationMesage :notification="notification" />
  </div>
</template>

<script>
import axios from 'axios';
import RoomList from './RoomList.vue';
import RoomForm from './RoomForm.vue';
import PriceManager from './PriceManager.vue';
import BookingManager from './BookingManager.vue';
import NotiFicationMesage from './NotiFicationMesage.vue';

export default {
  components: {
    RoomList,
    RoomForm,
    PriceManager,
    BookingManager,
    NotiFicationMesage
  },
  data() {
    return {
      rooms: [],
      allAmenities: [],
      allBedOptions: [],
      selectedRoom: null,
      selectedRoomId: null,
      selectedFiles: [],
      isNewRoom: false,
      showPriceManagement: false,
      selectedPriceRoom: null,
      selectedOccupancyRoom: null,
      occupiedDates: {},
      pricePeriods: [],
      newPrice: null,
      countgostprice: null,
      startDate: null,
      endDate: null,
      isCopying: false,
      notification: null,
      showBookingManagement: false,
      selectedBookingRoom: null,
      bookings: [],
      bookingStartDate: null,
      bookingEndDate: null,
      guest_name: '',
      guest_phone: '',
      guest_comment: '',
      number_of_guests: 1
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
    handleBookingsUpdate(updatedBookings) {
      const roomIndex = this.rooms.findIndex(
        r => r.id === this.selectedBookingRoom.id
      );
      
      if (roomIndex !== -1) {
        this.rooms[roomIndex].bookings = updatedBookings;
      }
    },
    // === Основные методы ===
    async checkAdminStatus() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://localhost:8000/users/me/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!response.data.is_superuser) this.$router.push('/');
      } catch (error) {
        this.$router.push('/login');
      }
    },

    async fetchData() {
      try {
        const [roomsRes, amenitiesRes, bedsRes] = await Promise.all([
          axios.get('http://localhost:8000/rooms/'),
          axios.get('http://localhost:8000/amenities/'),
          axios.get('http://localhost:8000/bed-options/')
        ]);
        
        this.rooms = roomsRes.data;
        this.allAmenities = amenitiesRes.data;
        this.allBedOptions = bedsRes.data;
      } catch (error) {
        this.showError('Ошибка загрузки данных');
      }
    },

    // === Методы для работы с номерами ===
    startNewRoom() {
      this.resetForm();
      this.isNewRoom = true;
      this.selectedRoom = null;
    },

    selectRoom(room) {
      this.selectedRoomId = room.id;
      this.showBookingManagement = false;       
      this.showPriceManagement = false;
      this.selectedBookingRoom = null;
      this.selectedPriceRoom = null;
      this.selectedRoom = room;
      this.isNewRoom = false;
    },

    cancelEdit() {
      this.selectedRoomId = null; 
      this.selectedRoom = null;
      this.isNewRoom = false;
      this.resetForm();
    },

    resetForm() {
      this.newRoom = {
        title: '',
        title_dop: '',
        floor: 1,
        description: '',
        max_guests: 2,
        number_of_rooms: 1,
        amenities: [],
        bed_options: []
      };
      this.showAmenityForm = false;
      this.showBedForm = false;
    },

    async handleRoomSubmit(roomData) {
      try {
        let response;
        if (this.selectedRoom) {
          response = await axios.put(
            `http://localhost:8000/rooms/${this.selectedRoom.id}`,
            roomData,
            { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
          );
          
          const updatedRoom = response.data;
          this.rooms = this.rooms.map(r => 
            r.id === updatedRoom.id ? updatedRoom : r
          );
          this.selectedRoom = updatedRoom;
        } else {
          response = await axios.post(
            'http://localhost:8000/rooms/',
            roomData,
            { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
          );
          this.rooms.push(response.data);
          this.resetForm();
        }

        this.showSuccess('Изменения сохранены');
      } catch (error) {
        this.handleApiError(error, 'Ошибка сохранения');
      }
    },

    async deleteRoom(roomId) {
      if (confirm('Вы уверены, что хотите удалить этот номер?')) {
        try {
          await axios.delete(
            `http://localhost:8000/rooms/${roomId}`,
            { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
          );
          this.rooms = this.rooms.filter(r => r.id !== roomId);
          this.showSuccess('Номер удален');
        } catch (error) {
          this.handleApiError(error, 'Ошибка удаления номера');
        }
      }
    },

    // === Методы для работы с фотографиями ===
    async uploadPhoto(files) {
      try {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        const response = await axios.post(
          `http://localhost:8000/rooms/${this.selectedRoom.id}/upload-photos`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );

        this.selectedRoom.photos = [
          ...this.selectedRoom.photos,
          ...response.data
        ];
        this.showSuccess(`Загружено ${response.data.length} фото`);
      } catch (error) {
        this.handleApiError(error, 'Ошибка загрузки фото');
      }
    },

    async setMainPhoto(photo) {
      try {
        await axios.patch(
          `http://localhost:8000/rooms/${this.selectedRoom.id}/photos/${photo.id}`, 
          { is_main: true },
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        
        this.selectedRoom.photos = this.selectedRoom.photos.map(p => ({
          ...p,
          is_main: p.id === photo.id
        }));
        this.showSuccess('Главное фото обновлено');

      } catch (error) {
        this.handleApiError(error, 'Ошибка обновления фото');
      }
    },

    async deletePhoto(photo) {
      try {
        await axios.delete(
          `http://localhost:8000/rooms/${this.selectedRoom.id}/photos/${photo.id}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        
        this.selectedRoom.photos = this.selectedRoom.photos.filter(p => p.id !== photo.id);
        this.showSuccess('Фото удалено');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления фото');
      }
    },

    // === Методы для удобств и кроватей ===
    async addAmenity(amenity) {
      const formData = new FormData();
      formData.append('name', amenity.name);
      formData.append('icon', amenity.iconFile);

      try {
        const response = await axios.post(
          'http://localhost:8000/amenities/',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        this.allAmenities.push(response.data);
        this.showSuccess('Удобство добавлено');
        return response.data;
      } catch (error) {
        this.handleApiError(error, 'Ошибка добавления удобства');
        return null;
      }
    },

    async deleteAmenity(amenityId) {
      try {
        await axios.delete(
          `http://localhost:8000/amenities/${amenityId}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        this.allAmenities = this.allAmenities.filter(a => a.id !== amenityId);
        this.showSuccess('Удобство удалено');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления удобства');
      }
    },

    async addBedOption(bedOption) {
      const formData = new FormData();
      formData.append('name', bedOption.name);
      formData.append('icon', bedOption.iconFile);

      try {
        const response = await axios.post(
          'http://localhost:8000/bed-options/',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        this.allBedOptions.push(response.data);
        this.showSuccess('Тип кровати добавлен');
        return response.data;
      } catch (error) {
        this.handleApiError(error, 'Ошибка добавления типа кровати');
        return null;
      }
    },

    async deleteBedOption(bedId) {
      try {
        await axios.delete(
          `http://localhost:8000/bed-options/${bedId}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        this.allBedOptions = this.allBedOptions.filter(b => b.id !== bedId);
        this.showSuccess('Тип кровати удален');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления типа кровати');
      }
    },

    // === Методы для работы с ценами ===
    togglePriceManagement(room) {
      this.selectedRoomId = room.id;
      this.selectedPriceRoom = room;
      this.showPriceManagement = true;
      this.showBookingManagement = false;
      this.selectedRoom = null;
      
      // Открываем текущий год по умолчанию
      const currentYear = new Date().getFullYear();
      this.openPriceYears = { [currentYear]: true };
    },

    closePriceManagement() {
      this.selectedRoomId = null;
      this.showPriceManagement = false;
      this.selectedPriceRoom = null;
    },

    async createPricePeriod(periodData) {
      try {
        const url = `http://127.0.0.1:8000/price-periods/rooms/${this.selectedPriceRoom.id}/price-periods`;
      const response = await axios.post(
        url,
        periodData,
        { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
      );
      
      this.selectedPriceRoom.price_periods.push(response.data);
      this.showSuccess('Ценовой период создан');
      return response.data;
    } catch (error) {
      this.handleApiError(error, 'Ошибка создания периода');
      return null;
    }
  },

  async deletePricePeriod(periodId) {
    try {
      await axios.delete(`http://127.0.0.1:8000/price-periods/${periodId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      this.selectedPriceRoom.price_periods = 
        this.selectedPriceRoom.price_periods.filter(p => p.id !== periodId);
      this.showSuccess('Период удален');
    } catch (error) {
      this.handleApiError(error, 'Ошибка удаления периода');
    }
  },

  async copyPricePeriodsToNextYear() {
    if (!this.selectedPriceRoom?.id) return;
    
    try {
      this.isCopying = true;
      const response = await axios.post(
        `http://localhost:8000/price-periods/rooms/${this.selectedPriceRoom.id}/copy-price-periods-to-next-year`,
        {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
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
      const response = await axios.get(
        `http://localhost:8000/rooms/${this.selectedPriceRoom.id}`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
      );
      
      this.selectedPriceRoom.price_periods = response.data.price_periods;
    } catch (error) {
      this.handleApiError(error, 'Ошибка обновления периодов');
    }
  },

  // === Методы для работы с бронированиями ===
  toggleBookingManagement(room) {
    this.selectedRoom = null;
    this.selectedRoomId = room.id;
    this.selectedBookingRoom = { ...room, bookings: room.bookings || [] };
    this.showBookingManagement = true;
    this.showPriceManagement = false;
    
    // Открываем текущий год по умолчанию
    const currentYear = new Date().getFullYear();
    this.openBookingYears = { [currentYear]: true };
  },

  closeBookingManagement() {
    this.selectedRoomId = null;
    this.showBookingManagement = false;
    this.selectedBookingRoom = null;
  },

  async createBooking(bookingData) {
    try {
      const response = await axios.post(
        'http://localhost:8000/bookings/', 
        bookingData,
        { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
      );
      
      this.selectedBookingRoom.bookings.push(response.data);
      this.showSuccess('Бронирование создано');
      return response.data;
    } catch (error) {
      this.handleApiError(error, 'Ошибка создания бронирования');
      return null;
    }
  },

  async saveBooking(bookingData) {
    try {
      const response = await axios.patch(
        `http://localhost:8000/bookings/${bookingData.id}`,
        bookingData,
        { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
      );
      
      // Обновляем данные в интерфейсе
      const index = this.selectedBookingRoom.bookings.findIndex(b => b.id === bookingData.id);
      if (index !== -1) {
        this.selectedBookingRoom.bookings.splice(index, 1, response.data);
      }

      this.showSuccess('Бронирование обновлено');
      return response.data;
    } catch (error) {
      this.handleApiError(error, 'Ошибка обновления бронирования');
      return null;
    }
  },

  async deleteBooking(bookingId) {
    if (confirm('Вы уверены, что хотите удалить это бронирование?')) {
      try {
        await axios.delete(
          `http://localhost:8000/bookings/${bookingId}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
        );
        
        this.selectedBookingRoom.bookings = this.selectedBookingRoom.bookings.filter(
          b => b.id !== bookingId
        );
        this.showSuccess('Бронирование удалено');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления бронирования');
      }
    }
  },

  // === Вспомогательные методы ===
  handleKeyPress(event) {
    if (event.key === 'Escape') {
      if (this.showPriceManagement || this.showBookingManagement) {
        this.resetdataForm();
      }
    }
  },

  handleApiError(error, defaultMessage) {
    const message = error.response?.data?.detail || defaultMessage;
    this.showError(message);
  },

  showError(message) {
    this.notification = { type: 'error', message };
    setTimeout(() => this.notification = null, 5000);
  },

  showSuccess(message) {
    this.notification = { type: 'success', message };
    setTimeout(() => this.notification = null, 5000);
  },

  formatAPIDate(date) {
    if (!date || !(date instanceof Date)) return null;
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  resetdataForm() {
    this.newPrice = null;
    this.startDate = null;
    this.countgostprice = null;
    this.endDate = null;
    this.guest_name = '';
    this.guest_phone = '';
    this.guest_comment = '';
    this.number_of_guests = 1;
  }
}}
</script>

<style scoped>
.admin-panel {
  max-width: 1120px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.back-button {
  color: #666;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.back-button:hover {
  color: #333;
}
</style>