<template>
  <div
    :class="{ 'single-month': singleMonth, 'lazy-mobile-calendar': isMobile && lazyMobile }"
    style="width: 100%; height: 100%;"
  >
    <div class="head-cal-conter">
      <div class="head-cal">
            <div style="width: 100%; display: flex; margin-bottom: 10px; ">
              <div class="calendar-name">Календарь</div>
              <button v-if="isMobile" class="close-btn" @click="$emit('close')">✕</button>
            </div>
            <hr>
            <div class="weekday-mobail" >
              <div 
                    v-for="day in weekDays" 
                    :key="day"
                  >
                    {{ day }}
                  </div>
            </div>
            <hr>
            
          </div>
    </div>
    
    
    
    
    <div class="navigation">
      <button
        class="nav-btn-start"
        @click="changeMonth(-1)"
        :class="{ visible: canShowPrev }"
      >
        <img class="svg_prev" src="@/assets/icons/arrow-left.svg" alt="Назад">
      </button>

      <div v-if="!singleMonth" class="selectors">
        <div class="year-select">
          <div
            v-for="year in years"
            :key="year"
            class="year-option"
            :class="{
              selected: year === currentYear,
              disabled: isYearDisabled(year)
            }"
            @click="selectYear(year)"
          >
            {{ year }}
          </div>
        </div>

        <div class="month-select">
          <div
            v-for="(month, index) in months"
            :key="index"
            class="month-option"
            :class="{
              selected: index === currentMonth,
              disabled: isMonthDisabled(index)
            }"
            @click="selectMonth(index)"
          >
            {{ month }}
          </div>
        </div>
      </div>

      <div v-else class="current-month-label">{{ calendars[0]?.title || '' }}</div>

      <button
        class="nav-btn-end"
        @click="changeMonth(1)"
        :class="{ nevisible: !canShowNext }"
      >
        <img class="svg_nex" src="@/assets/icons/arrow-right.svg" alt="Вперед">
      </button>
    </div>

    <div class="calendar-grid"
        :class="{ 'no-margin': noMargin }">
      <div 
        class="calendar-wrapper" 
        v-for="(calendar, index) in calendars" 
        :key="index"
      >
        <div class="month-title">{{ calendar.title }}</div>
        <div class="calendar dopcal">
          <div 
            class="weekday" 
            v-for="day in weekDays" 
            :key="day"
          >
            {{ day }}
          </div>
          <div 
            v-for="cell in calendar.days" 
            :key="cell.key"
            class="day"
            :class="getDayClasses(cell)"
            @click="selectDate(cell)"
            @mouseover="handleHover(cell)"
          >
            {{ cell.day }}
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="canLoadMoreMonths"
      ref="loadMoreTrigger"
      class="calendar-load-trigger"
      aria-hidden="true"
    >
      <span>Загружаем следующие месяцы...</span>
    </div>

  </div>
</template>

<script>
import { ref, computed, nextTick, onBeforeUnmount, onMounted, watch } from 'vue';

export default {

  
  props: {
    startDate: Date,
    endDate: Date,
    occupiedDates: {
      type: Object,
      default: () => ({}),
    },
    noMargin: {
      type: Boolean,
      default: false
    },
    numberOfRooms: {
      type: Number,
      default: 0,
    },
    handleClear: {
      type: Function,
      required: true,
    },
    pricePeriods: {
      type: Array,
      default: () => []
    },
    isMobile: {               // Новый пропс для определения мобильности
      type: Boolean,
      default: false
    },
    singleMonth: {            // Показывать только один месяц + стрелки (для room_detail_datapiker)
      type: Boolean,
      default: false
    },
    lazyMobile: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:startDate', 'update:endDate', 'clear', 'close'], // Добавлено событие close
  setup(props, { emit }) {
    const currentYear = ref(new Date().getFullYear());
    const currentMonth = ref(new Date().getMonth());
    const hoverEndDate = ref(null);
    const mobileMonthsToShow = ref(2);
    const loadMoreTrigger = ref(null);
    let loadObserver = null;
    let loadLock = false;

    const months = [
      'Январь', 'Февраль', 'Март', 'Апрель', 
      'Май', 'Июнь', 'Июль', 'Август', 
      'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

    const padDatePart = (value) => String(value).padStart(2, '0');

    const dateKeyFromParts = (year, monthIndex, day) => (
      `${year}-${padDatePart(monthIndex + 1)}-${padDatePart(day)}`
    );

    const dateKeyFromDate = (date) => dateKeyFromParts(
      date.getFullYear(),
      date.getMonth(),
      date.getDate()
    );

    const normalizedTimestamp = (date) => new Date(
      date.getFullYear(),
      date.getMonth(),
      date.getDate()
    ).getTime();

    const parseDateOnly = (value) => {
      if (!value) return null;
      if (value instanceof Date) {
        return new Date(value.getFullYear(), value.getMonth(), value.getDate());
      }

      const [year, month, day] = String(value).slice(0, 10).split('-').map(Number);
      if (!year || !month || !day) return null;
      return new Date(year, month - 1, day);
    };

    const todayTimestamp = computed(() => {
      const today = new Date();
      return new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
    });

    const occupiedDateKeys = computed(() => {
      if (!props.numberOfRooms) return new Set();
      return new Set(
        Object.entries(props.occupiedDates || {})
          .filter(([, count]) => count >= props.numberOfRooms)
          .map(([dateKey]) => dateKey)
      );
    });

    const pricedDateKeys = computed(() => {
      if (!props.pricePeriods || props.pricePeriods.length === 0) return null;

      const keys = new Set();
      props.pricePeriods.forEach((period) => {
        const start = parseDateOnly(period.start_date);
        const end = parseDateOnly(period.end_date);
        if (!start || !end || end < start) return;

        const current = new Date(start);
        while (current <= end) {
          keys.add(dateKeyFromDate(current));
          current.setDate(current.getDate() + 1);
        }
      });

      return keys;
    });

    const selectionTimestamps = computed(() => ({
      start: props.startDate ? normalizedTimestamp(props.startDate) : null,
      end: props.endDate ? normalizedTimestamp(props.endDate) : null,
      hover: hoverEndDate.value ? normalizedTimestamp(hoverEndDate.value) : null,
    }));

    const maxMobileMonths = computed(() => {
      const current = new Date();
      const limit = new Date(current.getFullYear() + 2, current.getMonth());
      const start = new Date(currentYear.value, currentMonth.value);
      const diff = (limit.getFullYear() - start.getFullYear()) * 12 + limit.getMonth() - start.getMonth() + 1;
      return Math.max(1, diff);
    });

    const canLoadMoreMonths = computed(() => (
      props.isMobile &&
      props.lazyMobile &&
      !props.singleMonth &&
      mobileMonthsToShow.value < maxMobileMonths.value
    ));

    // Генерация календарей: в мобильной форме бронирования месяцы подгружаются постепенно
    const calendars = computed(() => {
      const mobileMonths = props.lazyMobile
        ? Math.min(mobileMonthsToShow.value, maxMobileMonths.value)
        : 12;
      const monthsToShow = props.singleMonth ? 1 : (props.isMobile ? mobileMonths : 2);
      return Array.from({ length: monthsToShow }, (_, offset) => {
        const year = currentYear.value;
        const month = currentMonth.value + offset;
        const date = new Date(year, month);
        return {
          year: date.getFullYear(),
          month: date.getMonth(),
          title: `${months[date.getMonth()]} ${date.getFullYear()}`,
          days: generateCalendarDays(date)
        };
      });
    });

    const generateCalendarDays = (date) => {
      const year = date.getFullYear();
      const month = date.getMonth();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstDay = new Date(year, month, 1).getDay();
      const emptyCells = (firstDay + 6) % 7;
      const days = [];

      for (let i = 0; i < emptyCells; i++) {
        days.push({ day: '', key: `${year}-${month}-empty-${i}` });
      }

      for (let day = 1; day <= daysInMonth; day++) {
        const dateObj = new Date(year, month, day);
        const dateKey = dateKeyFromParts(year, month, day);
        days.push({
          day,
          date: dateObj,
          dateKey,
          timestamp: dateObj.getTime(),
          year,
          month,
          key: dateKey
        });
      }

      return days;
    };

    const isPastMonth = (year, month) => {
      const current = new Date();
      return year < current.getFullYear() || 
            (year === current.getFullYear() && month <= current.getMonth());
    };

    const isFutureLimit = (year, month) => {
      const current = new Date();
      const limit = new Date(current.getFullYear() + 2, current.getMonth());
      return new Date(year, month) > limit;
    };

    const canShowPrev = computed(() => !isPastMonth(currentYear.value, currentMonth.value));
    const canShowNext = computed(() => !isFutureLimit(currentYear.value, currentMonth.value));
    const years = computed(() => {
      const current = new Date().getFullYear();
      return [current, current + 1, current + 2];
    });

    const isDateOccupied = (cell) => {
      if (!cell?.dateKey) return false;
      return occupiedDateKeys.value.has(cell.dateKey);
    };

    const handleHover = (cell) => {
      if (props.isMobile || !cell?.date) return;
      if (props.startDate && !props.endDate && cell.date >= props.startDate) {
        hoverEndDate.value = cell.date;
      }
    };

    const hasPriceForDate = (cell) => {
      if (!cell?.dateKey) return false;
      return pricedDateKeys.value === null || pricedDateKeys.value.has(cell.dateKey);
    };

    const isDateBlockedByBaseRules = (cell) => {
      if (!cell?.date) return true;
      return cell.timestamp < todayTimestamp.value ||
        isFutureLimit(cell.year, cell.month);
    };

    const canUseAsCheckoutDate = (cell) => (
      props.startDate &&
      !props.endDate &&
      cell?.date > props.startDate &&
      !isDateBlockedByBaseRules(cell) &&
      hasPriceForDate(cell) &&
      !isDateOccupied(cell)
    );

    const selectDate = (cell) => {
      if (!cell?.date) return;

      if (!props.startDate || props.endDate) {
        if (isDateBlockedByBaseRules(cell) || !hasPriceForDate(cell) || isDateOccupied(cell)) return;
        emit('update:startDate', cell.date);
        emit('update:endDate', null);
      } else if (cell.date > props.startDate) {
        if (!canUseAsCheckoutDate(cell)) return;
        emit('update:endDate', cell.date);
      } else {
        if (isDateBlockedByBaseRules(cell) || !hasPriceForDate(cell) || isDateOccupied(cell)) return;
        emit('update:startDate', cell.date);
        emit('update:endDate', null);
      }
      hoverEndDate.value = null;
    };

    const getDayClasses = (cell) => {
      if (!cell.date) return 'empty';
      const date = cell.timestamp;
      const { start: startTimestamp, end: endTimestamp, hover: hoverTimestamp } = selectionTimestamps.value;
      const isStart = date === startTimestamp;
      const isValidEnd = props.endDate 
        ? props.endDate >= props.startDate 
        : hoverEndDate.value >= props.startDate;
      const isEnd = (date === endTimestamp && isValidEnd)
        || (!props.endDate && date === hoverTimestamp && isValidEnd);
      const inRange = props.startDate && props.endDate && 
                    date > startTimestamp &&
                    date < endTimestamp;
      const inHoverRange = props.startDate && hoverEndDate.value && 
                         date > startTimestamp &&
                         date < hoverTimestamp;
      const isDisabled = isDateBlockedByBaseRules(cell);
      const isOccupied = isDateOccupied(cell);
      const noPrice = !hasPriceForDate(cell);
      const isUnavailable = isDisabled || noPrice || isOccupied;

      return {
        'selected': isStart || isEnd || inRange || inHoverRange,
        'start-date': isStart,
        'end-date': isEnd,
        'occupied': isOccupied && !isDisabled,
        'disabled': isUnavailable,
      };
    };

    const changeMonth = (offset) => {
      const newMonth = currentMonth.value + offset;
      const newYear = currentYear.value;
      const limitDate = new Date(new Date().getFullYear() + 2, new Date().getMonth());

      if (new Date(newYear, newMonth) > limitDate) return;

      currentMonth.value = (newMonth + 12) % 12;
      if (newMonth > 11) currentYear.value++;
      if (newMonth < 0) currentYear.value--;
    };
    
    const isYearDisabled = (year) => {
      const current = new Date().getFullYear();
      return year < current || year > current + 2;
    };

    const isMonthDisabled = (month) => {
      const current = new Date();
      const currentYearNow = current.getFullYear();
      const currentMonthNow = current.getMonth();

      if (currentYear.value < currentYearNow) return true;
      if (currentYear.value === currentYearNow) return month < currentMonthNow;
      if (currentYear.value === currentYearNow + 2) return month > currentMonthNow;
      return false;
    };

    const selectYear = (year) => {
      if (!isYearDisabled(year)) {
        const current = new Date();
        if (year === current.getFullYear()) {
          currentMonth.value = Math.max(currentMonth.value, current.getMonth());
        }
        if (year === current.getFullYear() + 2) {
          currentMonth.value = Math.min(currentMonth.value, current.getMonth());
        }
        currentYear.value = year;
      }
    };

    const selectMonth = (month) => {
      if (!isMonthDisabled(month)) {
        currentMonth.value = month;
      }
    };

    const loadMoreMonths = () => {
      if (!canLoadMoreMonths.value || loadLock) return;
      loadLock = true;
      mobileMonthsToShow.value = Math.min(mobileMonthsToShow.value + 2, maxMobileMonths.value);
      window.setTimeout(() => {
        loadLock = false;
      }, 120);
    };

    const setupLazyObserver = async () => {
      await nextTick();

      if (loadObserver) {
        loadObserver.disconnect();
        loadObserver = null;
      }

      if (!canLoadMoreMonths.value || !loadMoreTrigger.value || typeof IntersectionObserver === 'undefined') {
        return;
      }

      loadObserver = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          loadMoreMonths();
        }
      }, {
        root: null,
        rootMargin: '240px 0px',
        threshold: 0
      });

      loadObserver.observe(loadMoreTrigger.value);
    };

    onMounted(setupLazyObserver);

    onBeforeUnmount(() => {
      if (loadObserver) {
        loadObserver.disconnect();
      }
    });

    watch(canLoadMoreMonths, setupLazyObserver);
    watch(mobileMonthsToShow, setupLazyObserver);

    return {
      currentYear,
      currentMonth,
      calendars,
      canLoadMoreMonths,
      loadMoreTrigger,
      canShowPrev,
      canShowNext,
      years,
      months,
      weekDays,
      selectDate,
      handleHover,
      getDayClasses,
      changeMonth,
      selectYear,
      selectMonth,
      isYearDisabled,
      isMonthDisabled
    };
  }
};
</script>
  
  <style scoped>

  .close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 0 10px;
  color: #333;
}
.head-cal-conter{
  display: none;
}

/* Адаптация под мобильные экраны */
@media (max-width: 768px) {


  .calendar-wrapper {
    min-width: 100%;
  }
  .flex{
    padding: 20px ;
  }
  .day {
    width: 40px;
    height: 40px;
    font-size: 14px;
  }

  .weekday-mobail{
    margin: 5px 0;
    color: #000000;
    display: grid;
    justify-items: center;
    justify-content: center;
    grid-template-columns: repeat(7, minmax(0, 1fr));
  }

  .weekday {
    display: none;
  }
  .calendar-grid {
    padding: 12px 0 24px 0 ;
    flex-direction: column;
    align-items: center;
  }
  .navigation {
    display: none;

  }
  .head-cal-conter{
  display: block;
}
  .head-cal{
  padding: 20px 20px 0 20px ;
  position: fixed;
  left: 0;
  right: 0;

  background-color: #ffffff;
  z-index: 100000000;
  }

  .nav-contr{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-md);
    width: 100%;
  }

  .current-month-label {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--color-gray-900);
    text-align: center;
    flex: 1;
  }

  .close-btn {
    margin-left: auto;
  }
}

  .calendar-wrapper{
    width: 315px;
    color: black;
  }
  
  .flex{
    display: flex;
    justify-content: space-between;
  }
  

  .nav-btn-start.visible{
    background: none;
    color: rgb(255, 255, 255);
    pointer-events: painted;
    cursor: pointer;
    opacity: 1;
  }
  
  .svg_prev{
    width: 16px;
    height: 16px;
    transform: rotate(180deg)
  }
  
  .svg_nex{
    width: 16px;
    height: 16px;
  }
  
  .nav-btn-end.nevisible{
    background: none;
    pointer-events: none;
    cursor: not-allowed;
    color: rgb(0, 0, 0);
    opacity: 0.5;
  }
  .nav-contr{
        display: flex;
    align-items: center;
    justify-content: center;
    color: #000000;
  }

  
  .nav-btn-start {
    box-sizing: border-box;
    padding: 4px;
    align-items: center;
    display: flex;    
    justify-content: center;
    background: none;
    border: none;
    opacity: 0.5;
    color: rgb(0, 0, 0);
    border-radius: 50%;

    pointer-events: none;
    cursor: not-allowed;
  }
  
  .month-option.disabled {
    opacity: 0.5;
    pointer-events: none;
    cursor: not-allowed;
  }
  
  .nav-btn-end {
    box-sizing: border-box;
    display: flex;    
    padding: 4px;
    align-items: center;
    justify-content: center;
    border: none;
    background: none;
    color: white;
    border-radius: 50%;
    cursor: pointer;
  }
  
  .nav-btn-end:hover {
    background: #c6c4fd;
  }
  .nav-btn-start:hover {
    background: #c6c4fd;
  }
  
  .selectors {
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex-grow: 1;
    color: #000000;
  }
  
  .month-select, .year-select {
    display: flex;

    flex: 0 0 16.66%;
    flex-wrap: wrap;
  }
  
  .month-select{
    justify-content: space-between;
  }
  
  .month-option, .year-option {
    font-size: 12px;
    padding: 2px 4px;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .month-option:hover, .year-option:hover {
    background: #e9ecef;
}


.month-option.selected, .year-option.selected {
  background: #c6c4fd;
  color: white;
  border-color: #c6c4fd;
}

.calendar-grid {
  display: flex;
  justify-content: space-evenly;
  flex-wrap: wrap;
  margin-bottom: 5px;
}

.calendar-load-trigger {
  min-height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b8b98;
  font-size: 13px;
}

.calendar-load-trigger span {
  padding: 8px 12px;
  border-radius: 999px;
  background: #f5f4ff;
}

@media (hover: hover) and (pointer: fine) {
  .day:not(.disabled):not(.selected):hover {
    background-color: #ffffff;
    cursor: pointer;
    border: 1px solid #000000;
    border-radius: 50%;
  }
}




.occupied{
  opacity: 0.5;
  pointer-events: none;
  text-decoration: line-through;
  text-decoration-style:solid  ;    
  text-decoration-thickness: 1px;    
  
}
.day.selected.occupied{
  
  background-color:#4c4cf771 ;
  color: #5a0202;
  border-bottom: 1px solid #5a0202;
  border-top: 1px solid #5a0202;
}


.month-title {
  text-align: center;
  font-weight: bold;
  margin: 15px 0;
  color: #333;
}

.calendar {
  display: grid;
  justify-items: center; 
  justify-content: center;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0;
  grid-auto-columns: 0;
  width: 100%;
  row-gap: 2px;
}

.weekday {
  text-align: center;
  font-weight: bold;
  font-size: 12px;
  padding: 5px 0;
}

.day {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
  caret-color: transparent;
  box-sizing: border-box;
  width: 45px;
  height: 45px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background: rgba(255, 255, 255, 0);
  /* можно добавить line-height: 1; для контроля */
}

.day.selected {
  background: #c6c4fd;
  color: white;
  width: 100%;
}

.day.start-date {
  background: linear-gradient(to right, #ffffff, #ffffff, #c6c4fd);
  color: white;
  z-index: 0;
  position: relative;
}

.day.end-date {
  color: white;
  z-index: 0;
  position: relative;
  background: linear-gradient(to right, #c6c4fd, #ffffff, #ffffff);
}

.day.start-date::before,
.day.end-date::before {
  position: absolute;
  content: " ";
  border-radius: 50%;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 45px;
  height: 100%;
  z-index: -1;
}

.day.start-date::before {
  background: linear-gradient(to right, #752424, #4c4cf7);
}

.day.end-date::before {
  background: linear-gradient(to left, #4c4cf7, #752424);
}


/* unused — button removed */
#clearBtn {
  height: fit-content;
  padding: 6px 12px;
  border: 1px solid #dc3545;
  background: white;
  color: red;
  border-radius: 4px;
  cursor: pointer;
}

#clearBtn:hover {
  background: #f3697727;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  display: flex;
  align-items: center;
  text-align: center;
}
hr{
  margin: 0;
}
.disabled {
  opacity: 0.3;
  pointer-events: none;
}

.empty {
  pointer-events: none;
}

.calendar-name{
  color: #000000;
  
  display: flex;
  flex-direction: column ;
  justify-content: center;
}

.calendar-grid.no-margin {
  padding: 0;
}

.navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  margin: 0 auto 12px;
  box-sizing: border-box;
}

.current-month-label {
  flex: 1;
  text-align: center;
  font-weight: 600;
  color: #222;
}

.navigation .selectors {
  flex: 1;
}

/* === room_detail_datapiker: только один месяц + стрелки === */
.single-month .navigation {
  display: flex;
  max-width: 420px;
}
.single-month .calendar-grid { padding: 0; justify-content: center; }
.single-month .month-title { display: none; }
.single-month .head-cal-conter { display: none !important; }
.single-month .calendar-wrapper { width: 100%; max-width: 420px; }
.single-month .calendar-wrapper ~ .calendar-wrapper { display: none; }

@media (max-width: 768px) {
  .single-month .calendar-grid { padding: 0; }
  .single-month .weekday { display: block; }
  .single-month .weekday-mobail { display: none; }
}

@media (max-width: 768px) {
  .lazy-mobile-calendar .navigation {
    display: none;
  }

  .lazy-mobile-calendar .head-cal {
    box-sizing: border-box;
    position: sticky;
    top: -10px;
    padding: 20px 20px 0;
    width: 100%;
    background-color: #ffffff;
    z-index: 10;
  }

  .lazy-mobile-calendar .calendar-grid {
    display: block;
    width: 100%;
    box-sizing: border-box;
    padding: 12px 0 24px;
    margin: 0;
    overflow-x: hidden;
  }

  .lazy-mobile-calendar .calendar-wrapper {
    width: 100%;
    min-width: 0;
    max-width: 360px;
    box-sizing: border-box;
    margin: 0 auto 22px;
    color: #000000;
  }

  .lazy-mobile-calendar .calendar {
    width: 100%;
    max-width: 360px;
    margin: 0 auto;
    grid-template-columns: repeat(7, minmax(0, 1fr));
  }

  .lazy-mobile-calendar .day {
    width: 100%;
    min-width: 0;
    height: 42px;
    font-size: 14px;
  }

  .lazy-mobile-calendar .day.start-date::before,
  .lazy-mobile-calendar .day.end-date::before {
    width: 42px;
    height: 42px;
    top: 50%;
    transform: translate(-50%, -50%);
  }
}
</style>
