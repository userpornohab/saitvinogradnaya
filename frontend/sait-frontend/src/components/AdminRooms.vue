<template>
  <div class="admin-panel">
    <!-- Заголовок -->
    <AdminHeader></AdminHeader>

    <!-- Список номеров и кнопка добавления -->
    <div class="section-card">
      <div class="rooms-header">
        <h3>Список номеров</h3>
        <button class="add-button" @click="startNewRoom">+ Добавить номер</button>
      </div>
      
      <div class="room-list">
        <div 
          v-for="room in rooms" 
          :key="room.id" 
          class="room-card"
          :class="{selected: selectedRoomId === room.id}"
        >
          <img 
            v-if="room.photos.length" 
            :src="getMainPhoto(room.photos)" 
            class="room-thumb"
          >
          <div>
              <div class="room-header">
              <h4>{{ room.title }}</h4>
              <button @click.stop="deleteRoom(room.id)" title="Удалить">🗑</button>
            </div>
            <div class="room-actions">
              <button @click.stop="togglePriceManagement(room)" title="Управление ценами">💰</button>
              <button @click.stop="toggleBookingManagement(room)" title="Бронирования">📅</button>
              <button @click="selectRoom(room)" title="Редактировать">✏️</button>
            </div>
          </div>
          
        </div>
        
      </div>
    </div>

    <!-- Блок редактирования -->
    <div class="section-card" v-if="selectedRoom || isNewRoom">
      <div class="edit-header">
        <h3>{{ isNewRoom ? 'Новый номер' : `Редактирование: ${selectedRoom.title}` }}</h3>
        <button v-if="!isNewRoom" @click="cancelEdit">×</button>
      </div>

      <!-- Форма редактирования -->
      <form @submit.prevent="handleRoomSubmit" class="border-bot">
        <div class="form-grid">
          <div class="form-group">
            <label>Название:</label>
            <input v-model="newRoom.title" required>
          </div>
          
          <div class="form-group">
            <label>Доп. название:</label>
            <input v-model="newRoom.title_dop">
          </div>
          
          <div class="form-group">
            <label>Описание:</label>
            <textarea v-model="newRoom.description" required rows="4"></textarea>
          </div>
          
          <div class="form-group">
            <label>Макс. гостей:</label>
            <input type="number" v-model.number="newRoom.max_guests" min="1" required>
          </div>
          <div class="form-group">
            <label>Этаж:</label>
            <input type="number" v-model.number="newRoom.floor" min="1" required>
          </div>
          
          <div class="form-group border-bot" >
            <label>Количество номеров:</label>
            <input type="number" v-model.number="newRoom.number_of_rooms" min="1" required>
          </div>

          <!-- Управление удобствами -->
          <div class="form-group full-width border-bot">
            <div class="manage-section">
              <div class="section-header">
                <h4>Удобства</h4>
                <div class="selection-grid">
                <div v-for="amenity in allAmenities" :key="amenity.id" class="selection-item">
                  <label>
                    <input 
                      type="checkbox" 
                      :value="amenity.id" 
                      v-model="newRoom.amenities"
                    >
                    <img :src="getIconUrl(amenity.icon)" :alt="amenity.name" class="icon-small" width="100" height="100">
                    {{ amenity.name }}
                    <button 
                    @click.stop="deleteAmenity(amenity.id)" 
                    class="delete-btn"
                    title="Удалить удобство"
                  >
                    ×
                  </button>
                  </label>
                </div>
              </div>
                <button type="button" @click="showAmenityForm = !showAmenityForm">
                  {{ showAmenityForm ? 'Скрыть' : 'Добавить' }}
                </button>
              </div>
              
              <div v-if="showAmenityForm" class="add-form">
                <input v-model="newAmenity.name" placeholder="Название удобства">
                <div class="add-form-marg">
                  <div class="custom-file-input">
                    <label class="file-input-label">
                      <input 
                        type="file" 
                        @change="handleAmenityIcon"
                        accept="image/svg+xml, image/png"
                        class="hidden-input"
                      >
                      <span class="button-content">
                        <svg class="upload-icon" viewBox="0 0 24 24">
                          <path d="M19 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5l-1-1v6a3 3 0 0 0 3 3h12a3 3 0 0 0 3-3v-6l-1 1z"/>
                          <path d="M12 15l5-6h-3V2h-4v7H7l5 6z"/>
                        </svg>
                        Выберите иконку
                      </span>
                    </label>
                    <div v-if="newAmenity.iconFile" class="file-info">
                      {{ newAmenity.iconFile.name }}
                    </div>
                  </div>
                  <button type="button" @click="addAmenity">Добавить</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Управление кроватями -->
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
                      v-model="newRoom.bed_options"
                    >
                    <img :src="getIconUrl(bed.icon)" :alt="bed.name" class="icon-small" width="100" height="100">
                    {{ bed.name }}
                    <button 
                    @click.stop="deleteBedOption(bed.id)" 
                    class="delete-btn"
                    title="Удалить тип кровати"
                  >
                    ×
                  </button>
                  </label>
                </div>
              </div> 
                <button type="button" @click="showBedForm = !showBedForm">
                  {{ showBedForm ? 'Скрыть' : 'Добавить' }}
                </button>
              </div>
              
              <div v-if="showBedForm" class="add-form">
                <input v-model="newBedOption.name" placeholder="Название типа кровати">
                <div class="add-form-marg">
                  <div class="custom-file-input">
                    <label class="file-input-label">
                      <input 
                        type="file" 
                        @change="handleBedIcon"
                        accept="image/svg+xml, image/png"
                        class="hidden-input"
                      >
                      <span class="button-content">
                        <svg class="upload-icon" viewBox="0 0 24 24">
                          <path d="M19 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5l-1-1v6a3 3 0 0 0 3 3h12a3 3 0 0 0 3-3v-6l-1 1z"/>
                          <path d="M12 15l5-6h-3V2h-4v7H7l5 6z"/>
                        </svg>
                        Выберите иконку
                      </span>
                    </label>
                    <div v-if="newBedOption.iconFile" class="file-info">
                      {{ newBedOption.iconFile.name }}
                    </div>
                  </div>
                  <button type="button" @click="addBedOption">Добавить</button>
                </div>
                
              </div>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-button">
            {{ isNewRoom ? 'Создать' : 'Обновить' }}
          </button>
          <button type="button" @click="cancelEdit" v-if="!isNewRoom">Отмена</button>
        </div>
      </form>

      <!-- Управление фотографиями -->
      <div class="photo-management" v-if="!isNewRoom">
        <h4>Фотографии номера</h4>
        <div class="photo-grid">
          <div v-for="photo in selectedRoom.photos" :key="photo.id" class="photo-card">
            <img :src="getPhotoUrl(photo.url)" class="photo-preview">
            <div class="photo-controls">
              <button 
                @click="setMainPhoto(photo)" 
                :class="{active: photo.is_main}"
              >
                ★
              </button>
              <button @click="deletePhoto(photo)">×</button>
            </div>
          </div>
        </div>
        <div class="upload-section">
          <label class="file-input-label">
                      <input 
                      type="file" 
                      @change="handlePhotoUpload" 
                      accept="image/*" 
                      ref="fileInput"
                      multiple
                        class="hidden-input"
                      >
                      <span class="button-content">
                        <svg class="upload-icon" viewBox="0 0 24 24">
                          <path d="M19 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5l-1-1v6a3 3 0 0 0 3 3h12a3 3 0 0 0 3-3v-6l-1 1z"/>
                          <path d="M12 15l5-6h-3V2h-4v7H7l5 6z"/>
                        </svg>
                        Загрузите фотографии
                      </span>
                    </label>
          <button 
            @click="uploadPhoto" 
            :disabled="selectedFiles.length === 0"  
          >
            Загрузить ({{ selectedFiles.length }})
          </button>
        </div>
      </div>
    </div>
    <!-- Блок управления ценами -->
  <div class="section-card price-management" v-if="showPriceManagement">
    <div class="edit-header">
      <h3>Управление ценами для {{ selectedPriceRoom.title }}</h3>
      <button @click="closePriceManagement">×</button>
    </div>

    <!-- Датапикер и форма ввода цены -->
    <div class="price-controls">
      <SyncDateRangePicker 
        v-model:start-date="startDate" 
        v-model:end-date="endDate"
        :number-of-rooms="selectedRoom?.number_of_rooms"
        @clear="resetdataForm()"
      />
      
      <div class="price-input-group">
        <input 
          type="number" 
          v-model.number="newPrice" 
          placeholder="Цена"
          min="1"
          class="price-input"
        >
        <input 
          type="number" 
          v-model.number="countgostprice" 
          placeholder="гостей"
          min="1"
          
          :max="selectedPriceRoom.max_guests"
          class="price-input"
        >
        
  <div class="price-actions">
      <button 
        class="copy-button"
        @click="createPricePeriod"
        :disabled="!isFormValid"
      >
        Установить цену
      </button>
      
      <!-- Добавленная кнопка -->
      <button 
        class="copy-button"
        @click="copyPricePeriodsToNextYear"
        :disabled="isCopying || !selectedPriceRoom.price_periods.length"
      >
        {{ isCopying ? 'Копирование...' : 'Копировать на следующий год' }}
      </button>
    </div>
      </div>
    </div>

    <!-- Список существующих периодов -->
    <div class="periods-list">
      <div v-for="(yearPeriods, year) in groupedPricePeriods" :key="year" class="year-group">
        <div class="accordion-header" @click="togglePriceYear(year)">
          <h4>Ценовые периоды за {{ year }} год</h4>
          <span class="accordion-icon">
            {{ openPriceYears[year] ? '▼' : '▶' }}
          </span>
        </div>
        
        <transition name="slide">
          <div v-if="openPriceYears[year]" class="accordion-content">
            <div v-for="period in yearPeriods" :key="period.id" class="period-item">
              <span class="dates">{{ formatDate(period.start_date) }} - {{ formatDate(period.end_date) }} за {{ period.number_of_guests }} гостей</span>
              <span class="price">{{ period.price }} ₽</span>
              <button class="delete-btnn" @click.stop="deletePricePeriod(period.id)">×</button>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>

    <!-- Блок просмотра занятости -->
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
            <textarea v-model="guest_comment"               
            placeholder="Комментарий"
></textarea>
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
          <!-- Заголовок аккордеона для бронирования -->
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
          
          <!-- Детали бронирования -->
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
  </div>
  <transition name="fade">
      <div v-if="notification" :class="['notification', notification.type]">
        {{ notification.message }}
      </div>
    </transition>
</template>

<script>
import axios from 'axios';

import SyncDateRangePicker  from './Admin/SyncDateRangePicker.vue';
import AdminHeader  from './AdminHeader.vue';



export default {
  components: {
    SyncDateRangePicker,
    AdminHeader
  },
  data() {
    return {
    activeBookingId: null, 
currentYear: new Date().getFullYear(),      rooms: [],
      openPriceYears: {},
      openBookingYears: {},
      activeAccordion: null,
    editingBookings: {},
    originalBookings: {},
      editingBooking: null, // Текущее редактируемое бронирование
    showEditForm: false, // Показать/скрыть форму
      allAmenities: [],
      allBedOptions: [],
      selectedRoom: null,
      selectedFiles: [],
      showAmenityForm: false,
      showBedForm: false,
      isNewRoom: false,
      showPriceManagement: false,
      selectedPriceRoom: null,
      selectedOccupancyRoom: null,
      occupiedDates: {},
      pricePeriods: [],
      newPrice: null,
      countgostprice:  null,
      startDate: null,
      endDate: null,
      isCopying: false,

      newRoom: {
        title: '',
        title_dop: '',
        description: '',
        floor: 1,
        max_guests: 2,
        number_of_rooms: 1,
        amenities: [],
        bed_options: []
      },
      newAmenity: {
        name: '',
        iconFile: null
      },
      newBedOption: {
        name: '',
        iconFile: null
      },
      editingRoom: null,  // Добавлено для отслеживания редактируемой комнаты
      notification: null,
      showBookingManagement: false,
      selectedBookingRoom: null,
      bookings: [],
      bookingStartDate: null,
      bookingEndDate: null,
      selectedRoomId: null,
    };
  },
   computed: {
    // Проверка валидности формы цен
    isFormValid() {
      return this.newPrice > 0 && 
             this.countgostprice > 0 &&
             this.startDate && 
             this.endDate && 
             this.startDate <= this.endDate
    },
    
    // Проверка валидности формы бронирования
    isBookingFormValid() {
      return this.startDate && 
             this.endDate && 
             this.startDate <= this.endDate;
    },
    
    // Группировка ценовых периодов по годам
    groupedPricePeriods() {
    if (!this.selectedPriceRoom?.price_periods) return {};
    
    return this.selectedPriceRoom.price_periods.reduce((groups, period) => {
      const year = new Date(period.start_date).getFullYear();
      if (!groups[year]) groups[year] = [];
      groups[year].push(period);
      return groups;
    }, {});
  },
    
    // Группировка бронирований по годам
     groupedBookings() {
    if (!this.selectedBookingRoom?.bookings) return {};
    
    const bookings = [...this.selectedBookingRoom.bookings].reverse(); // Добавлено reverse()
    
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
  },

    

  },
  async mounted() {
    window.addEventListener('keydown', this.handleKeyPress);
    await this.checkAdminStatus();
    await this.fetchData();
  },
      // Проверка, является ли год текущим
    isCurrentYear(year) {
      try {
        // Преобразуем значение года в число
        const yearNum = parseInt(String(year), 10);
        const currentYear = new Date().getFullYear();
        return !isNaN(yearNum) && yearNum === currentYear;
      } catch (e) {
        return false;
      }
    },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyPress);
  },
  methods: {
    // === Методы для работы с ценами ===
    
    // Переключение видимости года цен
    togglePriceYear(year) {
      this.openPriceYears = {
        ...this.openPriceYears,
        [year]: !this.openPriceYears[year]
      };
    },
    
    // Открытие управления ценами
    togglePriceManagement(room) {
      this.selectedRoomId = room.id;
      this.selectedPriceRoom = room;
      this.showPriceManagement = true;
      this.showBookingManagement = false;
      this.selectedRoom = null;
      this.resetdataForm();
      
      // Открываем текущий год по умолчанию
      const currentYear = new Date().getFullYear();
      this.openPriceYears = { [currentYear]: true };
    },
    
    // Закрытие управления ценами
    closePriceManagement() {
      this.selectedRoomId = null;
      this.showPriceManagement = false;
      this.selectedPriceRoom = null;
    },
    
    // Создание ценового периода

    
    // Удаление ценового периода
    async deletePricePeriod(periodId) {
      try {
        await axios.delete(`http://127.0.0.1:8000/price-periods/${periodId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        this.selectedPriceRoom.price_periods = 
          this.selectedPriceRoom.price_periods.filter(p => p.id !== periodId);
        this.showSuccess('Период удален');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления периода');
      }
    },
    
    // Копирование периодов на следующий год
    async copyPricePeriodsToNextYear() {
      if (!this.selectedPriceRoom?.id) return;
      
      try {
        this.isCopying = true;
        const response = await axios.post(
          `http://localhost:8000/price-periods/rooms/${this.selectedPriceRoom.id}/copy-price-periods-to-next-year`,
          {},
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        await this.refreshPricePeriods();
        this.showSuccess(response.data.message);
      } catch (error) {
        this.handleApiError(error, 'Ошибка копирования периодов');
      } finally {
        this.isCopying = false;
      }
    },
    
    // Обновление списка периодов
    async refreshPricePeriods() {
      try {
        const response = await axios.get(
          `http://localhost:8000/rooms/${this.selectedPriceRoom.id}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        this.selectedPriceRoom.price_periods = response.data.price_periods;
      } catch (error) {
        this.handleApiError(error, 'Ошибка обновления периодов');
      }
    },
    
    // === Методы для работы с бронированиями ===
    
    // Переключение видимости года бронирований
    toggleBookingYear(year) {
      this.openBookingYears = {
        ...this.openBookingYears,
        [year]: !this.openBookingYears[year]
      };
    },
    calculateNights(checkIn, checkOut) {
      try {
        const start = new Date(checkIn);
        const end = new Date(checkOut);
        
        // Проверка валидности дат
        if (isNaN(start) || isNaN(end)) return 0;
        
        // Рассчет разницы в днях
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
    // Открытие управления бронированиями
    toggleBookingManagement(room) {
      this.selectedRoom = null;
      this.selectedRoomId = room.id;
      this.selectedBookingRoom = {
        ...room,
        bookings: room.bookings || []
      };
      this.showBookingManagement = true;
      this.showPriceManagement = false;
      this.loadBookings(room.id);
      
      // Открываем текущий год по умолчанию
      const currentYear = new Date().getFullYear();
      this.openBookingYears = { [currentYear]: true };
    },
    
    // Закрытие управления бронированиями
    closeBookingManagement() {
      this.selectedRoomId = null;
      this.showBookingManagement = false;
      this.selectedBookingRoom = null;
    },
    
    // Переключение деталей бронирования
    toggleBookingAccordion(bookingId) {
      if (this.activeAccordion === bookingId) {
        this.activeAccordion = null;
        this.activeBookingId = null; // Сбросить выделение
        return;
      }
      
      if (this.activeAccordion === bookingId) {
        this.activeAccordion = null;
        return;
      }
      
      const booking = this.selectedBookingRoom.bookings.find(b => b.id === bookingId);
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
      this.activeBookingId = bookingId; // Установить выделение
      this.activeAccordion = bookingId;
    },
    
    // Создание бронирования
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
        
        this.selectedBookingRoom.bookings.push(response.data);
        this.calculateOccupiedDates();
        this.showSuccess('Бронирование создано');
        this.toggleBookingAccordion(response.data.id);
        this.resetdataForm();
      } catch (error) {
        this.resetdataForm();
        this.handleApiError(error, 'Ошибка создания бронирования');
      }
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
        return true
      }
    // Убраны лишние экранирующие символы \ перед -
    const phoneRegex = /^(\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/;
    return phoneRegex.test(phone);
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
      // Добавляем новые поля
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
    
    // Обновляем данные в интерфейсе
    const index = this.selectedBookingRoom.bookings.findIndex(b => b.id === booking.id);
    if (index !== -1) {
      this.selectedBookingRoom.bookings.splice(index, 1, response.data);
    }

    this.calculateOccupiedDates();
    this.showSuccess('Бронирование обновлено');
    this.activeAccordion = null;
  } catch (error) {
    this.handleApiError(error, 'Ошибка обновления бронирования');
  }
},
  
cancelEditBooking(bookingId) {
  // Восстанавливаем оригинальные данные
  const index = this.selectedBookingRoom.bookings.findIndex(b => b.id === bookingId);
  if (index !== -1 && this.originalBookings[bookingId]) {
    this.selectedBookingRoom.bookings.splice(index, 1, this.originalBookings[bookingId]);
  }
  
  this.activeAccordion = null;
  delete this.editingBookings[bookingId];
  delete this.originalBookings[bookingId];
},
  

  // Форматирование даты для API


    handleKeyPress(event) {
  if (event.key === 'Escape') {
    if (this.showPriceManagement || this.showBookingManagement) {
      this.resetdataForm();
    }
  }
},


async deleteBooking(bookingId) {
  if (confirm('Вы уверены, что хотите удалить эту бронь?')){
    try {
        await axios.delete(`http://localhost:8000/bookings/${bookingId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        // Удаляем бронирование локально
        this.selectedBookingRoom.bookings = this.selectedBookingRoom.bookings.filter(
          b => b.id !== bookingId
        );
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
    
    // Обеспечиваем реактивность
    this.selectedBookingRoom = {
      ...this.selectedBookingRoom,
      bookings: response.data
    };
    
    this.calculateOccupiedDates();
  } catch (error) {
    this.handleApiError(error, 'Ошибка загрузки бронирований');
  }
},



calculateOccupiedDates() {
  if (!this.selectedBookingRoom?.bookings) {
    this.occupiedDates = {};
    return;
  }
  
  const dates = {};
  this.selectedBookingRoom.bookings.forEach(booking => {
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



    // Обработчики дат из DateRangePicker
    setStartDate(date) {
      this.startDate = date
    },
    
    setEndDate(date) {
      this.endDate = date
    },

    // Создание нового периода
    async createPricePeriod() {
    try {
      const periodData = {
        start_date: this.formatAPIDate(this.startDate),
        end_date: this.formatAPIDate(this.endDate),
        price: this.newPrice,
        number_of_guests: this.countgostprice,
      };

      // Правильный URL с динамическим ID комнаты
      const url = `http://127.0.0.1:8000/price-periods/rooms/${this.selectedPriceRoom.id}/price-periods`;

      const response = await axios.post(
        url,
        periodData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      // Добавляем новый период в список
      this.selectedPriceRoom.price_periods.push(response.data);
      this.resetForm();
      this.showSuccess('Ценовой период создан');
      this.resetdataForm()
    } catch (error) {
      this.handlePriceError(error);
    }
  },
  formatAPIDate(date) {
  if (!date || !(date instanceof Date)) return null;
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
},
    // Удаление периода
    

    // Вспомогательные методы
    formatDate(dateString) {
      const options = { day: '2-digit', month: '2-digit', year: 'numeric' }
      return new Date(dateString).toLocaleDateString('ru-RU', options)
    },

    formatDateForAPI(date) {
      return date.toISOString().split('T')[0]
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

    resetdataForm() {
      this.newPrice = null
      this.startDate = null
      this.countgostprice = null
      this.endDate = null
    },

    handlePriceError(error) {
      if (error.response?.status === 422) {
        this.showError(error.response.data.detail || 'Некорректный период')
      } else {
        this.handleApiError(error, 'Ошибка создания периода')
      }
    },

  // Обработчик из DateRangePicker для создания периода
  handleDateRangeSelect({ startDate, endDate, price }) {
    this.createPricePeriod({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      price: price
    });
  },




  
    getIconUrl(icon) {
      return `http://127.0.0.1:8000/${icon}`;
    },
    getPhotoUrl(url) {
      return `http://localhost:8000${url}`;
    },
    getMainPhoto(photos) {
      const main = photos.find(p => p.is_main);
      return main ? this.getPhotoUrl(main.url) : this.getPhotoUrl(photos[0]?.url);
    },

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

    handleAmenityIcon(event) {
      this.newAmenity.iconFile = event.target.files[0];
    },

    async addAmenity() {
      const formData = new FormData();
      formData.append('name', this.newAmenity.name);
      formData.append('icon', this.newAmenity.iconFile);

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
        this.newAmenity = { name: '', iconFile: null };
        this.showAmenityForm = false;
        this.showSuccess('Удобство добавлено');
      } catch (error) {
        this.handleApiError(error, 'Ошибка добавления удобства');
      }
    },

    async deleteAmenity(amenityId) {
      try {
        await axios.delete(
          `http://localhost:8000/amenities/${amenityId}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        this.allAmenities = this.allAmenities.filter(a => a.id !== amenityId);
        this.showSuccess('Удобство удалено');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления удобства');
      }
    },

    handleBedIcon(event) {
      this.newBedOption.iconFile = event.target.files[0];
    },

    async addBedOption() {
      const formData = new FormData();
      formData.append('name', this.newBedOption.name);
      formData.append('icon', this.newBedOption.iconFile);

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
        this.newBedOption = { name: '', iconFile: null };
        this.showBedForm = false;
        this.showSuccess('Тип кровати добавлен');
      } catch (error) {
        this.handleApiError(error, 'Ошибка добавления типа кровати');
      }
    },

    async deleteBedOption(bedId) {
      try {
        await axios.delete(
          `http://localhost:8000/bed-options/${bedId}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        this.allBedOptions = this.allBedOptions.filter(b => b.id !== bedId);
        this.showSuccess('Тип кровати удален');
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления типа кровати');
      }
    },

    async handleRoomSubmit() {
      try {
        // Основное исправление: сохранение price_periods
        const roomData = {
          ...this.newRoom,
          price_periods: this.editingRoom ? this.editingRoom.price_periods : [],
          amenities: this.newRoom.amenities,
          bed_options: this.newRoom.bed_options
        };

        let response;
        if (this.editingRoom) {
          response = await axios.put(
            `http://localhost:8000/rooms/${this.editingRoom.id}`,
            roomData,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`
              }
            }
          );
          
          const updatedRoom = response.data;
          this.rooms = this.rooms.map(r => 
            r.id === updatedRoom.id ? updatedRoom : r
          );
          
          this.selectedRoom = updatedRoom;
          this.newRoom = { 
            ...this.newRoom,
            title: updatedRoom.title,
            title_dop: updatedRoom.title_dop,
            description: updatedRoom.description,
            max_guests: updatedRoom.max_guests,
            floor: updatedRoom.floor,
            number_of_rooms: updatedRoom.number_of_rooms,
            amenities: updatedRoom.amenities.map(a => a.id),
            bed_options: updatedRoom.bed_options.map(b => b.id)
          };
          
        } else {
          response = await axios.post(
            'http://localhost:8000/rooms/',
            roomData,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`
              }
            }
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
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`
              }
            }
          );
          this.rooms = this.rooms.filter(r => r.id !== roomId);
          this.showSuccess('Номер удален');
        } catch (error) {
          this.handleApiError(error, 'Ошибка удаления номера');
        }
      }
    },

    async uploadPhoto() {
      try {
        const formData = new FormData();
        this.selectedFiles.forEach(file => {
          formData.append('files', file);
        });

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

        this.selectedFiles = [];
        this.showSuccess(`Загружено ${response.data.length} фото`);
      } catch (error) {
        this.handleApiError(error, 'Ошибка загрузки фото');
      }
    },

    handlePhotoUpload(event) {
      this.selectedFiles = Array.from(event.target.files || event.dataTransfer.files);
    },

    async setMainPhoto(photo) {
      try {
        await axios.patch(
          `http://localhost:8000/rooms/${this.selectedRoom.id}/photos/${photo.id}`, 
          { is_main: true },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        this.selectedRoom.photos = this.selectedRoom.photos.map(p => ({
          ...p,
          is_main: p.id === photo.id
        }));

      } catch (error) {
        this.handleApiError(error, 'Ошибка обновления фото');
      }
    },

    async deletePhoto(photo) {
      try {
        await axios.delete(
          `http://localhost:8000/rooms/${this.selectedRoom.id}/photos/${photo.id}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        this.selectedRoom.photos = this.selectedRoom.photos.filter(p => p.id !== photo.id);
      } catch (error) {
        this.handleApiError(error, 'Ошибка удаления фото');
      }
    },

    startNewRoom() {
      this.resetForm();
      this.isNewRoom = true;
      this.selectedRoom = null;
    },

    selectRoom(room) {
      this.selectedRoomId = room.id;
      this.showBookingManagement = false;       
      this.showPriceManagement = false;
      this.selectedBookingRoom = null; // Сбрасываем выбранную комнату для бронирований
      this.selectedPriceRoom = null; // Сбрасываем выбранную комнату для цен
      this.selectedRoom = room;
      this.isNewRoom = false;
      this.editRoom(room);
},

    editRoom(room) {
      this.editingRoom = { ...room };
      this.newRoom = {
        title: room.title,
        title_dop: room.title_dop || '',
        description: room.description,
        max_guests: room.max_guests,
        floor: room.floor,
        number_of_rooms: room.number_of_rooms,
        amenities: room.amenities?.map(a => a.id) || [],
        bed_options: room.bed_options?.map(b => b.id) || []
      };
      this.isNewRoom = false;
    },

    cancelEdit() {
      this.showEditForm = false;
      this.editingBooking = null;
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
      this.editingRoom = null;
      this.showAmenityForm = false;
      this.showBedForm = false;
    },


  }
};
</script>
  
<style scoped>
/* Основные стили */
.rooms-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.delete-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.add-button {
  background: #4CAF50;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.add-button:hover {
  background: #45a049;
}

.room-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.room-card {
  background: #f8f9fa;
  display: flex;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.room-card.selected {
  box-shadow: 0 0 0 1px #99c3e6;
  transform: translateY(-2px);
}

.room-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.room-header button{
  background: none;
}


.room-thumb {
  max-width: 100px;
  aspect-ratio: 1 / 1;
  object-fit: cover;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.edit-header h3{
  padding: 0;
}
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
.active{
  background-color: #f1c40f;
}
/* Карточки секций */
.section-card {
  background: #fff;
  border-radius: 10px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.1);
  border: 1px solid #eee;
}
.year-group {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.year-group.current-year {
}

/* Заголовок аккордеона года */
.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
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

/* Контент аккордеона года */
.accordion-content {
  padding: 0 15px;
  background: #fff;
}

/* Элемент бронирования */
.booking-item {
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.booking-item:last-child {
  border-bottom: none;
}

/* Заголовок бронирования */
.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 10px;
  cursor: pointer;
}

.booking-header:hover {
  background-color: #f8f9fa;
}

.section-card h3 {
  margin-top: 0;
  color: #2c3e50;
  margin: auto 0;
}

/* Формы */
.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}



/* Кнопки */
button {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.submit-button {
  background: #3498db;
  color: white;
  margin-right: 30px;
}

.submit-button:hover {
  background: #2980b9;
}

.cancel-button {
  background: #e74c3c;
  color: white;
  margin-left: 1rem;
}

.cancel-button:hover {
  background: #c0392b;
}



/* Списки */
.amenities-list,
.bed-options-list {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}

.amenity-item,
.bed-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eee;
}

.amenity-icon {
  width: 32px;
  height: 32px;
  margin-right: 1rem;
  object-fit: contain;
}

/* Галерея фотографий */
.photo-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.photo-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
}

.photo-item img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.photo-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 0.5rem;
}

.photo-actions button {
  background: rgba(255,255,255,0.9);
  color: #333;
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
}

.photo-actions button.active {
  background: #f1c40f;
  color: white;
}

/* Список номеров */
.room-list {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.room-card {
  display: flex;
  gap: 30px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.room-card:hover {
  transform: translateY(-3px);
}

.room-card.selected {
  border-color: #98c0db;
  background: #f8fbff;
}

.room-thumb {
  width: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.room-actions{
  display: flex;
  gap: 5px;
  padding: 6px 0;

}
.room-actions button {
  background: none;
  border: 1px solid ;
  padding: 0.8rem 1rem;
}

/* Уведомления */
.notification {
  height: fit-content;
  position: fixed;
  
  padding: 1rem;
  border-radius: 4px;
  color: white;
}

.notification.success {
  background: #2ecc71;
}

.notification.error {
  background: #e74c3c;
}

/* Адаптивность */
@media (max-width: 768px) {
  .admin-panel {
    padding: 15px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .amenities-grid,
  .bed-options {
    grid-template-columns: 1fr;
  }

  .room-list {
    grid-template-columns: 1fr;
  }
}

/* Дополнительные эффекты */
button:active {
  transform: scale(0.98);
}
.form-row{
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}
.upload-section{
  margin-top: 80px;
}

.photo-upload-section {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.5rem;
}

.photo-upload-section input[type="file"] {
  flex-grow: 1;
}
input[type="file"]{
  border: none;
  width: auto;
  padding: 0;
}

.add-form{
  margin: 20px 0;
  width: 500px;
}
.add-form-marg{
  margin-top: 20px;
  width: 100%;
  display: flex;
  justify-content: space-between;
}

input, textarea, select {
  box-sizing: border-box;
  width: 500px;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

input:focus, textarea:focus {
  border-color: #3498db;
  outline: none;
}
input.fail,
textarea.fail,
select.fail {
  border-color: #ff4444;
  background-color: #fff5f5;
}

input.fail:focus,
textarea.fail:focus,
select.fail:focus {
  box-shadow: 0 0 0 2px rgba(255, 68, 68, 0.2);
}
.booking-info{
  display: flex;
  gap: 20px;
}

/* Стили для уведомлений */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.notification.error {
  background-color: #ff4444;
}

.notification.success {
  background-color: #4CAF50;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.silca{
  color: black;
  outline: none;
  

}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Стили для добавления отступов в форме */
.add-form-marg {
  margin-top: 1rem;
  display: flex;
  gap: 0.8rem;
  align-items: center;
}

/* Исправление сетки для удобств и кроватей */
.selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.selection-item {
  position: relative;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.selection-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Улучшение отображения иконок */
.icon-small {
  width: 40px;
  height: 40px;
  object-fit: contain;
  margin-right: 0.8rem;
  vertical-align: middle;
}


/* Исправление позиционирования кнопок удаления */
.delete-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  color: #ff4444;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .add-form-marg {
    flex-direction: column;
  }
  
  .selection-grid {
    grid-template-columns: 1fr;
  }
}

.border-bot{
  padding-bottom: 20px ;
  border-bottom: 2px solid #eee;
}
.photo-preview{
  width: 100%;
  height: 100%;
}

.price-input-group{
  display: flex;
  margin: 30px 0;
  max-width: 400px;
  gap: 20px;
  flex-wrap: wrap;
}

.photo-grid{
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}
.photo-card{
  position: relative;
  
  
}
.photo-controls{
  position: absolute;
  bottom: 10px;
  width: 100%;
  display: flex;
  justify-content: space-between;
  

}

.custom-file-input {
  margin: 1rem 0;
}

.hidden-input {
  display: none;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  padding: 0.8rem 1.5rem;
  background: #f0f4f8;
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 20px;
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

.file-info {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #718096;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Адаптивность */
@media (max-width: 768px) {
  .file-input-label {
    width: 100%;
    justify-content: center;
  }
}

.periods-list {
  margin-top: 1.5rem;
  border-radius: 8px;
  overflow: hidden;
}

.period-item {
  padding: 10px 10px;
  display: flex;
  align-items: center;
  background: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s ease;
}

.period-item:last-child {
  border-bottom: none;
}

.period-item:hover {
  background: #f8f9fa;
}

.dates {
  flex: 1;
  font-size: 0.9rem;
  color: #555;
  font-family: 'Roboto Mono', monospace;
}

.price {
  width: 120px;
  text-align: right;
  font-weight: 600;
  color: #2e7d32;
  font-size: 1rem;
}

.price-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.copy-button {
  background-color: #9b59b6;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.copy-button:hover:not(:disabled) {
  background-color: #8e44ad;
}

.copy-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.delete-btnn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: #d32f2f;
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  margin-left: 1rem;
}

.delete-btnn:hover {
  background: #ffebee;
  transform: scale(1.1);
}

.delete-btnn:active {
  transform: scale(0.95);
}

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .period-item {
    flex-wrap: wrap;
    gap: 0.5rem;
    padding: 0.75rem;
  }
  
  .dates {
    width: 100%;
    order: 1;
    font-size: 0.8rem;
  }
  
  .price {
    text-align: left;
    order: 2;
    width: auto;
  }
  
  .delete-btnn {
    order: 3;
    margin-left: auto;
  }
}
.flex{
  display: flex;
  gap: 20px;  
}

.flex input{
  width: 170px;
}

/* Стили для аккордеона */
.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background: #f8f9fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.accordion-header:hover {
  background: #e9ecef;
}

.accordion-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.accordion-icon {
  font-size: 12px;
  color: #666;
}

.accordion-content {
  padding: 16px;
  background: #fff;
  border: 1px solid #eee;
  border-top: none;
  border-radius: 0 0 6px 6px;
}

/* Анимация аккордеона */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0 16px;
}

/* Форма бронирования */
.booking-form {

}

.booking-form input{
  max-width: 200px;
}

.readonly-input {
  background: #f5f5f5;
  border: 1px solid #ddd;
  color: #666;
}

.form-actions {

  margin-top: 10px;
}

.save-btn {
  background: #4CAF50;
  color: white;
}

.cancel-btn {
  margin-right: 20px;
  background: #f44336;
  color: white;
  transition: all 0.2s;
}

.cancel-btn:hover {
    background: #3a100d;
}

@media (max-width: 768px) {
  .booking-form {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    grid-column: span 1;
  }
}

.active-booking {
  background-color: #f8f9fa !important; 
  margin-bottom: 20px;
  border-radius: 6px;
}

/* Для плавной анимации выделения */
.booking-header {
  transition: all 0.3s ease;
}

.booking-details{
  padding: 20px 20px ;

}

</style>