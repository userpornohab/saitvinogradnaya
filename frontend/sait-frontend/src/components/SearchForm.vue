<template>
  <div class="calendar-container" ref="calendarRef">
    <div class="inputs">
      <div
        class="field field--date"
        :class="{ 'field--active': showCalendar }"
        @click="toggleCalendar"
      >
        <span class="field-label">Заезд</span>
        <input
          type="text"
          :value="startDateText"
          placeholder="Добавить дату"
          readonly
          id="startDate"
        >
      </div>

      <div
        class="field field--date field--end"
        :class="{ 'field--active': showCalendar }"
        @click="toggleCalendar"
      >
        <span class="field-label">Выезд</span>
        <input
          type="text"
          :value="endDateText"
          placeholder="Добавить дату"
          readonly
          id="endDate"
        >
        <button
          v-if="startDate || endDate"
          type="button"
          class="field-clear"
          aria-label="Очистить даты"
          @click.stop="fetchAllRoomsand"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="field field--guests">
        <span class="field-label">Гости</span>
        <GuestsInput
          v-model:count="guestsCount"
          :MIN_GUESTS="MIN_GUESTS"
          :MAX_GUESTS="MAX_GUESTS"
        />
      </div>

      <button
        id="findBtn"
        class="find-btn"
        @click.stop="handleSearch"
        :disabled="isLoading || !isDateRangeValid"
        :aria-label="isLoading ? 'Поиск...' : 'Найти'"
      >
        <svg class="find-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="11" cy="11" r="7"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <span class="find-text">{{ isLoading ? 'Поиск...' : 'Найти' }}</span>
      </button>
    </div>
    
    <div 
      class="calendars" 
      ref="calendarsRef"
      :class="{
        visible: showCalendar,
        fullscreen: showCalendar && isMobile,
        'calendars--above': dropDirection === 'up'
      }"
    >
      <DateRangePicker
        v-model:startDate="startDate"
        v-model:endDate="endDate"
        v-model:error="searchError"
        @clear="fetchAllRoomsand"
        @close="toggleCalendar"         
        :isMobile="isMobile"             
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import GuestsInput from './GuestsInput.vue';
import DateRangePicker from './DateRangePicker.vue';

export default {
  components: {
    GuestsInput,
    DateRangePicker,
  },
  props: {
    fetchAllRooms: {
      type: Function,
      required: true,
    },
  },
  methods: {
    fetchAllRoomsand() {
      this.startDate = null;
      this.endDate = null;
      this.$emit('clire');
      return this.fetchAllRooms();
    },
  },
  emits: ['search', 'clire'],
  setup(props, { emit }) {
    const MIN_GUESTS = 1;
    const MAX_GUESTS = 4;
    const showCalendar = ref(false);
    const startDate = ref(null);
    const endDate = ref(null);
    const guestsCount = ref(1);
    const isLoading = ref(false);
    const searchError = ref(null);
    const calendarRef = ref(null);
    const calendarsRef = ref(null);
    const dropDirection = ref('down');

    // Определение мобильного устройства
    const isMobile = ref(false);
    const checkMobile = () => {
      isMobile.value = window.matchMedia('(max-width: 768px)').matches;
    };

    onMounted(() => {
      checkMobile();
      window.addEventListener('resize', checkMobile);
    });

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile);
    });

    // Блокировка прокрутки body при открытом fullscreen-календаре
    watch([showCalendar, isMobile], () => {
      const isFullscreen = showCalendar.value && isMobile.value;
      document.body.style.overflow = isFullscreen ? 'hidden' : '';
      document.body.classList.toggle('calendar-fullscreen-open', isFullscreen);
    });

    const startDateText = computed(() => startDate.value?.toLocaleDateString() || '');
    const endDateText = computed(() => endDate.value?.toLocaleDateString() || '');

    const isDateRangeValid = computed(() => {
      if (!startDate.value || !endDate.value) return false;
      const diffDays = Math.ceil((endDate.value - startDate.value) / (1000 * 60 * 60 * 24));
      return diffDays >= 3 && diffDays <= 90;
    });

    const toggleCalendar = () => {
      showCalendar.value = !showCalendar.value;
    };

    // Закрытие календаря после выбора конечной даты
    watch(endDate, (newEndDate) => {
      if (newEndDate && startDate.value && showCalendar.value) {
        setTimeout(() => {
          showCalendar.value = false;
        }, 50);
      }
    });

    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && showCalendar.value) {
        showCalendar.value = false;
      }
    };

    const handleSearch = async () => {
      if (!startDate.value || !endDate.value) {
        searchError.value = 'Пожалуйста, выберите даты заезда и выезда';
        return;
      }
      if (!isDateRangeValid.value) {
        searchError.value = 'Срок бронирования должен быть от 3 до 90 ночей';
        return;
      }
      if (guestsCount.value < MIN_GUESTS || guestsCount.value > MAX_GUESTS) {
        searchError.value = 'Некорректное количество гостей';
        return;
      }

      try {
        isLoading.value = true;
        const searchData = {
          guests: guestsCount.value,
          check_in_date: formatDate(startDate.value),
          check_out_date: formatDate(endDate.value),
        };
        emit('search', searchData);
        showCalendar.value = false;
      } catch (error) {
        searchError.value = `Ошибка поиска: ${error.message}`;
      } finally {
        isLoading.value = false;
      }
    };

    const formatDate = (date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };

    const handleClickOutside = (event) => {
      const isCalendarInput = event.target.closest('#startDate, #endDate');
      const isInsideCalendar = event.target.closest('.calendars') 
        || event.target.closest('.calendar-container');

      if (!isInsideCalendar && !isCalendarInput && showCalendar.value && !isMobile.value) {
        // На мобильных не закрываем по клику вне, только через кнопку
        showCalendar.value = false;
      }
    };

    const updateDropDirection = () => {
      if (isMobile.value || !calendarRef.value || !calendarsRef.value) return;
      const triggerRect = calendarRef.value.getBoundingClientRect();
      const popupHeight = calendarsRef.value.offsetHeight || 420;
      const spaceBelow = window.innerHeight - triggerRect.bottom;
      const spaceAbove = triggerRect.top;
      dropDirection.value = (spaceBelow < popupHeight && spaceAbove > spaceBelow) ? 'up' : 'down';
    };

    watch(showCalendar, (newVal) => {
      if (newVal) {
        nextTick(updateDropDirection);
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('keydown', handleKeyDown);
        window.addEventListener('resize', updateDropDirection);
        window.addEventListener('scroll', updateDropDirection, true);
      } else {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('keydown', handleKeyDown);
        window.removeEventListener('resize', updateDropDirection);
        window.removeEventListener('scroll', updateDropDirection, true);
      }
    });

    onUnmounted(() => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    });

    return {
      showCalendar,
      startDate,
      endDate,
      guestsCount,
      startDateText,
      endDateText,
      isLoading,
      searchError,
      isDateRangeValid,
      MIN_GUESTS,
      MAX_GUESTS,
      toggleCalendar,
      handleSearch,
      calendarRef,
      calendarsRef,
      dropDirection,
      isMobile,
    };
  },
};
</script>
  <style scoped>
  /* ======================================
     DESKTOP — Airbnb-style pill bar
     ====================================== */
  .calendar-container {
    z-index: 10000;
    display: flex;
    justify-content: center;
    font-family: 'Inter', 'Circular', 'Helvetica Neue', sans-serif;
    max-width: 640px;
    width: 100%;
    margin: 20px auto;
    position: relative;
  }

  .inputs {
    display: flex;
    align-items: stretch;
    width: 100%;
    background: var(--color-white, #fff);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 9999px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    padding: 0 5px;
    gap: 0;
    transition: background 0.2s ease, box-shadow 0.2s ease;
  }

  .inputs:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  /* ---- Сегмент поля ---- */
  .field {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    text-align: left;
    padding: 2px 18px;
    border-radius: 9999px;
    cursor: pointer;
    transition: background-color 0.15s ease;
    flex: 1 1 0;
    min-width: 0;
  }

  .field * { text-align: left; }

  .field:not(:first-child)::before {
    content: "";
    position: absolute;
    left: 0;
    top: 25%;
    bottom: 25%;
    width: 1px;
    background: #e0e0e0;
    transition: opacity 0.15s ease;
  }

  /* Приглушаем разделители при наведении */
  .inputs:hover .field::before,
  .inputs:has(.field:hover) .field::before,
  .inputs:has(.field--active) .field::before {
    opacity: 0;
  }

  .field:hover {
    background: #ebebeb;
  }

  .inputs:hover .field:not(:hover):not(.field--active) {
    background: transparent;
  }

  .field--active {
    background: var(--color-white, #fff);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  }

  .field--end {
    padding-right: 32px;
  }

  .field-clear {
    position: absolute;
    top: 50%;
    right: 8px;
    transform: translateY(-50%);
    width: 22px;
    height: 22px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    border: none;
    border-radius: 50%;
    background: transparent;
    color: #888;
    cursor: pointer;
    opacity: 0.55;
    transition: opacity 0.15s ease, background 0.15s ease, color 0.15s ease;
  }

  .field-clear:hover {
    opacity: 1;
    color: #222;
    background: rgba(0, 0, 0, 0.06);
  }

  .field-label {
    font-size: 12px;
    font-weight: 600;

    color: #222222;
    letter-spacing: 0.01em;
    margin-bottom: 0px;
    pointer-events: none;
  }


    .field--guests .field-label {
      transform: translateY(10px);
    }


  .field--guests {
    flex: 1.2 1 0;
    padding-right: 10px;
    
  }

  .field--guests :deep(.guests-container) {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 8px !important;
    padding: 0 !important;
    border: none !important;
    position: static !important;
    width: 100%;
  }

  .field--guests :deep(#guestsInput) {
    font-size: 14px;
    color: #222;
    padding: 0 !important;
    text-align: left;
    width: auto !important;
    flex: 1 1 auto;
    min-width: 0;
  }

  .field--guests :deep(.guests-controls) {
    position: static !important;
    transform: translate(0, -8px);
    right: auto !important;
    top: auto !important;
    gap: 4px;
    flex-shrink: 0;
  }

  .field--guests :deep(.guest-btn) {
    width: 34px;
    height: 34px;
    font-size: 15px;
    box-shadow: none;
    background: transparent;
    border: 1px solid #d1d1d1;
    color: #222;
  }

  .field--guests :deep(.guest-btn:hover:not(:disabled)) {
    background: #222;
    color: #fff;
    border-color: #222;
    transform: none;
  }

  /* ---- Поля с датами ---- */
  .inputs input {
    padding: 0;
    border: none;
    background: transparent;
    font-size: 14px;
    color: #222222;
    cursor: pointer;
    width: 100%;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .inputs input::placeholder {
    color: #717171;
  }

  input:active,
  input:focus-visible {
    outline: none;
    box-shadow: none;
  }

  /* ---- Кнопка поиска ---- */
  .find-btn {
    align-self: center;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border: none;
    background: linear-gradient(135deg, #4c4cf7 0%, #4c4cf7 50%, #5757da 100%);
    color: #fff;
    cursor: pointer;
    font-weight: 600;
    font-size: 13px;
    height: 40px;
    min-width: 40px;
    padding: 0 12px;
    border-radius: 9999px;
    box-shadow: 0 2px 6px rgb(66, 39, 218);
    transition: transform 0.15s ease, box-shadow 0.2s ease, background 0.2s ease, min-width 0.25s ease;
    flex-shrink: 0;
    margin: 0 2px;
  }

  .find-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgb(66, 39, 218);
  }

  .find-btn:active:not(:disabled) {
    transform: translateY(0);
  }

  .find-btn:disabled {
    background: #d1d1d1;
    box-shadow: none;
    cursor: not-allowed;
    color: #fff;
  }

  .find-icon {
    flex-shrink: 0;
  }

  /* На десктопе по умолчанию — только иконка, текст появляется при наведении строки */
  .find-text {
    max-width: 0;
    opacity: 0;
    overflow: hidden;
    transition: max-width 0.25s ease, opacity 0.2s ease;
    white-space: nowrap;
  }

  .inputs:hover .find-text,
  .field--active ~ * .find-text,
  .find-btn:focus-visible .find-text {
    max-width: 80px;
    opacity: 1;
  }

  /* Календарь popup */
  .calendars {
    pointer-events: none;
    position: absolute;
    top: calc(100% + 10px);
    left: 50%;
    transform: translateX(-50%) translateY(-8px);
    width: min(720px, calc(100vw - 32px));
    border-radius: 20px;
    padding: 8px;
    box-sizing: border-box;
    background: white;
    box-shadow: 0 8px 28px rgba(0,0,0,0.18), 0 2px 6px rgba(0,0,0,0.08);
    transition: opacity 0.2s ease, transform 0.2s ease;
    opacity: 0;
    z-index: 10001;
  }

  .calendars.visible {
    opacity: 1;
    pointer-events: auto;
    transform: translateX(-50%) translateY(0);
  }

  /* Открытие вверх */
  .calendars.calendars--above {
    top: auto;
    bottom: calc(100% + 10px);
    transform: translateX(-50%) translateY(8px);
  }
  .calendars.calendars--above.visible {
    transform: translateX(-50%) translateY(0);
  }

  /* Fullscreen-режим календаря */
  .calendars.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: white;
    z-index: 10001;
    overflow-y: auto;
    padding: 0 20px;
    box-sizing: border-box;
    margin: 0;
    border-radius: 0;
    box-shadow: none;
    opacity: 1;
    transform: none;
  }

  /* ======================================
     TABLET / MOBILE
     ====================================== */
  @media (max-width: 900px) {
    .field { padding: 2px 18px; }
    .field--guests .field-label { left: 18px; }
  }

  @media (max-width: 768px) {
    .calendar-container {
      margin: 16px auto;
      padding: 0 12px;
    }

    .inputs {
      flex-direction: column;
      border-radius: 24px;
      padding: 8px;
      gap: 4px;
    }

    .field {
      width: 100%;
      padding: 10px 18px;
      border-radius: 16px;
    }

    /* горизонтальные разделители между полями */
    .field:not(:first-child)::before {
      left: 16px;
      right: 16px;
      top: 0;
      bottom: auto;
      width: auto;
      height: 1px;
    }

    .field--guests {
      flex-direction: column;
      align-items: stretch;
      padding-right: 18px;
    }

    .field--guests .field-label {
      position: static;
      top: auto;
      left: auto;
    }

    .field--guests :deep(.guests-container) {
      padding: 0;
    }

    .find-btn {
      margin-top: 8px;
      width: 100%;
      height: 52px;
      min-width: 0;
    }

    .find-text {
      max-width: none;
      opacity: 1;
    }
  }
</style>