<template>
  <transition name="modal-fade">
    <div
      v-if="modelValue"
      class="photo-modal-overlay"
      @click="handleOverlayClick"
    >
      <div class="photo-modal-content" @click.stop>
        <!-- Заголовок -->
        <div class="modal-header">
          <h3 class="modal-title">{{ roomTitle }} — Фотографии</h3>
          <button class="modal-close" @click="closeModal">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Сетка фото (как на sutochno.ru) -->
        <div class="photo-grid">
          <div
            v-for="(photo, index) in photos"
            :key="photo.fullUrl || index"
            class="photo-grid-item"
            @click="openFullscreen(index)"
          >
            <img
              :src="photo.fullUrl"
              :alt="roomTitle"
              loading="lazy"
            />
          </div>
        </div>
      </div>
    </div>
  </transition>

  <!-- Полноэкранный просмотр одного фото -->
  <transition name="fullscreen-fade">
    <div
      v-if="isFullscreenOpen"
      class="fullscreen-viewer"
      @click="handleViewerClick"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <button class="viewer-close" @click.stop="closeFullscreen">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
      </button>
      <button class="viewer-nav viewer-prev" @click.stop="prevPhoto">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>

      <!-- Трек из всех слайдов: сдвигается по горизонтали -->
      <div
        class="viewer-track"
        :class="{ 'is-dragging': isDragging }"
        :style="trackStyle"
      >
        <div
          v-for="(photo, i) in photos"
          :key="photo.fullUrl || i"
          class="viewer-slide"
        >
          <img
            :src="photo.fullUrl"
            :alt="roomTitle"
            class="viewer-image"
            draggable="false"
            @dragstart.prevent
            @click.stop
          />
        </div>
      </div>

      <button class="viewer-nav viewer-next" @click.stop="nextPhoto">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
      <div class="viewer-counter">
        {{ currentFullscreenIndex + 1 }} / {{ photos.length }}
      </div>
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
      isFullscreenOpen: false,
      currentFullscreenIndex: 0,
      // Drag/swipe state
      dragStartX: null,
      dragStartY: null,
      dragDeltaX: 0,
      isDragging: false,
      wasDragged: false,
      swipeThreshold: 40
    }
  },

  computed: {
    trackStyle() {
      const base = -this.currentFullscreenIndex * 100;
      const drag = this.isDragging ? this.dragDeltaX : 0;
      return {
        transform: `translate3d(calc(${base}% + ${drag}px), 0, 0)`
      };
    }
  },

  watch: {
    modelValue(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden';
        window.addEventListener('keydown', this.handleKeydown);
      } else {
        document.body.style.overflow = '';
        window.removeEventListener('keydown', this.handleKeydown);
        this.closeFullscreen();
      }
    }
  },

  beforeUnmount() {
    document.body.style.overflow = '';
    window.removeEventListener('keydown', this.handleKeydown);
  },

  methods: {
    closeModal() {
      this.$emit('update:modelValue', false);
    },

    handleOverlayClick(e) {
      if (e.target === e.currentTarget) {
        this.closeModal();
      }
    },

    openFullscreen(index) {
      this.currentFullscreenIndex = index;
      this.isFullscreenOpen = true;
    },

    closeFullscreen() {
      this.isFullscreenOpen = false;
    },

    prevPhoto() {
      if (this.currentFullscreenIndex > 0) {
        this.currentFullscreenIndex--;
      } else {
        this.currentFullscreenIndex = this.photos.length - 1;
      }
    },

    nextPhoto() {
      if (this.currentFullscreenIndex < this.photos.length - 1) {
        this.currentFullscreenIndex++;
      } else {
        this.currentFullscreenIndex = 0;
      }
    },

    onPointerDown(e) {
      if (!this.isFullscreenOpen) return;
      // Не начинаем drag с кнопок управления
      if (e.target.closest('.viewer-nav, .viewer-close')) return;

      this.dragStartX = e.clientX;
      this.dragStartY = e.clientY;
      this.dragDeltaX = 0;
      this.isDragging = true;
      this.wasDragged = false;

      // Захватываем указатель, чтобы move/up приходили даже если курсор покинул элемент
      const el = e.currentTarget;
      if (el && el.setPointerCapture && e.pointerId != null) {
        try { el.setPointerCapture(e.pointerId); } catch (_) { /* noop */ }
      }
    },

    onPointerMove(e) {
      if (!this.isDragging || this.dragStartX === null) return;
      this.dragDeltaX = e.clientX - this.dragStartX;
      if (Math.abs(this.dragDeltaX) > 5) this.wasDragged = true;
    },

    onPointerUp(e) {
      if (!this.isDragging) return;
      const delta = this.dragDeltaX;
      this.isDragging = false;
      this.dragStartX = null;
      this.dragStartY = null;
      this.dragDeltaX = 0;

      const el = e && e.currentTarget;
      if (el && el.releasePointerCapture && e.pointerId != null) {
        try { el.releasePointerCapture(e.pointerId); } catch (_) { /* noop */ }
      }

      if (delta <= -this.swipeThreshold) {
        this.nextPhoto();
      } else if (delta >= this.swipeThreshold) {
        this.prevPhoto();
      }
    },

    handleViewerClick(e) {
      // Если только что был свайп — не закрываем окно
      if (this.wasDragged) {
        this.wasDragged = false;
        return;
      }
      // Закрываем только при клике на фон (не на фото и не на кнопки)
      if (e.target === e.currentTarget) {
        this.closeFullscreen();
      }
    },

    handleKeydown(e) {
      if (e.key === 'Escape') {
        if (this.isFullscreenOpen) {
          this.closeFullscreen();
        } else {
          this.closeModal();
        }
      }
      if (this.isFullscreenOpen) {
        if (e.key === 'ArrowRight') this.nextPhoto();
        if (e.key === 'ArrowLeft') this.prevPhoto();
      }
    }
  }
}
</script>

<style scoped>
/* ======================================
   MODAL OVERLAY & GRID
   ====================================== */
.photo-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 9999;
  /* Единственный скролл — у оверлея. Внутренний контент растёт свободно. */
  overflow-y: auto;
  overscroll-behavior: contain;
  display: flex;
  justify-content: center;
}

.photo-modal-content {
  background: var(--color-white);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 900px;
  /* высота по содержимому — без внутреннего скролла */
  height: auto;
  min-height: 100%;
  overflow: visible;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-gray-200);
  position: sticky;
  top: 0;
  background: var(--color-white);
  z-index: 10;
}

.modal-title {
  font-size: var(--text-xl);
  font-weight: 600;
  margin: 0;
  color: var(--color-gray-900);
}

.modal-close {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-100);
  color: var(--color-gray-700);
  transition: all var(--transition-fast);
  border: none;
  cursor: pointer;
}

.modal-close:hover {
  background: var(--color-gray-200);
  color: var(--color-gray-900);
}

/* ======================================
   PHOTO GRID — мозаика как в макете
   ====================================== */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-auto-rows: 280px;
  grid-auto-flow: dense;
  gap: 10px;
  padding: var(--spacing-lg);
}

/* Повторяющийся узор из 6 плиток:
   1 — большая 2×2 (герой)
   2, 3 — квадраты в один ряд
   4 — квадрат слева
   5 — высокая 1×2 справа
   6 — квадрат слева под 4 (dense fill) */
.photo-grid-item:nth-child(6n + 1) {
  grid-column: span 2;
  grid-row: span 2;
}
.photo-grid-item:nth-child(6n + 5) {
  grid-row: span 2;
}

@media (max-width: 768px) {
  .photo-grid {
    grid-auto-rows: 170px;
    gap: 8px;
    padding: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .photo-grid {
    grid-auto-rows: 140px;
    gap: 6px;
  }
}

.photo-grid-item {
  overflow: hidden;
  border-radius: var(--radius-md);
  cursor: pointer;
  position: relative;
  background: var(--color-gray-100);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.photo-grid-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  z-index: 1;
}

.photo-grid-item::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0);
  transition: background var(--transition-fast);
}

.photo-grid-item:hover::after {
  background: rgba(0, 0, 0, 0.15);
}

.photo-grid-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
  display: block;
}

.photo-grid-item:hover img {
  transform: scale(1.06);
}

/* ======================================
   FULLSCREEN VIEWER
   ====================================== */
.fullscreen-viewer {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: pan-y;
  user-select: none;
  overflow: hidden;
}

/* Горизонтальный трек со всеми слайдами */
.viewer-track {
  display: flex;
  width: 100%;
  height: 100%;
  will-change: transform;
  transition: transform 320ms cubic-bezier(0.22, 1, 0.36, 1);
  cursor: grab;
}

.viewer-track.is-dragging {
  transition: none;
  cursor: grabbing;
}

.viewer-slide {
  flex: 0 0 100%;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: var(--radius-md);
  user-select: none;
  -webkit-user-drag: none;
  pointer-events: none;  /* все жесты ловит трек/оверлей */
}

.viewer-close {
  position: absolute;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  z-index: 10;
  transition: background var(--transition-fast);
}

.viewer-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.viewer-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  z-index: 10;
  transition: background var(--transition-fast);
}

.viewer-nav:hover {
  background: rgba(255, 255, 255, 0.2);
}

.viewer-prev { left: var(--spacing-xl); }
.viewer-next { right: var(--spacing-xl); }

.viewer-counter {
  position: absolute;
  bottom: var(--spacing-xl);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  z-index: 10;
}

/* ======================================
   ANIMATIONS
   ====================================== */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity var(--transition-slow);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.fullscreen-fade-enter-active,
.fullscreen-fade-leave-active {
  transition: opacity var(--transition-slow);
}

.fullscreen-fade-enter-from,
.fullscreen-fade-leave-to {
  opacity: 0;
}

/* Scrollbar styling — применяется к оверлею, т.к. скролл теперь там */
.photo-modal-overlay::-webkit-scrollbar {
  width: 10px;
}

.photo-modal-overlay::-webkit-scrollbar-track {
  background: var(--color-gray-100);
}

.photo-modal-overlay::-webkit-scrollbar-thumb {
  background: var(--color-gray-300);
  border-radius: var(--radius-full);
}

.photo-modal-overlay::-webkit-scrollbar-thumb:hover {
  background: var(--color-gray-400);
}

@media (max-width: 768px) {
  .photo-modal-overlay {
    padding: 0;
  }

  .photo-modal-content {
    border-radius: 0;
  }

  .modal-header {
    padding: var(--spacing-md);
  }

  .photo-grid {
    gap: 4px;
    padding: var(--spacing-md);
  }

  .viewer-nav {
    width: 44px;
    height: 44px;
  }

  .viewer-prev { left: var(--spacing-md); }
  .viewer-next { right: var(--spacing-md); }
}
</style>
