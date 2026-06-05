<template>
  <section class="room_detail">
    <div v-if="roomLoading" class="room_detail_container room-detail-skeleton" aria-busy="true" aria-live="polite">
      <div class="flex-titel">
        <span class="skeleton-line skeleton-title"></span>
        <span class="skeleton-button"></span>
      </div>

      <div class="room_img_container room_img_container--skeleton">
        <div class="room_img main_img skeleton-block"></div>
        <div v-for="item in 4" :key="'gallery-skeleton-' + item" class="room_img skeleton-block"></div>
      </div>

      <div class="room_detail_wrapper">
        <div class="room_detail_wrapper_left">
          <div class="room_detail_about">
            <span class="skeleton-line skeleton-heading"></span>
            <div class="info_about_room">
              <span v-for="item in 4" :key="'info-skeleton-' + item" class="info_about_room_cont skeleton-pill"></span>
            </div>
            <div class="about-skeleton">
              <span class="skeleton-line"></span>
              <span class="skeleton-line"></span>
              <span class="skeleton-line skeleton-line--short"></span>
            </div>
          </div>

          <span class="skeleton-line skeleton-heading-small"></span>
          <div class="room_detail_bed_info">
            <div v-for="item in 2" :key="'bed-skeleton-' + item" class="bed bed--skeleton">
              <span class="skeleton-icon"></span>
              <span class="skeleton-line skeleton-line--tiny"></span>
            </div>
          </div>

          <div class="room_detail_facilities">
            <span class="skeleton-line skeleton-heading-small"></span>
            <div class="facilities_grap">
              <div v-for="item in 6" :key="'facility-skeleton-' + item" class="facilities_block facilities_block--skeleton">
                <span class="skeleton-icon"></span>
                <span class="skeleton-line skeleton-line--tiny"></span>
              </div>
            </div>
          </div>

          <div class="rules-card rules-card--skeleton">
            <span class="skeleton-line skeleton-heading-small"></span>
            <span class="skeleton-line skeleton-line--mid"></span>
            <span class="skeleton-line"></span>
            <span class="skeleton-line skeleton-line--short"></span>
          </div>
        </div>

        <div class="room_detail_wrapper_right">
          <div class="booking-form-skeleton">
            <span class="skeleton-line skeleton-heading-small"></span>
            <span class="skeleton-block skeleton-input"></span>
            <span class="skeleton-block skeleton-input"></span>
            <span class="skeleton-block skeleton-input skeleton-input--button"></span>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="room" class="room_detail_container">
      <div class="flex-titel">
        <h1 class="room_detail_h1">{{ room.title }}</h1>
        <div class="lincto" @click="copyBookingLink">
          <img class="lincto_svg" src="@/assets/icons/upload.svg" alt="Назад">
        </div>
      </div>  

      
      <div class="room_img_container">
        <!-- Кнопка назад для мобильной версии -->
        <button v-if="isMobile" class="back-button-mobile" @click="goBack">
          <img class="activiti_svg" src="@/assets/icons/back-svgrepo-com.svg" alt="Назад">
        </button>
        
        <div  
          v-for="(photo, index) in sortedRoomPhotos.slice(0, 5)"
          :key="photo.url"
          :class="['room_img', { main_img: photo.is_main }]"
          @click="openModal(index)" 
        >
          <img :src="getPhotoUrl(photo.url)" :alt="room.title" loading="lazy" decoding="async" />
        </div>
      </div>
      <div class="room_detail_wrapper">
        <div class="room_detail_wrapper_left">
          <div class="room_detail_about">
            <div class="room_detail_full_name">
              <h2>{{ room.title_dop }}</h2>
            </div>
            <div class="info_about_room">
              <div class="info_about_room_cont" v-if="room.area">{{ room.area }} м²</div>
              <div class="info_about_room_cont">{{ room.max_guests }} гостя</div>
              <div class="info_about_room_cont">{{ room.floor }} этаж</div>
              <div class="info_about_room_cont">{{ room.bed_options.length  }} кровати</div>
            </div>
            <div class="about">{{ room.description }}</div>
          </div>

          <h3>Где вы будете спать</h3>

          <div class="room_detail_bed_info">
            <div class="bed" v-for="bed in room.bed_options" :key="bed.id">
              <img
                class="room_bed_img"
                :src="getIconUrl(bed.icon)"
                alt=""
              />

              <div class="room_bed_were">{{ bed.name }}</div>
            </div>
          </div>
          <div class="room_detail_facilities">
            <h3 class="facilities_h3">Удобства</h3>
            <div
              class="facilities_grap"
            >
              <div class="facilities_block" v-for="amenity in visibleAmenities"
              :key="amenity.id">
                <img
                  :src="getIconUrl(amenity.icon)"
                  alt=""
                />
                <div class="facilities_name">{{ amenity.name }}</div>
              </div>
            </div>
            <button v-if="visibleAmenities.length >= defaultVisibleAmenities " class="facilities_btn" @click="toggleFacilities">
              {{ showAllFacilities ? 'Скрыть' : 'Все удобства' }}
            </button>
          </div>

          <div class="rules-card">
            <h3 class="rules-title">Правила проживания</h3>

            <div class="rules-checkin info_about_room_cont">
              <span>Заезд с <strong>14:00</strong></span>
              <span>—</span>
              <span>Выезд до <strong>12:00</strong></span>
            </div>

            <ul class="rules-list">
              <li>
                <span class="rule-icon">🚭</span>
                <span>Курение разрешено в специально отведённых местах</span>
              </li>
              <li>
                <span class="rule-icon">🐾</span>
                <span>Можно с питомцами по согласованию </span>
              </li>
              <li>
                <span class="rule-icon">🎉</span>
                <span>Без вечеринок и мероприятий</span>
              </li>
              <li>
                <span class="rule-icon">👨‍👩‍👧</span>
                <span>Можно с детьми</span>
              </li>
            </ul>

            <div class="rules-section">
              <h3>Способ оплаты</h3>
              <p>Наличные</p>
              <p>Перевод</p>
            </div>

            <div class="rules-section">
              <h3>Условия отмены</h3>
              <p>Вы можете бесплатно отменить бронирование, если сообщите нам об этом не позднее чем за 2 недели до заезда.</p>
            </div>
          </div>

          <div class="room_detail_datapiker">
            <h3>Календарь</h3>
            <div class="room-calendar">
              <DateRangePicker
                :start-date="startDate"
                :end-date="endDate"
                v-model:error="searchError"
                :occupied-dates="occupiedDates"
                :number-of-rooms="room.number_of_rooms"
                :price-periods="room.price_periods"
                @update:startDate="handleRoomCalendarStartDateUpdate"
                @update:endDate="handleRoomCalendarEndDateUpdate"
                @clear="handleClear"
                :no-margin="true"
                :single-month="isMobile"
              />
            </div>
          </div>
          <div class="accordion-container">
            <h3>Часто задаваемые вопросы</h3>
            <div
              v-for="(item, index) in accordionItems"
              :key="index"
              class="accordion-item"
              :class="{ active: item.isOpen }"
            >
              <div class="accordion-header" @click="toggleAccordion(index)">
                <h3>{{ item.title }}</h3>
                <svg class="accordion-icon" viewBox="0 0 24 24">
                  <path
                    d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"
                  />
                </svg>
              </div>
              <div class="accordion-content">
                <div v-html="item.content"></div>
              </div>
            </div>
          </div>

          
        </div>
        <div ref="bookingFormAnchor" class="room_detail_wrapper_right">
          <BookingForm
            :start-date="startDate"
            :end-date="endDate"
            :guests-count="guestsCount" 
            @update:guestsCount="guestsCount = $event" 
            :price-periods="room.price_periods"
            :bookings="booking"
            :number-of-rooms="room.number_of_rooms"
            :max-guests="room.max_guests"
            :room-id="roomId"
            @update:startDate="startDate = $event"
            @update:endDate="endDate = $event"
            @booking-change="handleBookingChange"
            @booking-submit="handleBookingSubmit"
          />
        </div>
      </div>
    </div>

    <div v-else-if="roomLoadError" class="room-detail-error">
      <h2>Не удалось загрузить номер</h2>
      <p>Проверьте подключение или попробуйте открыть страницу ещё раз.</p>
      <button type="button" @click="fetchRoomDetail">Повторить</button>
    </div>
      <div v-if="showCopiedNotification" class="copied-notification">
    Ссылка скопирована!
  </div>

    <!-- Telegram booking confirmation modal -->
    <TelegramBookingModal
      v-if="telegramModalOpen"
      v-model="telegramModalOpen"
      :booking-data="telegramBookingData"
    />

    <!-- Photo carousel modal -->
    <PhotoModal
      v-model="isModalOpen"
      :photos="fullPhotos"
      :initialIndex="currentPhotoIndex"
      :roomTitle="room?.title || ''"
    />
  </section>
</template>

<script>
import api, { API_BASE_URL } from '@/api';
import DateRangePicker from './DateRangePicker.vue';
import BookingForm from './BookingForm.vue';
import PhotoModal from './PhotoModal.vue';
import TelegramBookingModal from './TelegramBookingModal.vue';
import { absoluteMediaUrl, getRoomPath, setPageMeta } from '@/utils/seo';

export default {
  components: {
    DateRangePicker,
    BookingForm,
    PhotoModal,
    TelegramBookingModal,
  },

  data() {
    return {
      isModalOpen: false,
      currentPhotoIndex: 0,
      room: null,
      roomLoading: true,
      roomLoadError: false,
      startDate: null,
      endDate: null,
      guestsCount: 1,
      searchError: null,
      buttonText: 'Поделиться',
      showCopiedNotification: false,
      booking:[],
      occupiedDates: {},
      showAllFacilities: false,
      defaultVisibleAmenities: 6,
      initialLoad: true,
      roomCalendarAwaitingEndDate: false,
      isMobile: false, // Добавляем свойство для определения мобильного устройства
      accordionItems: [],
      telegramModalOpen: false,
      telegramBookingData: {
        checkin: null,
        checkout: null,
        guests: 1,
        price: 0,
        prepay: 0,
        roomId: null,
      },
    };
  },
  watch: {
    startDate() {
      if (!this.initialLoad) this.updateUrlQuery();
    },
    endDate() {
      if (!this.initialLoad) this.updateUrlQuery();
    },
    guestsCount() {
      if (!this.initialLoad) this.updateUrlQuery();
    },
    $route() {
      if (this.room) this.setParamsFromUrl();
    }
  },
  computed: {
    fullPhotos() {
      if (!this.room) return [];
      return this.sortedRoomPhotos.map(photo => ({
        ...photo,
        fullUrl: this.getPhotoUrl(photo.url)
      }));
    },
    sortedRoomPhotos() {
      return [...(this.room?.photos || [])].sort((a, b) => {
        const orderDiff = (a.sort_order || 0) - (b.sort_order || 0);
        return orderDiff || a.id - b.id;
      });
    },
    visibleAmenities() {
      if (!this.room) return [];
      return this.showAllFacilities 
        ? this.room.amenities 
        : this.room.amenities.slice(0, this.defaultVisibleAmenities);
    },
    roomId() {
      return this.extractRoomId();
    },
  },

  created() {
    this.fetchRoomDetail();
    this.loadBookings();
    this.fetchFAQ();
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeydown);
    this.checkMobile(); // Проверяем размер экрана при монтировании
    window.addEventListener('resize', this.checkMobile); // Следим за изменением размера
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeydown);
    window.removeEventListener('resize', this.checkMobile);
    document.body.style.overflow = '';
  },

  methods: {
    // Метод для определения мобильного устройства
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
    },

    extractRoomId() {
      if (this.$route.params.id) return this.$route.params.id;
      const slug = this.$route.params.roomSlug || '';
      const match = String(slug).match(/^(\d+)/);
      return match ? match[1] : null;
    },

    updateRoomMeta() {
      if (!this.room) return;
      const mainPhoto = this.sortedRoomPhotos.find(photo => photo.is_main) || this.sortedRoomPhotos[0];
      const description = this.room.description
        ? this.room.description.replace(/\s+/g, ' ').slice(0, 160)
        : `${this.room.title}: номер для отдыха в гостевом доме Виноградная Лоза в Крыму.`;

      setPageMeta({
        title: `${this.room.title} - ${this.room.max_guests} гостей | Виноградная Лоза`,
        description,
        image: absoluteMediaUrl(mainPhoto?.url),
        url: `${window.location.origin}${getRoomPath(this.room)}`,
        type: 'product'
      });
    },
    
    // Метод для возврата на предыдущую страницу
    goBack() {
      this.$router.back(); // или this.$router.go(-1)
    },
    
    openModal(index) {
      this.currentPhotoIndex = index;
      this.isModalOpen = true;
    },

    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    async copyBookingLink() {
      try {
        const bookingUrl = this.generateBookingUrl();
        
        // Копируем ВСЕГДА, даже если параметров нет
        await navigator.clipboard.writeText(bookingUrl);
        
        this.showCopiedNotification = true;
        this.buttonText = 'Скопировано!';
        
        setTimeout(() => {
          this.showCopiedNotification = false;
          this.buttonText = 'Поделиться';
        }, 2000);
      } catch (err) {
        console.error('Ошибка копирования:', err);
        alert('Не удалось скопировать ссылку. Пожалуйста, скопируйте вручную.');
      }
    },

    updateUrlQuery() {
      const query = { ...this.$route.query };
      
      if (this.startDate) {
        query.start = this.formatDate(this.startDate);
      } else {
        delete query.start;
      }
      
      if (this.endDate) {
        query.end = this.formatDate(this.endDate);
      } else {
        delete query.end;
      }
      
      if (this.guestsCount > 1) {
        query.guests = this.guestsCount;
      } else {
        delete query.guests;
      }
      
      this.$router.replace({ 
        path: this.$route.path, 
        query 
      }).catch(() => {});
    },

    setParamsFromUrl() {
      const query = this.$route.query;
      
      if (query.start) {
        const [year, month, day] = query.start.split('-').map(Number);
        const startDate = new Date(year, month - 1, day);
        if (!isNaN(startDate.getTime())) {
          this.startDate = startDate;
        }
      }
      
      if (query.end) {
        const [year, month, day] = query.end.split('-').map(Number);
        const endDate = new Date(year, month - 1, day);
        if (!isNaN(endDate.getTime())) {
          this.endDate = endDate;
        }
      }
      
      if (query.guests) {
        const guests = parseInt(query.guests);
        if (!isNaN(guests) && guests > 0) {
          this.guestsCount = guests;
        }
      }
    },
    
    generateBookingUrl() {
      const params = new URLSearchParams();
      
      // Добавляем параметры только если они есть
      if (this.startDate) {
        params.append('start', this.formatDate(this.startDate));
      }
      
      if (this.endDate) {
        params.append('end', this.formatDate(this.endDate));
      }
      
      // Всегда добавляем количество гостей (даже если 1)
      params.append('guests', this.guestsCount);
      
      const queryString = params.toString();
      return queryString 
        ? `${window.location.origin}${window.location.pathname}?${queryString}`
        : `${window.location.origin}${window.location.pathname}`;
    },

    async fetchRoomDetail() {
      const roomId = this.extractRoomId();
      this.roomLoading = true;
      this.roomLoadError = false;
      try {
        const response = await api.get(`/rooms/${roomId}/`);
        this.room = response.data;
        this.updateRoomMeta();

      } catch (error) {
        console.error('Ошибка при загрузке данных о комнате:', error);
        this.room = null;
        this.roomLoadError = true;
      } finally {
        this.roomLoading = false;
      }
    },
    async fetchFAQ() {
  try {
    const response = await api.get('/site/faqs/');
    // Преобразуем поля API в формат аккордеона
    this.accordionItems = response.data.map(item => ({
      title: item.question,
      content: item.answer,
      isOpen: false
    }));
  } catch (error) {
    console.error('Ошибка при загрузке FAQ:', error);
  }
},

    async loadBookings() {
      try {
        const resolvedRoomId = this.extractRoomId();
        const response = await api.get(`/bookings/rooms/${resolvedRoomId}`);
        
        // Обеспечиваем реактивность
        this.booking = response.data
        this.calculateOccupiedDates(response.data);
        this.setParamsFromUrl();
        this.initialLoad = false;
        
        
      } catch (error) {
        console.error(error, 'Ошибка загрузки бронирований');
      }
    },

    handleRoomCalendarStartDateUpdate(newDate) {
      this.roomCalendarAwaitingEndDate = Boolean(newDate);
      this.startDate = newDate;
    },

    handleRoomCalendarEndDateUpdate(newDate) {
      this.endDate = newDate;
      if (this.roomCalendarAwaitingEndDate && this.isCompleteDateRange(newDate)) {
        this.roomCalendarAwaitingEndDate = false;
        this.scrollToBookingForm();
      }
    },

    isCompleteDateRange(endDate = this.endDate) {
      return Boolean(
        !this.initialLoad &&
        this.isMobile &&
        this.startDate &&
        endDate &&
        endDate > this.startDate
      );
    },

    scrollToBookingForm() {
      this.$nextTick(() => {
        this.$refs.bookingFormAnchor?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    },

    toggleAccordion(index) {
      // Закрываем все элементы
      this.accordionItems.forEach((item, i) => {
        if (i !== index) {
          item.isOpen = false;
        }
      });
      
      // Переключаем текущий элемент
      this.accordionItems[index].isOpen = !this.accordionItems[index].isOpen;
    },

    calculateOccupiedDates(ocupasiti) {
      const occupied = {};
      ocupasiti.forEach(booking => {
        const start = new Date(booking.check_in_date);
        const end = new Date(booking.check_out_date);
        let current = new Date(start);

        while (current < end) {
          const dateStr = this.formatDate(current)
          occupied[dateStr] = (occupied[dateStr] || 0) + 1;
          current.setDate(current.getDate() + 1);
        }
      });
      this.occupiedDates = occupied;
    },

    getIconUrl(icon) {
      return `${API_BASE_URL}/${icon}`;
    },

    getPhotoUrl(url) {
      return `${API_BASE_URL}${url}`;
    },

    handleBookingChange(payload) {
      this.startDate = payload.startDate;
      this.endDate = payload.endDate;
      this.guestsCount = payload.guestsCount;
      this.$emit('booking-data', {
        startDate: this.startDate,
        endDate: this.endDate,
        guestsCount: this.guestsCount
      });
    },

    /**
     * Открывает модалку подтверждения бронирования с передачей данных в Telegram.
     * Не ломает существующую логику — просто показывает окно поверх страницы.
     */
    handleBookingSubmit(payload) {
      this.telegramBookingData = {
        checkin: payload.startDate,
        checkout: payload.endDate,
        guests: payload.guests,
        price: payload.totalPrice,
        prepay: payload.prepayment,
        roomId: this.roomId,
      };
      this.telegramModalOpen = true;
    },

    handleClear() {
      this.startDate = null;
      this.endDate = null;
      this.guestsCount = 1;
      this.searchError = null;
      this.roomCalendarAwaitingEndDate = false;
    },
    
    toggleFacilities() {
      this.showAllFacilities = !this.showAllFacilities;
    }
  }
};
</script>

<style scoped>

/* Типографика заголовков на странице детального описания номера */
.room_detail h1,
.room_detail_h1 { font-size: 32px; line-height: 1.2; font-weight: 700; }
.room_detail h2 { font-size: 24px; line-height: 1.3; font-weight: 600; }
.room_detail h3 { font-size: 20px; line-height: 1.35; font-weight: 600; }

.room_detail_facilities{
  padding: 0  0 25px;
  padding-top: 25px;
  border-bottom: 1px solid #dddddd;
  border-top: 1px solid #dddddd;

}

.room-calendar {
  max-width: 700px;
  margin: 20px 0;
}

.room_detail_about {
  border-bottom: 1px solid #dddddd;
  padding-bottom: 25px;
  margin-bottom: 25PX;
}

.about {
  font-size: 20px;
  line-height: 1.5;
}

.room-calendar .end-date {
  z-index: 0;
}

.flex {
  display: flex;
  justify-content: space-between;
}

.img {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 20px 0;
}

.main_img {
  grid-column: 1;
  grid-row: 1 / span 2;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  margin: 5px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
}

/* Стили для блока кроватей */
.room_detail_bed_info {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
  margin: 20px 0 30px;
}

.bed {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 15px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
  transition: all 0.3s ease;
}



.room_bed_were {
  text-align: center;
 
}

.room_bed_img {
  width: 30px;
  height: 30px;
  margin-bottom: 12px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

/* Стили для блока удобств */
.facilities_grap {
   grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  display:grid;
  gap: 20px;
  margin: 20px 0;
}

.facilities_block {
    border-radius: 12px;

    gap: 15px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
  display: flex;
  padding: 15px 0;
  align-items: center;
  justify-content: center;
}

.facilities_block img {
  width: 30px;
  height: 30px;
  transition: transform 0.3s ease;
}

.facilities_block:hover img {
  transform: scale(1.1);
}

.facilities_name {
  font-size: 14px;
  text-align: center;
  line-height: 1.4;
}

.facilities_btn {
  margin-top: 10px;
  padding: 12px 24px;
  background: white;
  border: 1px solid #222;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.facilities_btn:hover {
  background: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Анимация для появления/скрытия удобств */
.facilities-enter-active,
.facilities-leave-active {
  transition: all 0.5s ease;
  max-height: 500px;
  overflow: hidden;
}

.facilities-enter-from,
.facilities-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}

.date-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

label {
  font-size: 0.9em;
  margin-bottom: 5px;
  color: #666;
}
.lincto{
  border-radius: 8px;
  align-items: center;
  padding: 10px 15px;
  gap: 8px;
  display: flex;
  cursor: pointer;
  background-color: #f0eeee9a;
  transition: 0.2s all ease-in-out;
}

.lincto:hover{
    background-color: #d3d2d2;
}
@keyframes fadeInOut {
  0% { opacity: 0; bottom: 0; }
  20% { opacity: 1; bottom: 20px; }
  80% { opacity: 1; bottom: 20px; }
  100% { opacity: 0; bottom: 0; }
}

.copied-notification {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px 20px;
  border-radius: 4px;
  z-index: 1000;
  animation: fadeInOut 3s ease;
}

.flex-titel{
  display: flex;
  align-items: center;
  justify-content: space-between;

}

input[type="date"] {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.room_detail {
  max-width: 1120px;
  margin: 0 auto;

}

.lincto_svg{
  width: 20px;
}

.room_img_container {
  border-radius: 16px;
  overflow: hidden;
  display: grid;
  grid-template-columns: 50% 25% 25%;
  grid-template-rows: 50% 50%;
  gap: 6px;
  width: 100%;
  aspect-ratio: 3/1.5;
  max-height: 54vh;
  margin: 0 auto;
  overflow: hidden;
}

.room_img {
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
  cursor: pointer;
}

.room_img::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.room_img:hover::after {
  opacity: 1;
}

.room_img:hover img {
  transform: scale(1.05);
}

.room_img img {
  transition: transform 0.3s ease;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.room_img_container.asymmetric {
  border-radius: 50px 20px;
}

.room_img_container.sides-only {
  border-radius: 0 15px 15px 0;
}

.room_detail_container{
   padding: 10px; 
  }

/* Кнопка "Назад" для мобильной версии */
.back-button-mobile {
  position: absolute;
  background: none;
  top: 20px;
  padding: 4px 8px;
  left: 20px;
  border-radius: 16px;
  z-index: 10;
  background-color: #ffffffea;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.back-button-mobile:hover {
  transform: translateX(-2px);
}

.back-button-mobile svg {
  width: 18px;
  height: 18px;
}
.room_detail_wrapper {
  margin-top: 30px;
  display: grid;
  grid-template-columns: 58% 10% 32%;
}

@media (max-width: 768px) {
  .room_detail_wrapper_left{
    order: 2
  }
  .room_detail_wrapper_right{
    order: 1;
    background: var(--color-gray-50);
    padding: 16px 0;
    border-radius: var(--radius-lg);
    margin-bottom: var(--spacing-md);
  }

  .room_detail_container {
    padding: 0;
    position: relative;
  }

  .flex-titel {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    z-index: 3;
    padding: 0;
    margin: 0;
    background: none;
  }

  .flex-titel .room_detail_h1 {
    display: none;
  }

  .flex-titel .lincto {
    background: rgba(255, 255, 255, 0.9);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    padding: 8px;
    border-radius: 50%;
  }

  .flex-titel .lincto:hover {
    background: #fff;
  }

  .room_img_container {
    position: relative;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    display: block;
    height: 45vh;
    width: 100%;
    aspect-ratio: auto;
    overflow: hidden;
  }

  /* Показываем только первое фото */
  .room_img_container .room_img {
    display: none;
  }

  .room_img_container .room_img:first-of-type {
    display: block;
    width: 100%;
    height: 100%;
  }

  .room_img_container .room_img:first-of-type img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .room_detail_wrapper {
    padding: var(--spacing-md);
    margin-top: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .room_detail_h1 {
    font-size: var(--text-xl);
  }

  .room_detail_bed_info {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
  }

  .facilities_grap {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
  }

  .back-button-mobile {
    top: var(--spacing-md);
    left: var(--spacing-md);
    padding: var(--spacing-xs) var(--spacing-sm);
  }
}

@media (max-width: 480px) {
  .room_img_container {
    height: 35vh;
  }

  .room_detail_wrapper {
    padding: 0 20px ;
  }

  .about {
    font-size: var(--text-base);
  }

  .bed {
    padding: var(--spacing-md);
  }

  .facilities_block {
    padding: var(--spacing-sm) 6px;
    justify-content:flex-start;
  }
}




.activiti_svg{
  width: 20px;
  height: 20px;
}

.room_detail_wrapper_right {
  width: 100%;
  grid-column: 3;
  box-sizing: border-box;
}

.accordion-container {
  margin-bottom: 50px;
  padding: 25px 0;
  border-top: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
}

.accordion-item {
  border-bottom: 1px solid #eee;
}

.accordion-item:last-child {
  border-bottom: none;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  cursor: pointer;
}

.accordion-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.accordion-icon {
  width: 24px;
  height: 24px;
  transition: transform 0.3s ease;
}

.accordion-item.active .accordion-icon {
  transform: rotate(180deg);
}

.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;
}

.accordion-item.active .accordion-content {
  max-height: 500px;
  padding-bottom: 15px;
}

.accordion-list {
  padding-left: 20px;
  margin: 0;
}

.accordion-list li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #555;
}

.accordion-list li:last-child {
  margin-bottom: 0;
}

.accordion-list strong {
  color: #000;
  font-weight: 500;
}

.zoom-fade-enter-active,
.zoom-fade-leave-active {
  transition: opacity 0.3s ease;
}

.zoom-fade-enter-active .image-container,
.zoom-fade-leave-active .image-container {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

.zoom-fade-enter-from,
.zoom-fade-leave-to {
  opacity: 0;
}

.zoom-fade-enter-from .image-container {
  transform: translate(-50%, -50%) scale(0.1);
  opacity: 0;
}

.zoom-fade-enter-to .image-container {
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
}

.zoom-fade-leave-to .image-container {
  transform: translate(-50%, -50%) scale(0.1);
  opacity: 0;
}

/* Стили модального окна */

.info_about_room{
  
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 20px;
}
.info_about_room_cont{
  padding: 10px 16px ;
  font-size: 12px;
  background-color: #f7f7f7;
  border-radius: 18px;
  border: 1px solid #ebebeb;
}

.rules-card {
   border-bottom: 1px solid #dddddd;

  padding: 20px 0;
  background: #ffffff;
  color: #222;
}
li{
  background: none;
}

.rules-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 12px;
}

.rules-checkin {
  display: flex;
  gap: 6px;
  max-width: 200px;
  font-size: 14px;
  color: #555;
  margin-bottom: 16px;
}

.rules-checkin strong {
  font-weight: 600;
}

.rules-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px;
}

.rules-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 16px;
  color: #333;
  padding: 6px 0;
}

.rule-icon {
  width: 22px;
  flex-shrink: 0;
  text-align: center;
  font-size: 16px;
}

.rules-section {
  padding-top: 16px;
  margin-top: 8px;
}

.rules-section h3 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px;
}

.rules-section p {
  font-size: 14px;
  margin: 0;
  color: #444;
}
.room_detail_datapiker h3{
  margin: 16px 0;
}

/* Loading state */
.room-detail-skeleton {
  pointer-events: none;
}

.skeleton-block,
.skeleton-line,
.skeleton-button,
.skeleton-pill,
.skeleton-icon {
  position: relative;
  overflow: hidden;
  background: linear-gradient(90deg, #ececf4 0%, #f8f7ff 46%, #ececf4 100%);
  background-size: 220% 100%;
  animation: room-detail-shimmer 1.35s ease-in-out infinite;
}

.skeleton-line {
  display: block;
  width: 100%;
  height: 14px;
  border-radius: 999px;
}

.skeleton-line + .skeleton-line {
  margin-top: 12px;
}

.skeleton-title {
  width: min(420px, 62vw);
  height: 34px;
  margin: 16px 0;
}

.skeleton-heading {
  width: min(340px, 75%);
  height: 26px;
  margin-bottom: 20px;
}

.skeleton-heading-small {
  width: min(260px, 66%);
  height: 22px;
  margin: 18px 0;
}

.skeleton-line--mid {
  width: 72%;
}

.skeleton-line--short {
  width: 48%;
}

.skeleton-line--tiny {
  width: 88px;
}

.skeleton-button {
  width: 50px;
  height: 42px;
  border-radius: 8px;
}

.room_img_container--skeleton .room_img {
  cursor: default;
}

.room_img_container--skeleton .room_img::after {
  display: none;
}

.skeleton-pill {
  width: 88px;
  height: 38px;
  border-color: transparent;
}

.about-skeleton {
  max-width: 640px;
}

.bed--skeleton,
.facilities_block--skeleton {
  cursor: default;
}

.skeleton-icon {
  display: block;
  width: 30px;
  height: 30px;
  flex: 0 0 30px;
  border-radius: 10px;
}

.rules-card--skeleton {
  display: grid;
  gap: 12px;
}

.booking-form-skeleton {
  position: sticky;
  top: 96px;
  display: grid;
  gap: 16px;
  padding: 22px;
  border: 1px solid rgba(198, 196, 253, 0.55);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 18px 42px rgba(24, 24, 27, 0.08);
}

.skeleton-input {
  height: 58px;
  border-radius: 14px;
}

.skeleton-input--button {
  height: 48px;
  border-radius: 999px;
}

.room-detail-error {
  max-width: 620px;
  margin: 80px auto;
  padding: 32px;
  text-align: center;
  border: 1px solid rgba(198, 196, 253, 0.55);
  border-radius: 18px;
  background: linear-gradient(135deg, #fff, #f8f7ff);
}

.room-detail-error h2 {
  margin: 0 0 8px;
}

.room-detail-error p {
  margin: 0 0 20px;
  color: var(--color-gray-600);
}

.room-detail-error button {
  padding: 12px 18px;
  border: 0;
  border-radius: 999px;
  color: #fff;
  background: #5651d8;
  font-weight: 800;
  cursor: pointer;
}

@keyframes room-detail-shimmer {
  0% { background-position: 120% 0; }
  100% { background-position: -120% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-block,
  .skeleton-line,
  .skeleton-button,
  .skeleton-pill,
  .skeleton-icon {
    animation: none;
  }
}

@media (max-width: 768px) {
  .room-detail-skeleton .flex-titel {
    display: none;
  }

  .booking-form-skeleton {
    position: static;
    margin: 0 16px;
  }
}

</style>
