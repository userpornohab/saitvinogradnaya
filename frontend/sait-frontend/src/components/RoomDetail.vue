<template>
  <section class="room_detail">
    <div v-if="room" class="room_detail_container">
      <div class="flex-titel">
        <h1 class="room_detail_h1">{{ room.title }}</h1>
        <div class="lincto" @click="copyBookingLink">
          <img class="lincto_svg" src="@/assets/icons/upload.svg" alt="Назад">
          <div>Поделиться</div>
        </div>
      </div>  

      
      <div class="room_img_container">
      <div
        v-for="(photo, index) in room.photos.slice(0, 5)"
        :key="photo.url"
        :class="['room_img', { main_img: photo.is_main }]"
        @click="openModal(index)" 
      >
        <img :src="getPhotoUrl(photo.url)" :alt="room.title" />
      </div>
    </div>
    <PhotoModal
      v-model="isModalOpen"
      :photos="fullPhotos"
      :initialIndex="currentPhotoIndex"
      :roomTitle="room?.title || ''"
    />
      <div class="room_detail_wrapper">
        <div class="room_detail_wrapper_left">
          <div class="room_detail_about">
            <div class="room_detail_full_name">
              <h2>{{ room.title_dop }}</h2>
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
              <div class="room_bed_were">Комната</div>
              <div>{{ bed.name }}</div>
            </div>
          </div>
          <div class="room_detail_facilities">
            <h3 class="facilities_h3">Основные удобства</h3>
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
              {{ showAllFacilities ? 'Скрыть' : 'Показать все удобства' }}
            </button>
          </div>
          <div class="room_detail_datapiker">
            <h3>Календарь</h3>
            <div class="room-calendar">
              <DateRangePicker
                v-model:startDate="startDate"
                v-model:endDate="endDate"
                v-model:error="searchError"
                :occupied-dates="occupiedDates"
                :number-of-rooms="room.number_of_rooms"
                :price-periods="room.price_periods"
                @clear="handleClear"
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
        <div class="room_detail_wrapper_right">
          <BookingForm
            :start-date="startDate"
            :end-date="endDate"
            :guests-count="guestsCount" 
            @update:guestsCount="guestsCount = $event" 
            :price-periods="room.price_periods"
            :bookings="booking"
            :number-of-rooms="room.number_of_rooms"
            :max-guests="room.max_guests"
            @update:startDate="startDate = $event"
            @update:endDate="endDate = $event"
            @booking-change="handleBookingChange"

          />
        </div>
      </div>
    </div>

    <div v-else>
      <p>Загрузка данных о комнате...</p>
    </div>
      <div v-if="showCopiedNotification" class="copied-notification">
    Ссылка скопирована!
  </div>
  </section>
</template>

<script>
import axios from 'axios';
import DateRangePicker from './DateRangePicker.vue';
import BookingForm from './BookingForm.vue';
import PhotoModal from './PhotoModal.vue';

export default {
  components: {
    DateRangePicker,
    BookingForm,
    PhotoModal 
  },

  data() {
    return {
      isModalOpen: false,
      currentPhotoIndex: 0,
      room: null,
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
      accordionItems: [
        {
          title: "Условия бронирования",
          content: `
            <ul class="accordion-list">
              <li>При бронировании необходимо внести предоплату в размере стоимости номера за сутки проживания</li>
              <li>Вы можете бесплатно отменить бронирование за семь суток до заезда</li>
              <li>Время выезда: до 12:00</li>
              <li>Время заезда: после 14:00</li>
              <li>Минимальный срок проживания: 3 ночи</li>
            </ul>
          `,
          isOpen: false
        },
        {
          title: "Правила проживания",
          content: `
            <ul class="accordion-list">
              <li>С домашними животными не принимаем</li>
              <li>В номерах не курить</li>
              <li>После 23:00 часов соблюдаем тишину и относимся с уважением к отдыху других</li>
              <li>Шумные компании на берегу моря могут отдыхать и шуметь до утра</li>
            </ul>
          `,
          isOpen: false
        },
        {
          title: "Условия проживания",
          content: `
            <ul class="accordion-list">
              <li>Горячая вода постоянно</li>
              <li>Оплата наличными и по переводу на карту</li>
            </ul>
          `,
          isOpen: false
        },
        {
          title: "Трансфер",
          content: `
            <ul class="accordion-list">
              <li>Трансфер от и до ж/д вокзала (за дополнительную плату)</li>
              <li>Трансфер из и в аэропорта (за дополнительную плату)</li>
            </ul>
          `,
          isOpen: false
        },
        {
          title: "Сервис",
          content: `
            <ul class="accordion-list">
              <li><strong>Бесплатный:</strong> Смена постельного белья, парковка</li>
              <li><strong>За дополнительную плату:</strong> Услуги экскурсовода, пользование стиральной машиной</li>
            </ul>
          `,
          isOpen: false
        },
        {
          title: "Скидки и акции",
          content: `
            <ul class="accordion-list">
              <li>Заказ от 30 дней и больше скидка 10%</li>
              <li>Отдых для детей до трёх лет (бесплатно)</li>
            </ul>
          `,
          isOpen: false
        }
      ]
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
        return this.room.photos.map(photo => ({
          ...photo,
          fullUrl: this.getPhotoUrl(photo.url)
        }));
      },
    visibleAmenities() {
      return this.showAllFacilities 
        ? this.room.amenities 
        : this.room.amenities.slice(0, this.defaultVisibleAmenities);
    },
    roomId() {
    return this.$route.params.id;
  },
  },

  created() {
    this.fetchRoomDetail();
    this.loadBookings();
  },
  mounted() {
  window.addEventListener('keydown', this.handleKeydown);
},
beforeUnmount() {
  window.removeEventListener('keydown', this.handleKeydown);
  document.body.style.overflow = '';
},

  methods: {
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
      const roomId = this.$route.params.id;
      try {
        const response = await axios.get(`http://127.0.0.1:8000/rooms/${roomId}/`);
        this.room = response.data;

      } catch (error) {
        console.error('Ошибка при загрузке данных о комнате:', error);
      }
    },

    async loadBookings() {
  try {
    const roomId = this.$route.params.id;
    const response = await axios.get(`http://localhost:8000/bookings/rooms/${roomId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    
    // Обеспечиваем реактивность
    this.booking = response.data
    this.calculateOccupiedDates(response.data);
    this.setParamsFromUrl();
    this.initialLoad = false;
    
    
  } catch (error) {
    console.error(error, 'Ошибка загрузки бронирований');
  }
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
          end.setDate(end.getDate() - 1);

        while (current < end) {
          const dateStr = this.formatDate(current)
          occupied[dateStr] = (occupied[dateStr] || 0) + 1;
          current.setDate(current.getDate() + 1);
        }
      });
      this.occupiedDates = occupied;
    },

    getIconUrl(icon) {
      return `http://127.0.0.1:8000/${icon}`;
    },

    getPhotoUrl(url) {
      return `http://127.0.0.1:8000${url}`;
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

    handleClear() {
      this.startDate = null;
      this.endDate = null;
      this.guestsCount = 1;
      this.searchError = null;
    },
    
    toggleFacilities() {
      this.showAllFacilities = !this.showAllFacilities;
    }
  }
};
</script>

<style scoped>

.room_detail_facilities{
  padding: 0  0 50px;
    border-bottom: 1px solid #dddddd;
    border-top: 1px solid #dddddd;

}

.room-calendar {
  max-width: 700px;
  margin: 20px 0;
}

.room_detail_about {
  border-bottom: 1px solid #dddddd;
  padding-bottom: 50px;
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
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
  font-weight: bold;
  margin: 10px 0;
}

.room_bed_img {
  width: 36px;
  height: 36px;
  margin-bottom: 12px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

/* Стили для блока удобств */
.facilities_grap {
   grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
  width: 40px;
  height: 40px;
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
  font-size: 16px;
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
  margin: 30px auto 100px;

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

@media (max-width: 768px) {
  .room_img_container {
    border-radius: 15px;
  }
}

.room_detail_wrapper {
  margin-top: 30px;
  display: grid;
  grid-template-columns: 58% 10% 32%;
}

.room_detail_wrapper_right {
  width: 100%;
  grid-column: 3;
  box-sizing: border-box;
}

.accordion-container {
  margin-top: 30px;
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



</style>