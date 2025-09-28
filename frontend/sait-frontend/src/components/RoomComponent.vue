<template>
  <div class="room_number" style="width: 100%;">
    <h3 class="h_room_number">Номера</h3>
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
                  v-for="(photo, idx) in room.photos.slice(0, 4)" 
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
                <div class="flex_icons">
                  <img  class="icon-pad" src="@/assets/icons/user.svg" alt="Назад">
                  <div>{{ room.max_guests }} чел.</div>
                </div>
                  <div>
                    <img class="icon-pad" src="@/assets/icons/wifi.svg" alt="Назад">
                  </div>
              </div>
              <div class="convenience_row_bot">
                  <img class="icon-pad" src="@/assets/icons/bed.svg" alt="Назад">
                  <div style="display: flex; gap: 6px;" >{{ room.bed_options.length }} 
                    <div v-if="room.bed_options.length <= 1">кровать</div>
                    <div v-else>кровати</div>
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
                  v-for="(photo, idx) in room.photos.slice(0, 4)" 
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

    <!-- Модальное окно для фотографий двора -->
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
import PhotoModal from './PhotoModal.vue';

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
      return `http://127.0.0.1:8000/${icon}`;
    },
    getPhotoUrl(url) {
      return `http://127.0.0.1:8000${url}`;
    },
    goToRoomDetail(id) {
      const queryParams = {};
      
      if (this.url_data) {
        queryParams.start = this.url_data.start;
        queryParams.end = this.url_data.end;
        queryParams.guests = this.url_data.guests;
      }
      
      this.$router.push({
        name: 'RoomDetail',
        params: { id },
        query: queryParams
      });
    },
    initPhotoIndex(roomId) {
      if (this.currentPhotoIndex[roomId] === undefined) {
        const room = this.rooms.find(r => r.id === roomId);
        if (room) {
          const mainPhotoIndex = room.photos.findIndex(p => p.is_main);
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
/* Ограничиваем количество комнат в строке */
.flex {
  gap: clamp(6px, 2vw, 30px);
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  /* flex-wrap: wrap;
  justify-content: space-around; */
}
@media (max-width: 930px)  {
  .flex {
    grid-template-columns: 1fr 1fr ;

  }
}
@media (max-width: 460px)  {
  .flex {
    grid-template-columns: 1fr ;

  }
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
  width: clamp(20px, 2vw, 30px);

  filter: invert(100%);
  padding: 0 10px;
}

.room-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.room-header h4 {
  font-size: 1.2rem;
  margin: 0;
}


@media (max-width: 636px)  {
    .room-header{
      font-size: 12px;
    }
}

.flex_icons {
  
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  color: white;
}

.price-range {
  display: flex;
  font-size: 1.2rem;
  margin: 0;
  font-weight: 600;
}


.convenience_row_top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  position: absolute;
  top: 20px;
}

.convenience_row_bot {
  align-items: center;
  color: white;
  width: 100%;
  display: flex;
  position: absolute;
  bottom: 20px;
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
  background: rgba(0, 0, 0, 0.3);
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