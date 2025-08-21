<template>
  <div>
    <div class="navigation">
      <button 
        class="nav-btn-start" 
        @click="changeMonth(-1)" 
        :class="{ visible: canShowPrev }"
      >
        <img class="svg_prev" src="@/assets/icons/arrow-left.svg" alt="Назад">
      </button>
      
      <div class="selectors">
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
      <button 
        class="nav-btn-end" 
        @click="changeMonth(1)" 
        :class="{ nevisible: !canShowNext }"
      >
        <img class="svg_nex" src="@/assets/icons/arrow-right.svg" alt="Вперед">
      </button>
    </div>

    <div class="calendar-grid">
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
            @click="selectDate(cell.date)"
            @mouseover="handleHover(cell.date)"
          >
            {{ cell.day }}
            <div 
            v-if="cell.date && numberOfRooms > 0" 
            class="availability-info"
          >
            <div class="availability-count">
              {{ availableRooms(cell.date) }}/{{ numberOfRooms }}
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>
    <div class="flex">
      <button id="clearBtn" @click="$emit('clear')">Очистить</button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

const months = [
  'Январь', 'Февраль', 'Март', 'Апрель', 
  'Май', 'Июнь', 'Июль', 'Август', 
  'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

export default {
  props: {
    startDate: Date,
    endDate: Date,
    occupiedDates: {
      type: Object,
      default: () => ({}),
    },
    numberOfRooms: {
      type: Number,
      default: 0,
    },
    handleClear: {
      type: Function,
      required: true,
    },
    pricePeriods: { // Добавляем новый пропс с ценовыми периодами
      type: Array,
      default: () => []
    }
  },
  
  emits: ['update:startDate', 'update:endDate', 'clear'],

  setup(props, { emit }) {
    const currentYear = ref(new Date().getFullYear());
    const currentMonth = ref(new Date().getMonth());
    const hoverEndDate = ref(null);
    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

    const bookingPeriods = computed(() => {
      const periods = [];
      const dates = Object.keys(props.occupiedDates)
        .map(d => {
          const [year, month, day] = d.split('-');
          return new Date(year, month - 1, day);
        })
        .sort((a, b) => a - b);

      let currentPeriod = null;
      dates.forEach(date => {
        const normalizedDate = new Date(date);
        normalizedDate.setHours(0,0,0,0);

        if (!currentPeriod) {
          currentPeriod = { 
            start: new Date(normalizedDate), 
            end: new Date(normalizedDate)
          };
          return;
        }

        

        const prevEnd = new Date(currentPeriod.end);
        prevEnd.setDate(prevEnd.getDate() + 1);
        prevEnd.setHours(0,0,0,0);

        if (normalizedDate.getTime() === prevEnd.getTime()) {
          currentPeriod.end = new Date(normalizedDate);
        } else {
          periods.push(currentPeriod);
          currentPeriod = { 
            start: new Date(normalizedDate), 
            end: new Date(normalizedDate)
          };
        }
      });

      if (currentPeriod) periods.push(currentPeriod);
      return periods;
    });

    const bookingStartDates = computed(() => 
      new Set(bookingPeriods.value.map(p => formatDate(p.start)))
    );

    const bookingEndDates = computed(() => 
      new Set(
        bookingPeriods.value.map(p => {
          const endDate = new Date(p.end);
          endDate.setDate(endDate.getDate() + 1); // Корректировка конечной даты
          return formatDate(endDate);
        })
      )
    );

    const generateCalendarDays = (date) => {
      const moscowDate = new Date(date.toLocaleString('en-US', { timeZone: 'Europe/Moscow' }));
      const year = moscowDate.getFullYear();
      const month = moscowDate.getMonth();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstDay = new Date(year, month, 1).getDay();
      const emptyCells = (firstDay + 6) % 7;
      const days = [];

      for (let i = 0; i < emptyCells; i++) {
        days.push({ day: '', key: `empty-${i}` });
      }

      for (let day = 1; day <= daysInMonth; day++) {
        const dateObj = new Date(year, month, day);
        days.push({
          day,
          date: dateObj,
          key: `${year}-${month}-${day}`
        });
      }

      return days;
    };

    const isPastMonth = (year, month) => {
      const current = new Date();
      return year < current.getFullYear() || 
            (year === current.getFullYear() && month < current.getMonth());
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

    const availableRooms = (date) => {
  if (!date || !props.numberOfRooms) return 0;
  
  const dateStr = formatDate(date);
  let occupied = props.occupiedDates[dateStr] || 0;
  
  // Получаем оригинальную дату без коррекции
  const originalDate = new Date(date);
  originalDate.setDate(originalDate.getDate() - 1);
  const originalDateStr = formatDate(originalDate);
  
  // Проверяем, является ли текущая дата:
  const isStart = bookingStartDates.value.has(dateStr); // Началом периода
  const isEnd = bookingEndDates.value.has(dateStr);     // Конец (уже увеличенный)
  const wasEnd = bookingPeriods.value.some(p =>        // Оригинальный конец
    formatDate(p.end) === originalDateStr
  );

  // Логика коррекции занятости
  if (isStart || wasEnd) {
    occupied = Math.max(0, occupied - 0.5);
  }

  // Для скорректированной конечной даты
  if (isEnd) {
    occupied = Math.max(0, (props.occupiedDates[originalDateStr] || 0) - 0.5);
  }

  return props.numberOfRooms - occupied;
};

    const selectDate = (date) => {
      const moscowDate = new Date(date.toLocaleString('en-US', { timeZone: 'Europe/Moscow' }));
      moscowDate.setHours(0,0,0,0);

      if (!props.startDate || props.endDate) {
        emit('update:startDate', moscowDate);
        emit('update:endDate', null);
      } else if (moscowDate > props.startDate) {
        emit('update:endDate', moscowDate);
      } else {
        emit('update:startDate', moscowDate);
        emit('update:endDate', null);
      }
      hoverEndDate.value = null;
    };

    const handleHover = (date) => {
      if (props.startDate && !props.endDate && date >= props.startDate) {
        hoverEndDate.value = new Date(date.toLocaleString('en-US', { timeZone: 'Europe/Moscow' }));
      }
    };

    const formatDate = (date) => {
      return date.toLocaleDateString('en-CA', {
        timeZone: 'Europe/Moscow',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    };

        const hasPriceForDate = (date) => {
          if (!props.pricePeriods || props.pricePeriods.length === 0) return true;
          
          return props.pricePeriods.some(period => {
            const start = new Date(period.start_date);
            const end = new Date(period.end_date);
            const dateObj = new Date(date);
            return formatDate(dateObj) >= formatDate(start) && formatDate(dateObj) <= formatDate(end);
          });
        };

    const getDayClasses = (cell) => {
      if (!cell.date) return 'empty';
      
      const currentDate = new Date(cell.date);
      currentDate.setHours(0,0,0,0);
      const startDate = props.startDate ? new Date(props.startDate.setHours(0,0,0,0)) : null;
      const endDate = props.endDate ? new Date(props.endDate.setHours(0,0,0,0)) : null;
      
      const isStart = currentDate.getTime() === startDate?.getTime();
      const isValidEnd = endDate 
        ? endDate >= startDate 
        : hoverEndDate.value >= startDate;
      const isEnd = (currentDate.getTime() === endDate?.getTime() && isValidEnd) 
        || (!endDate && currentDate.getTime() === hoverEndDate.value?.getTime() && isValidEnd);
      
      const inRange = startDate && endDate && 
                    currentDate > startDate && 
                    currentDate < endDate;
      const inHoverRange = startDate && hoverEndDate.value && 
                         currentDate > startDate && 
                         currentDate < hoverEndDate.value;
      
      const isDisabled = currentDate < new Date().setHours(0,0,0,0) || 
                        isFutureLimit(currentDate.getFullYear(), currentDate.getMonth());
      
      const currentDateStr = formatDate(currentDate);
      const isBookingStart = bookingStartDates.value.has(currentDateStr);
      const isBookingEnd = bookingEndDates.value.has(currentDateStr);
      
      let available = availableRooms(currentDate);
      if (isBookingStart || isBookingEnd) {
        available += 0.5;
      }

      // Проверяем наличие цены для даты
      const noPrice = !hasPriceForDate(currentDate);

      return {
        'start-date': isStart,
        'end-date': isEnd,
        'disabled': isDisabled || noPrice, // Добавляем класс disabled если нет цены
        'full-occupied': available <= 0 && props.numberOfRooms > 0,
        'partially-occupied': available > 0 && available < props.numberOfRooms,
        'booking-period-start': isBookingStart,
        'booking-period-end': isBookingEnd,
        'selected': isStart || isEnd || inRange || inHoverRange,
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

    return {
      currentYear,
      currentMonth,
      calendars: computed(() => {
        return [0, 1, 2].map(offset => {
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
      }),
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
      isMonthDisabled,
      availableRooms,
      bookingPeriods,
      bookingStartDates,
      bookingEndDates,
      formatDate,
      hasPriceForDate, // Экспортируем функцию
    };
  }
};
</script>


    <style scoped>



    .calendar-wrapper{
      width: 315px;
    }
    
    .flex{
      display: flex;
      justify-content: flex-end;
      padding: 0 20px;
    }
    
    
    .nav-btn-start.visible{
      background: #ffffff;
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
      pointer-events: none;
      cursor: not-allowed;
      color: rgb(0, 0, 0);
      opacity: 0.5;
    }
    
    .navigation {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
    }
    
    .nav-btn-start {
      box-sizing: border-box;
      padding: 4px;
      align-items: center;
      display: flex;    
      justify-content: center;
      background: white;
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
      background: #ffffff;
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
      padding: 3px 6px;
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
  
  .day:not(.disabled):not(.selected):hover {
    background-color: #ffffff;
    cursor: pointer;
    border: 1px solid #000000;
    border-radius: 4px;
    
    
  }
  
  
  .month-title {
    text-align: center;
    font-weight: bold;
    margin-bottom: 15px;
    color: #333;
  }
  
  .calendar {
    display: grid;
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
    box-sizing: border-box;
    width: 45px;
    height: 45px;
    text-align: center;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: center;
    z-index: 1;
  }
  
  .day.selected {
    background: #c6c4fd;
    color: white;
    z-index: 2;
    position: relative;
  }
  
  .day.start-date {
    background: linear-gradient(to right, #ffffff, #ffffff, #c6c4fd);
    color: white;
    z-index: 2;
    position: relative;
  }
  
  .day.end-date {
    color: white;
    z-index: 2;
    position: relative;
    background: linear-gradient(to right, #c6c4fd, #ffffff, #ffffff);
  }
  
  .day.start-date::before {
    position: absolute;
    content: " ";
    border-radius: 4px 0 0 4px ;
    top: 0;
    z-index: -1;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to left, #752424, #4c4cf7);
  }
  
  .day.end-date::before {
    position: absolute;
    content: " ";
    border-radius: 0 4px 4px 0 ;
    top: 0;
    z-index: -1;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to right, #752424, #4c4cf7);
  }
  
  
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
  
  .disabled {
    opacity: 0.3;
    pointer-events: none;
  }
  
  .empty {
    pointer-events: none;
  }
  .day.full {
  background-color: #ff4444;
  color: white;
}

.partially-occupied{
  background-color: #44ff737e;
}

.full-occupied{
  background-color: #ff444417;
}

.special-next-day {
  background-color: #e6f7ff !important;
  border: 2px solid #1890ff !important;
  position: relative;
}





/* Переопределяем фоны с !important */
.booking-period-start {
  background: linear-gradient(135deg, #fff 50%, #44ff737e 50%) ;
}

.booking-period-end {
  background: linear-gradient(-45deg, #fff 50%, #44ff737e 50%) ;
  
}



/* Исправляем наслоение с .day */
.day.booking-period-start,
.day.booking-period-end {
  background-size: cover !important;
  background-position: center !important;}
  

  </style>

