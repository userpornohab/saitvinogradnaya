<template>
  <div v-if="error" class="error-message">
    {{ error }}
  </div>
  <div v-else class="selected-days-info">{{ selectedDaysInfo }}</div>
</template>

<script>
import { computed, watch } from 'vue';

export default {
  props: {
    startDate: Date,
    endDate: Date,
    occupiedDates: Object,
    numberOfRooms: Number,
  },
  
  setup(props, { emit }) {
    const getNightsDeclension = (days) => {
      const lastDigit = days % 10;
      const lastTwoDigits = days % 100;
      if (lastTwoDigits >= 11 && lastTwoDigits <= 14) return 'ночей';
      if (lastDigit === 1) return 'ночь';
      if (lastDigit >= 2 && lastDigit <= 4) return 'ночи';
      return 'ночей';
    };

    // Общая функция проверки сроков
    const checkStayDuration = (diffDays) => {
      if (diffDays < 3) return 'Минимальный срок бронирования - 3 ночи';
      if (diffDays > 90) return 'Максимальный срок бронирования - 90 ночей';
      return null;
    };

    const error = computed(() => {
      if (!props.startDate && !props.endDate) return null;
      
      const currentDate = new Date().setHours(0,0,0,0);
      const startTime = props.startDate?.getTime();
      
      // Проверка на прошедшие даты
      if (startTime < currentDate) return 'Выбранный период недоступен';
      
      // Проверка на занятость
      const isDateOccupied = (date) => {
        if (!props.numberOfRooms || !date) return false;
        const dateStr = date.toISOString().split('T')[0];
        return (props.occupiedDates[dateStr] || 0) >= props.numberOfRooms;
      };

      if (isDateOccupied(props.startDate)) return 'Выбранный период недоступен';

      // Проверка длительности проживания
      if (props.startDate && props.endDate) {
        const diffDays = Math.ceil((props.endDate - props.startDate) / (1000 * 60 * 60 * 24));
        const durationError = checkStayDuration(diffDays);
        if (durationError) return durationError;
      }

      // Проверка периода на занятость
      if (props.endDate) {
        let current = new Date(props.startDate);
        const end = new Date(props.endDate);
        
        while (current <= end) {
          if (isDateOccupied(current)) {
            return 'Период содержит занятые даты';
          } 
          current.setDate(current.getDate() + 1);
        }
      }
      
      return null;
    });

    watch(error, (newError) => {
      emit('error', newError !== null);
    });

    const selectedDaysInfo = computed(() => {
      if (!props.startDate) return 'Выберите начальную дату';
      if (!props.endDate) return 'Выберите дату окончания';
      
      const diffDays = Math.ceil((props.endDate - props.startDate) / (1000 * 60 * 60 * 24));
      return `Выбрано ${diffDays} ${getNightsDeclension(diffDays)}`;
    });

    return {
      error,
      selectedDaysInfo
    };
  }
};
</script>
  <style scoped>

    
.flex{
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
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

.selected-days-info{
  font-size: 14px;
  display: flex;
  align-items: center;
}

    </style>