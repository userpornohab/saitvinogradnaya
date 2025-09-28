<template>
  <transition name="zoom-fade">
    <div 
      v-if="modelValue" 
      class="modal-overlay"
      tabindex="0"
      ref="modal"
      @keydown="handleKeydown" 
    >
      <div 
        class="carousel-wrapper"
        ref="wrapper"
        @mousedown="startDrag"
        @touchstart.passive="startDrag"
      >
        <div 
          class="carousel-track"
          :style="trackStyle"
          ref="track"
        >
          <div 
            v-for="photo in photos" 
            :key="photo.fullUrl"
            class="carousel-slide"
          >
            <img 
              :src="photo.fullUrl" 
              :alt="roomTitle"
              class="modal-image"
              @dragstart.prevent
            />
          </div>
        </div>
      </div>
      
      <div class="photo-counter">
        {{ currentIndex + 1 }} / {{ photos.length }}
      </div>
      
      <button class="close-button" @click="closeModal">Закрыть</button>
      <button class="nav-button prev" @click.stop="prevPhoto">‹</button>
      <button class="nav-button next" @click.stop="nextPhoto">›</button>
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    photos: {
      type: Array,
      required: true
    },
    initialIndex: {
      type: Number,
      default: 0
    },
    roomTitle: {
      type: String,
      default: ''
    }
  },
  
  data() {
    return {
      currentIndex: this.initialIndex,
      startX: 0,
      currentTranslateX: 0,
      isDragging: false,
      slideWidth: 0,
      containerWidth: 0,
      dragDistance: 0
    }
  },
  
  computed: {
    trackStyle() {
      return {
        transform: `translateX(${this.currentTranslateX}px)`,
        transition: this.isDragging ? 'none' : 'transform 0.4s ease',
        width: `${this.photos.length * this.slideWidth}px`
      }
    }
  },
  
  watch: {
    photos: {
    handler() {
      this.$nextTick(() => {
        this.initCarousel();
      });
    },
    deep: true
  },
    initialIndex(newIndex) {
      this.currentIndex = newIndex
      this.updatePosition()
    },
    
    modelValue(newVal) {
    if (newVal) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', this.handleKeydown);
      
      this.$nextTick(() => {
        this.initCarousel();
        // Сбросим индекс при открытии
        this.currentIndex = this.initialIndex;
        this.updatePosition();
      });
    } else {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', this.handleKeydown);
    }
  }
  },
  
  mounted() {
    this.initCarousel();
    window.addEventListener('resize', this.initCarousel)
  },
  
  beforeUnmount() {
    this.cleanupEvents()
    document.body.style.overflow = ''
    window.removeEventListener('keydown', this.handleKeydown)
    window.removeEventListener('resize', this.initCarousel)
  },
  
  methods: {
    cleanupEvents() {
      window.removeEventListener('mousemove', this.dragMove)
      window.removeEventListener('mouseup', this.endDrag)
      window.removeEventListener('touchmove', this.dragMove)
      window.removeEventListener('touchend', this.endDrag)
    },
    
initCarousel() {
  if (!this.$refs.wrapper) return;
  
  // Используем реальную ширину контейнера вместо window.innerWidth
  this.containerWidth = this.$refs.wrapper.clientWidth;
  this.slideWidth = this.containerWidth;
  
  this.updatePosition();
},
    
    updatePosition() {
      this.currentTranslateX = -this.currentIndex * this.slideWidth
    },
    
    closeModal() {
      this.$emit('update:modelValue', false)
    },
    
    nextPhoto() {
      if (this.currentIndex < this.photos.length - 1) {
        this.currentIndex++
      } else {
        this.currentIndex = 0
      }
      this.updatePosition()
    },
    
    prevPhoto() {
      if (this.currentIndex > 0) {
        this.currentIndex--
      } else {
        this.currentIndex = this.photos.length - 1
      }
      this.updatePosition()
    },
    
    handleKeydown(e) {
      if (e.key === 'Escape') this.closeModal()
      if (e.key === 'ArrowRight') this.nextPhoto()
      if (e.key === 'ArrowLeft') this.prevPhoto()
    },
    
    startDrag(e) {
      // Игнорируем кнопки
      if (e.target.closest('button')) return
      
      // Очищаем предыдущие события
      this.cleanupEvents()
      
      this.isDragging = true
      this.startX = this.getPositionX(e)
      this.dragDistance = 0
      
      // Добавляем обработчики
      window.addEventListener('mousemove', this.dragMove)
      window.addEventListener('mouseup', this.endDrag)
      window.addEventListener('touchmove', this.dragMove, { passive: false })
      window.addEventListener('touchend', this.endDrag)
    },
    
    dragMove(e) {
      if (!this.isDragging) return
      e.preventDefault()
      
      const currentX = this.getPositionX(e)
      this.dragDistance = currentX - this.startX
      
      // Обновляем позицию трека
      this.currentTranslateX = -this.currentIndex * this.slideWidth + this.dragDistance
    },
    
    endDrag() {
      if (!this.isDragging) return
      
      this.isDragging = false
      this.cleanupEvents()
      
      // Порог для смены слайда - 100px или 20% ширины экрана
      const threshold = Math.min(100, window.innerWidth * 0.2)
      const absDistance = Math.abs(this.dragDistance)
      
      if (absDistance > threshold) {
        if (this.dragDistance > 0) {
          this.prevPhoto()
        } else {
          this.nextPhoto()
        }
      } else {
        // Возвращаем на текущую позицию
        this.updatePosition()
      }
    },
    
    getPositionX(e) {
      if (e.type.includes('touch')) {
        return e.touches[0] ? e.touches[0].clientX : e.changedTouches[0].clientX
      }
      return e.clientX
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  overflow: hidden;
  user-select: none;
}

.carousel-wrapper {
  width: 90vw;
  height: 80vh;
  overflow: hidden;
  position: relative;
  cursor: grab;
}

.carousel-wrapper:active {
  cursor: grabbing;
}

.carousel-track {
  display: flex;
  height: 100%;
  will-change: transform;
}

.carousel-slide {
  width: 90vw;
  height: 80vh;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-image {
  max-width: 100%;
  max-height: 100%;
  display: block;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  object-fit: contain;
  pointer-events: none;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  color: white;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid white;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 16px;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.close-button:hover {
  background: rgba(100, 100, 100, 0.7);
}

.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid white;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 28px;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.nav-button:hover {
  background: rgba(100, 100, 100, 0.7);
  transform: translateY(-50%) scale(1.1);
}

.prev {
  left: 20px;
}

.next {
  right: 20px;
}

.photo-counter {
  position: absolute;
  left: 50%;
  bottom: 20px;
  transform: translateX(-50%);
  color: white;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 16px;
  z-index: 10;
}

/* Анимации */
.zoom-fade-enter-active,
.zoom-fade-leave-active {
  transition: opacity 0.3s ease;
}

.zoom-fade-enter-active .carousel-wrapper,
.zoom-fade-leave-active .carousel-wrapper {
  transition: all 0.4s cubic-bezier(0.22, 0.61, 0.36, 1);
}

.zoom-fade-enter-from,
.zoom-fade-leave-to {
  opacity: 0;
}

.zoom-fade-enter-from .carousel-wrapper {
  transform: scale(0.8);
  opacity: 0;
}

.zoom-fade-enter-to .carousel-wrapper {
  transform: scale(1);
  opacity: 1;
}

.zoom-fade-leave-to .carousel-wrapper {
  transform: scale(0.8);
  opacity: 0;
}
</style>