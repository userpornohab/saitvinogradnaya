<template>
  <div class="room_number" style="width: 100%;">
    <!-- Декоративная фоновая иллюстрация «Пляжный дом» -->
    <img
      src="@/assets/icons/plajniydom.svg"
      alt=""
      aria-hidden="true"
      class="rooms-bg-illustration"
      :class="{ 'is-loading': isLoading }"
    />

    <div v-if="isLoading" class="loading-indicator">
      <div class="spinner_grup">
        <div class="spinner"></div>
        <div class="spinner_text">Поиск подходящих комнат...</div>
      </div>
    </div>
    
    <div v-else class="room_serch" >
      <div v-if="rooms && rooms.length > 0" class="flex">
        <!-- Блок с фотографиями комнат -->
        <div 
          v-for="(room, index) in rooms" 
          :key="room.id" 
          class="room" 
          @click="goToRoomDetail(room.id)"
          :style="{
            transitionDelay: `${index * 0.1}s`,
            '--i': index
          }"
        >
          <div class="slider-container">
            <div class="slider-viewport">
              <div 
                class="slider-wrapper" 
                :style="{ transform: `translateX(${-currentPhotoIndex[room.id] * 100}%)` }"
              >
                <div 
                  v-for="(photo, idx) in sortedRoomPhotos(room).slice(0, 4)" 
                  :key="idx" 
                  class="slide"
                >
                  <img 
                    :src="getPhotoUrl(photo.url)" 
                    :alt="room.title" 
                    class="slider-image"
                  />
                </div>
              </div>
            </div>

            <div class="convenience">
              <div class="convenience_row_top">
                <div class="room-feature-pill">
                  <img class="icon-pad" src="@/assets/icons/user.svg" alt="">
                  <div>{{ room.max_guests }} чел.</div>
                </div>
                  <div class="room-feature-pill room-feature-pill--icon">
                    <img class="icon-pad" src="@/assets/icons/wifi.svg" alt="">
                  </div>
              </div>
              <div class="convenience_row_bot">
                <div class="room-feature-pill">
                  <img class="icon-pad" src="@/assets/icons/bed.svg" alt="">
                  <span>{{ room.bed_options.length }} {{ room.bed_options.length <= 1 ? 'кровать' : 'кровати' }}</span>
                </div>
              </div>
            </div>
            
            <div class="slider-controls" v-if="room.photos.length > 1" @click.stop>
              <button 
                class="slider-arrow prev" 
                @click.stop="prevPhoto(room.id)"
                :disabled="currentPhotoIndex[room.id] === 0"
              >
                <img  style="transform: rotate(180deg); width: 12px; height: 12px ;" class="" src="@/assets/icons/arrow-right.svg" alt="Назад">
              </button>
              
              <div class="slider-dots">
                <span 
                  v-for="(photo, idx) in sortedRoomPhotos(room).slice(0, 4)" 
                  :key="idx"
                  class="dot"
                  :class="{ active: currentPhotoIndex[room.id] === idx }"
                  @click.stop="setPhoto(room.id, idx)"
                ></span>
              </div>
              
              <button 
                class="slider-arrow next" 
                @click.stop="nextPhoto(room.id)"
                :disabled="currentPhotoIndex[room.id] === 3"
              >
                <img  style=" width: 12px; height: 12px ;" class="" src="@/assets/icons/arrow-left.svg" alt="Назад">
              </button>
            </div>
          </div>
          <div class="room-header">
            <div>
              <h4 >{{ room.title }}</h4>
              <div>{{ room.floor }} этаж</div>
            </div>
            
            <div class="price-range">
              <div v-if="getMinPrice(room) !== getMaxPrice(room)">
                <div style="margin-bottom: 6px;">от {{ getMinPrice(room) }}₽/ночь</div>
                <div>до {{ getMaxPrice(room) }}₽/ночь</div>
              </div>
              <div v-else>
                Цена: {{ getMinPrice(room) }}₽/ночь
              </div>
            </div>
          </div>
        </div>

        <!-- Отдельный блок с фотографиями двора (не привязан к комнатам) -->
        <div 
          v-if="pfoto_dvor && pfoto_dvor.length > 0" 
          class="room dvor-block"
          :style="{
            transitionDelay: `${rooms.length * 0.1}s`,
            '--i': rooms.length
          }"
        >
          <div class="slider-container-dvor">
            <div class="slider-viewport">
              <div 
                class="slider-wrapper" 
                :style="{ transform: `translateX(${-currentDvorPhotoIndex * 100}%)` }"
              >
                <div 
                  v-for="(photo, idx) in pfoto_dvor.slice(0, 4)" 
                  :key="idx" 
                  class="slide"
                  @click="openDvorModal(idx)" 
                >
                  <img 
                    :src="getPhotoUrl(photo.url)" 
                    :alt="'Фото двора'" 
                    class="slider-image"
                  />
                </div>
              </div>
            </div>
            
            <div class="slider-controls" v-if="pfoto_dvor.length > 1" @click.stop>
              <button 
                class="slider-arrow prev" 
                @click.stop="prevDvorPhoto"
                :disabled="currentDvorPhotoIndex === 0"
              >
                <img  style="transform: rotate(180deg); width: 12px; height: 12px ;" class="" src="@/assets/icons/arrow-right.svg" alt="Назад">
              </button>
              
              <div class="slider-dots">
                <span 
                  v-for="(photo, idx) in pfoto_dvor.slice(0, 4)" 
                  :key="idx"
                  class="dot"
                  :class="{ active: currentDvorPhotoIndex === idx }"
                  @click.stop="setDvorPhoto(idx)"
                ></span>
              </div>
              
              <button 
                class="slider-arrow next" 
                @click.stop="nextDvorPhoto"
                :disabled="currentDvorPhotoIndex === 3"
              >
                <img  style=" width: 12px; height: 12px ;" class="" src="@/assets/icons/arrow-left.svg" alt="Назад">
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else>
        <p>Нет доступных комнат по вашему запросу.</p>
      </div>
    </div>

    <PhotoModal

        tabindex="0"

        v-if="isDvorModalOpen"
        v-model="isDvorModalOpen"
        :photos="processedDvorPhotos"
        :initialIndex="dvorModalInitialIndex"
        roomTitle="Двор"
      />
  </div>
</template>

<script>
import { API_BASE_URL } from '@/api';
import PhotoModal from './PhotoModal.vue';
import { getRoomPath } from '@/utils/seo';
import { trackEvent } from '@/utils/analytics';

export default {
  components: {
    PhotoModal 
  },
  props: {
    url_data: {
      type: Object,
      default: null
    },
    rooms: {
      type: Array,
      required: true,
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    pfoto_dvor: {
      type: Array,
      required: true
    },
  },
  data() {
    return {
      isDvorModalOpen: false,
      dvorModalInitialIndex: 0,
      currentPhotoIndex: {},
      currentDvorPhotoIndex: 0,
    };
  },
    computed: {
    // Преобразуем фотографии для модального окна
    processedDvorPhotos() {
      return this.pfoto_dvor.map(photo => ({
        ...photo,
        fullUrl: this.getPhotoUrl(photo.url)
      }));
    }
  },
  methods: {
    openDvorModal(index) {
      this.dvorModalInitialIndex = index;
      this.isDvorModalOpen = true;
    },
    getIconUrl(icon) {
      return `${API_BASE_URL}/${icon}`;
    },
    getPhotoUrl(url) {
      return `${API_BASE_URL}${url}`;
    },
    sortedRoomPhotos(room) {
      return [...(room.photos || [])].sort((a, b) => {
        const orderDiff = (a.sort_order || 0) - (b.sort_order || 0);
        return orderDiff || a.id - b.id;
      });
    },
    goToRoomDetail(id) {
      const room = this.rooms.find(item => item.id === id);
      const queryParams = {};
      trackEvent('room_click', { roomId: id });
      
      if (this.url_data) {
        queryParams.start = this.url_data.start;
        queryParams.end = this.url_data.end;
        queryParams.guests = this.url_data.guests;
      }
      
      this.$router.push({
        path: room ? getRoomPath(room) : `/room=${id}`,
        query: queryParams
      });
    },
    initPhotoIndex(roomId) {
      if (this.currentPhotoIndex[roomId] === undefined) {
        const room = this.rooms.find(r => r.id === roomId);
        if (room) {
          const photos = this.sortedRoomPhotos(room);
          const mainPhotoIndex = photos.findIndex(p => p.is_main);
          this.currentPhotoIndex[roomId] = mainPhotoIndex !== -1 ? mainPhotoIndex : 0;
        }
      }
    },
    prevPhoto(roomId) {
      if (this.currentPhotoIndex[roomId] > 0) {
        this.currentPhotoIndex[roomId]--;
      }
    },
    nextPhoto(roomId) {
      const room = this.rooms.find(r => r.id === roomId);
      if (this.currentPhotoIndex[roomId] < room.photos.length - 1) {
        this.currentPhotoIndex[roomId]++;
      }
    },
    setPhoto(roomId, index) {
      this.currentPhotoIndex[roomId] = index;
    },
    prevDvorPhoto() {
      if (this.currentDvorPhotoIndex > 0) {
        this.currentDvorPhotoIndex--;
      }
    },
    nextDvorPhoto() {
      if (this.currentDvorPhotoIndex < this.pfoto_dvor.length - 1) {
        this.currentDvorPhotoIndex++;
      }
    },
    setDvorPhoto(index) {
      this.currentDvorPhotoIndex = index;
    },
    getMinPrice(room) {
      if (!room.price_periods?.length) return 0;
      const min = Math.min(...room.price_periods.map(p => p.price));
      return this.formatPrice(min);
    },
    getMaxPrice(room) {
      if (!room.price_periods?.length) return 0;
      const max = Math.max(...room.price_periods.map(p => p.price));
      return this.formatPrice(max);
    },
    formatPrice(price) {
      return Math.round(price).toLocaleString('ru-RU');
    }
  },
  watch: {
    rooms: {
      immediate: true,
      handler(newRooms) {
        newRooms.forEach(room => {
          this.initPhotoIndex(room.id);
        });
      }
    }
  }
};
</script>

<style scoped>
/* ================================================================
   Декоративная фоновая иллюстрация «Пляжный дом»
   ================================================================ */
.room_number {
  position: relative;
  overflow: hidden;
}

.rooms-bg-illustration {
  position: absolute;
  right: -6%;
  top: 50%;
  transform: translateY(-50%);
  width: clamp(520px, 45%, 620px);
  max-width: 620px;
  height: auto;
  pointer-events: none;
  user-select: none;
  z-index: 0;
  opacity: 0.08;
  filter: saturate(0.85);
  animation: rooms-bg-float 9s ease-in-out infinite;
  transition: opacity 600ms ease;
}

.room_serch,
.loading-indicator {
  position: relative;
  z-index: 1;
}

@keyframes rooms-bg-float {
  0%, 100% { transform: translateY(-50%) translateX(0) rotate(0deg); }
  50%      { transform: translateY(calc(-50% - 10px)) translateX(-6px) rotate(-1deg); }
}

.rooms-bg-illustration.is-loading {
  opacity: 0.16;
  animation: rooms-bg-loading 2.2s ease-in-out infinite;
}

@keyframes rooms-bg-loading {
  0%   { transform: translateY(-50%)           translateX(0)  rotate(0deg)   scale(1);     }
  25%  { transform: translateY(calc(-50% - 6px))  translateX(-4px) rotate(-1.5deg) scale(1.015); }
  50%  { transform: translateY(calc(-50% - 12px)) translateX(0)    rotate(0deg)    scale(1.03);  }
  75%  { transform: translateY(calc(-50% - 6px))  translateX(4px)  rotate(1.5deg)  scale(1.015); }
  100% { transform: translateY(-50%)           translateX(0)  rotate(0deg)   scale(1);     }
}

@media (prefers-reduced-motion: reduce) {
  .rooms-bg-illustration,
  .rooms-bg-illustration.is-loading {
    animation: none;
  }
}

/* ================================================================
   Сетка комнат
   ================================================================ */
.flex {
  gap: clamp(6px, 2vw, 30px);
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
}

@media (max-width: 930px) {
  .flex { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 768px) {
  .rooms-bg-illustration {
    width: 70%;
    right: -15%;
    opacity: 0.06;
  }
}

@media (max-width: 480px) {
  .rooms-bg-illustration { display: none; }
}

@media (max-width: 460px) {
  .flex { grid-template-columns: 1fr; }
}

/* Новые стили для слайдера */
.slider-container {
  position: relative;
  margin-bottom: 15px;
  aspect-ratio: 1 / 1;

  overflow: hidden;
  border-radius: 8px;
}
.slider-container-dvor{
  position: relative;
  margin-bottom: 15px;
  height: 100%;
  overflow: hidden;
  border-radius: 8px;
}

.slider-viewport {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.slider-wrapper {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}

.slide {
  flex: 0 0 100%;
  min-width: 100%;
  height: 100%;
}

.slider-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

/* Остальные стили остаются без изменений */
.room_serch {
  margin: 30px 0;
}

.spinner_text {
  font-size: 16px;
  color: #555;
}

.spinner_grup {
  justify-content: center;
  align-items: center;
  display: flex;
  gap: 30px;
}

/* Индикатор загрузки */
.loading-indicator {
  padding: 40px;
  height: 76vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #555;
}

.spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.room {
  
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

.icon-pad {
  width: 16px;
  height: 16px;
  filter: invert(100%);
  padding: 0;
}

.room-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.room-header h4 {
  font-size: 1.2rem;
  margin-bottom: 6px;
}


@media (max-width: 636px)  {
    .room-header{
      font-size: 12px;
    }


}

.flex_icons,
.room-feature-pill {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  color: white;
}

.room-feature-pill {
  align-self: flex-start;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 650;
  line-height: 1;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.32);
  border-radius: 999px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16);
}

.room-feature-pill--icon {
  width: 34px;
  height: 30px;
  padding: 0;
}

.price-range {
  display: flex;
  margin: 0;
}


.convenience_row_top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  left: 14px;
  right: 14px;
  position: absolute;
  top: 14px;
}

.convenience_row_bot {
  align-items: center;
  color: white;
  left: 14px;
  right: 14px;
  display: flex;
  position: absolute;
  bottom: 14px;
}

.convenience{
    opacity: 1;
    visibility:visible;
    transition: all 0.3s ease;
}
.slider-controls {
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  z-index: 0;
}

.room:hover .slider-controls {
  opacity: 1;
  visibility: visible;
}

.room:hover .convenience {
  opacity: 0;
  visibility:hidden
}

.slider-arrow {

  position: absolute;
  top: 50%;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
  z-index: 10;
  transform: translateY(-50%);
}

.prev {
  left: 12px;
}

.next {
  right: 12px;
}

.slider-arrow:hover:not(:disabled) {
  background: #3498db;
  color: white;
}

.slider-arrow:disabled {
  opacity: 0;
  cursor: not-allowed;
}

.slider-dots {
  position: absolute;
  bottom: 12px;
  display: flex;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 20px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ccc;
  cursor: pointer;
  transition: background 0.3s;
}

.dot.active {
  background: #3498db;
}

.dot:hover {
  background: #2980b9;
}

.h_room_number{
  font-size: 26px;
}
.room_number{
  
}
</style>
