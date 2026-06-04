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

    <div v-if="isLoading" class="rooms-skeleton" aria-busy="true" aria-live="polite">
      <span class="rooms-skeleton-label">{{ loadingText }}</span>
      <div class="flex">
        <article v-for="item in 3" :key="'room-skeleton-' + item" class="room room--skeleton">
          <div class="slider-container skeleton-block"></div>
          <div class="room-header room-header--skeleton">
            <div class="room-header-title-skeleton">
              <span class="skeleton-line skeleton-line--mid"></span>
              <span class="skeleton-line skeleton-line--tiny"></span>
            </div>
            <div class="price-range price-range--skeleton">
              <span class="skeleton-line skeleton-line--short"></span>
              <span class="skeleton-line skeleton-line--tiny"></span>
            </div>
          </div>
        </article>
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
                    loading="lazy"
                    decoding="async"
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

            <div class="room-details-pill">Подробнее</div>
            
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
              <div class="room-floor">{{ room.floor }} этаж</div>
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
                    loading="lazy"
                    decoding="async"
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
      
      <div v-else class="rooms-empty-state">
        <div class="rooms-empty-icon" aria-hidden="true">
          <svg viewBox="0 0 64 64" fill="none">
            <path d="M13 31.5C13 20.7 21.7 12 32.5 12S52 20.7 52 31.5 43.3 51 32.5 51 13 42.3 13 31.5Z" fill="currentColor" opacity="0.12"/>
            <path d="M22 34.5V25a4 4 0 0 1 4-4h12a4 4 0 0 1 4 4v9.5" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            <path d="M18 43V32.5a3 3 0 0 1 3-3h22a3 3 0 0 1 3 3V43" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            <path d="M18 43h28M23 43v-4M41 43v-4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            <path d="M46 18 18 46" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="rooms-empty-content">
          <h3>На выбранные даты свободных номеров нет</h3>
          <p>
            Попробуйте изменить даты, количество гостей или посмотрите все варианты размещения без фильтра.
          </p>
          <button
            v-if="url_data"
            type="button"
            class="rooms-empty-button"
            @click="$emit('reset-search')"
          >
            Показать все номера
          </button>
        </div>
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
    loadingText: {
      type: String,
      default: 'Загружаем номера...'
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
.loading-indicator,
.rooms-skeleton {
  position: relative;
  z-index: 1;
}

.rooms-skeleton {
  margin: 30px 0;
}

.rooms-skeleton-label {
  display: inline-flex;
  margin: 0 0 var(--spacing-md);
  color: var(--color-gray-500);
  font-size: var(--text-sm);
  font-weight: 700;
}

.room--skeleton {
  cursor: default;
}

.skeleton-block,
.skeleton-line {
  position: relative;
  overflow: hidden;
  background: linear-gradient(90deg, #ececf4 0%, #f8f7ff 46%, #ececf4 100%);
  background-size: 220% 100%;
  animation: skeleton-shimmer 1.35s ease-in-out infinite;
}

.skeleton-line {
  display: block;
  height: 12px;
  border-radius: 999px;
}

.skeleton-line--mid {
  width: 150px;
}

.skeleton-line--short {
  width: 118px;
}

.skeleton-line--tiny {
  width: 76px;
}

.room-header--skeleton {
  gap: var(--spacing-md);
}

.room-header-title-skeleton,
.price-range--skeleton {
  display: grid;
  gap: 10px;
}

.price-range--skeleton {
  justify-items: end;
}

@keyframes skeleton-shimmer {
  0% { background-position: 120% 0; }
  100% { background-position: -120% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-block,
  .skeleton-line {
    animation: none;
  }
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

.rooms-empty-state {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 560px);
  justify-content: center;
  align-items: center;
  gap: var(--spacing-xl);
  width: min(100%, 860px);
  margin: clamp(18px, 4vw, 42px) auto 0;
  padding: clamp(24px, 5vw, 44px);
  border: 1px solid rgba(198, 196, 253, 0.55);
  border-radius: var(--radius-xl);
  background:
    radial-gradient(420px 180px at 10% 15%, rgba(198, 196, 253, 0.28), transparent 70%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(248, 247, 255, 0.92));
  box-shadow: 0 18px 48px rgba(24, 24, 27, 0.07);
  overflow: hidden;
}

.rooms-empty-state::after {
  content: "";
  position: absolute;
  right: -54px;
  bottom: -68px;
  width: 180px;
  height: 180px;
  border: 34px solid rgba(198, 196, 253, 0.22);
  border-radius: 50%;
  pointer-events: none;
}

.rooms-empty-icon {
  position: relative;
  z-index: 1;
  width: clamp(76px, 11vw, 118px);
  height: clamp(76px, 11vw, 118px);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #5651d8;
  border-radius: 28px 10px 28px 10px;
  background: rgba(198, 196, 253, 0.22);
}

.rooms-empty-icon svg {
  width: 72%;
  height: 72%;
}

.rooms-empty-content {
  position: relative;
  z-index: 1;
}

.rooms-empty-content h3 {
  margin: 0 0 8px;
  color: var(--color-gray-900);
  font-size: clamp(1.25rem, 2vw, 1.75rem);
  line-height: 1.18;
}

.rooms-empty-content p {
  margin: 0;
  max-width: 54ch;
  color: var(--color-gray-600);
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
}

.rooms-empty-button {
  margin-top: var(--spacing-lg);
  padding: 12px 18px;
  border: 0;
  border-radius: var(--radius-full);
  background: #5651d8;
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(86, 81, 216, 0.22);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
}

.rooms-empty-button:hover {
  transform: translateY(-1px);
  background: #4640bd;
  box-shadow: 0 16px 30px rgba(86, 81, 216, 0.3);
}

.rooms-empty-button:focus-visible {
  outline: 3px solid rgba(86, 81, 216, 0.28);
  outline-offset: 3px;
}

@media (max-width: 640px) {
  .rooms-empty-state {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
    gap: var(--spacing-lg);
  }

  .rooms-empty-content p {
    margin-left: auto;
    margin-right: auto;
  }
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

.room-floor {
  color: var(--color-gray-700);
  font-size: 1rem;
  font-weight: 600;
}


@media (max-width: 636px)  {
    .room-header{
      font-size: 14px;
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

.room-details-pill {
  position: absolute;
  left: 50%;
  right: auto;
  bottom: 14px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  padding: 7px 12px;
  border-radius: 999px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.32);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16);
  font-size: 12px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transform: translateX(-50%);
  transition: opacity 0.22s ease, visibility 0.22s ease, box-shadow 0.22s ease;
}

.price-range {
  display: flex;
  margin: 0;
  color: var(--color-gray-700);
  font-size: 0.98rem;
  font-weight: 600;
  line-height: 1.35;
  text-align: right;
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
  right: 132px;
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

.room:hover .room-details-pill {
  opacity: 1;
  visibility: visible;
  animation: details-pill-pulse 1.45s ease-in-out infinite;
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
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 20px;
  z-index: 11;
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

@keyframes details-pill-pulse {
  0%, 100% {
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16);
  }
  50% {
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.3), 0 0 0 6px rgba(255, 255, 255, 0.16);
  }
}

@media (hover: none) and (pointer: coarse) {
  .room-details-pill {
    left: auto;
    right: 14px;
    transform: none;
    opacity: 1;
    visibility: visible;
    animation: details-pill-pulse 1.45s ease-in-out infinite;
  }
}

@media (prefers-reduced-motion: reduce) {
  .room:hover .room-details-pill,
  .room-details-pill {
    animation: none;
  }
}

.h_room_number{
  font-size: 26px;
}
.room_number{
  
}
</style>
