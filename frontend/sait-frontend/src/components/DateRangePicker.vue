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
          </div>
        </div>
      </div>
    </div>
    <div class="flex">
      <CalendarStatus 
      :start-date="startDate"
      :end-date="endDate"
      :occupied-dates="occupiedDates"
      :number-of-rooms="numberOfRooms"
      @error = 'ErorDate'
      />
    <button id="clearBtn" @click="$emit('clear')">Очистить</button>
    </div>
    
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import CalendarStatus from './CalendarStatus.vue';

export default {
  components: {
    CalendarStatus
  },
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
    handleClear: { // Принимаем метод через пропсы
      type: Function,
      required: true,
    },
    pricePeriods: { // Добавляем новый пропс с ценовыми периодами
      type: Array,
      default: () => []
    }
  },
  methods:{
    ErorDate(post){
      if (post) return post
      return false
    }
  },
  emits: ['update:startDate', 'update:endDate', 'clear'],
  setup(props, { emit }) {
    const currentYear = ref(new Date().getFullYear());
    const currentMonth = ref(new Date().getMonth());
    const hoverEndDate = ref(null);

    const months = [
      'Январь', 'Февраль', 'Март', 'Апрель', 
      'Май', 'Июнь', 'Июль', 'Август', 
      'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

    const calendars = computed(() => {
      return [0, 1].map(offset => {
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

const isDateOccupied = (date) => {
  if (!props.numberOfRooms || !date) return false;
  
  // Смещаем дату на 1 день назад для проверки занятости
  const checkDate = new Date(date);
  checkDate.setDate(date.getDate() - 1);
  const checkDateStr = formatDate(checkDate);
  
  // Также проверяем саму дату (без смещения)
  const currentDateStr = formatDate(date);
  
  // Дата считается занятой, если занята смещенная дата ИЛИ текущая дата
  const isShiftedOccupied = (props.occupiedDates[checkDateStr] || 0) >= props.numberOfRooms;
  const isCurrentOccupied = (props.occupiedDates[currentDateStr] || 0) >= props.numberOfRooms;
  
  return isShiftedOccupied || isCurrentOccupied;
};
    const selectDate = (date) => {
      if (!props.startDate || props.endDate) {
        emit('update:startDate', date);
        emit('update:endDate', null);
      } else if (date > props.startDate) {
        emit('update:endDate', date);
      } else {
        emit('update:startDate', date);
        emit('update:endDate', null);
      }
      hoverEndDate.value = null;
    };

    const handleHover = (date) => {
      if (props.startDate && !props.endDate && date >= props.startDate) {
        hoverEndDate.value = date;
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
  
  const date = cell.date.getTime();
  const isStart = date === props.startDate?.getTime();
  const isValidEnd = props.endDate 
    ? props.endDate >= props.startDate 
    : hoverEndDate.value >= props.startDate;
  const isEnd = (date === props.endDate?.getTime() && isValidEnd) 
    || (!props.endDate && date === hoverEndDate.value?.getTime() && isValidEnd);
  const inRange = props.startDate && props.endDate && 
                date > props.startDate.getTime() && 
                date < props.endDate.getTime();
  const inHoverRange = props.startDate && hoverEndDate.value && 
                     date > props.startDate.getTime() && 
                     date < hoverEndDate.value.getTime();
  const isDisabled = date < new Date().setHours(0,0,0,0) || 
                    isFutureLimit(cell.date.getFullYear(), cell.date.getMonth());
  
  // Используем смещенную проверку занятости
  const isOccupied = isDateOccupied(cell.date);
  const noPrice = !hasPriceForDate(cell.date);

  return {
    'selected': isStart || isEnd || inRange || inHoverRange,
    'start-date': isStart,
    'end-date': isEnd,
    'occupied': isOccupied && !isDisabled,
    'disabled': isDisabled || noPrice || isOccupied,
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
      calendars,
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

  

  .calendar-wrapper{
    width: 315px;
    color: black;
  }
  
  .flex{
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
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
  
  .navigation {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
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
  border-radius: 50%;
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
  background: rgba(255, 255, 255, 0);
}

.day.selected {
  background: #c6c4fd;
  color: white;
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

.day.start-date::before {
  position: absolute;
  content: " ";
  border-radius: 50%;
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
  border-radius: 50%;
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
</style>