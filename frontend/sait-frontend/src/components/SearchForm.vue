<template>
  <div class="calendar-container" ref="calendarRef">
    <div class="inputs">
      <div class="search-btn">
        <GuestsInput 
          v-model:count="guestsCount"
          :MIN_GUESTS="MIN_GUESTS"
          :MAX_GUESTS="MAX_GUESTS"
        />
      </div>
      <input 
        type="text" 
        :value="startDateText" 
        placeholder="Дата начала" 
        readonly 
        id="startDate"
        @click="toggleCalendar"
      >
      <input 
        type="text" 
        :value="endDateText" 
        placeholder="Дата окончания" 
        readonly 
        id="endDate"
        @click="toggleCalendar"
      >
      <button 
        id="findBtn" 
        @click="handleSearch"
        :disabled="isLoading || !isDateRangeValid"
      >
        <span v-if="!isLoading">Найти</span>
        <span v-else>Поиск...</span>
      </button>
    </div>
    <div class="calendars" :class="{ visible: showCalendar }" >
      <DateRangePicker
        v-model:startDate="startDate"
        v-model:endDate="endDate"
        v-model:error="searchError"
        @clear="fetchAllRoomsand" 
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onUnmounted } from 'vue';
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
      this.$emit('clire')
      return this.fetchAllRooms()
    }
  },  

  emits: ['search'],
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

    // // Закрытие календаря после выбора конечной даты
     watch(endDate, (newEndDate) => {
       if (newEndDate && startDate.value && showCalendar.value) {
         setTimeout(() => {
           showCalendar.value = false;
         }, 50);
       }
     });

    // Обработчик клавиши Esc
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

      if (!isInsideCalendar && !isCalendarInput && showCalendar.value) {
        showCalendar.value = false;
      }
    };

    // Добавляем/удаляем обработчики событий
    watch(showCalendar, (newVal) => {
      if (newVal) {
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('keydown', handleKeyDown);
      } else {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('keydown', handleKeyDown);
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
    };
  },
};
</script>
  
  <style scoped>

.search-btn{
    border-top: 1px solid #e0e0e0;
    border-bottom: 1px solid #e0e0e0;
    border-left: 1px solid #e0e0e0;
    border-radius: 32px 0 0 32px;
    width: 150px;
    background-color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.calendars {
    pointer-events: none;
    margin: 0 auto;
    position: absolute;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    transition: opacity 0.3s;
    opacity: 0;    
  }
  
  .calendars.visible {
    background: white;
    opacity: 1;
    pointer-events: painted;
  }



  .calendar-container {
    z-index: 10000;
    display: flex;
    justify-content: center;
    font-family: Arial, sans-serif;
    max-width: 701px;
    margin: 20px auto;
    
  }
  
  .inputs {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
  }
  
  .inputs input {
    padding: 15px 10px;
    color: #757587;
    width: 110px;
    text-align: center;
    border: none;
    font-size: 14px;
    cursor: pointer;
    border-top: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
    
  }
  input, 
input:active, 
input:focus-visible {
  outline: none;
  box-shadow: none;
  border-color: #ccc;
}
  
  #startDate {
    border-right: 1px dotted #ddd;
  }
  
  #findBtn {
    padding: 10px;
      outline: none;
  box-shadow: none;
    width: 80px;
    border-radius: 0 32px 32px 0; 
    border: none;
    background: #4c4cf7;
    color: white;
    cursor: pointer;
  }
  
  #findBtn:hover {
    background: #c6c4fd;
  }
  
  #findBtn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
    opacity: 0.7;
  }

  </style>