<template>
  <div>
    <div ref="targetBlock"></div>
    <div class="booking-form" :class="fixedClass">
      <h6>Бронирование
      </h6>
      <div class="date-inputs"  @click.stop="showDatePicker = true">
        <div class="input-group">
          <div>Заезд</div>
          <input
            class="input-group-inp"
            type="text" 
            placeholder="Укажите дату" 
            :value="formattedStartDate"
            @input="updateStartDate($event.target.value)"
            readonly
            @focus="showDatePicker = true"
          >
        </div>

        <div class="input-group">
          <div>Выезд</div>
          <input
            class="input-group-inp"
            type="text" 
            placeholder="Укажите дату" 
            :value="formattedEndDate"
            @input="updateEndDate($event.target.value)"
            readonly
            @focus="showDatePicker = true"
          >
        </div>
      </div>
      <div  class="guests-input">
      <div style="font-size: 12px;">Гости</div>
      <GuestsInput 
        :count="guestsCount"
        :MAX_GUESTS="maxGuests"
        @update:count="handleGuestsUpdate"
        @error="handleGuestsError"
      />
      </div>
      
      
      <transition name="datepicker-fade">
        <div v-if="showDatePicker" class="datepicker-wrapper">
          <DateRangePicker
            :start-date="startDate"
            :end-date="endDate"
            :occupied-dates="occupiedDates"
            :number-of-rooms="numberOfRooms"
            @update:startDate="handleStartDateUpdate"
            @update:endDate="handleEndDateUpdate"
            @clear="handleClear"
            @error="handleDateError"
            :price-periods="pricePeriods"

          />
        </div>
      </transition>

      <div>
        <CalendarStatus 
        class="status"
          :start-date="startDate"
          :end-date="endDate"
          :occupied-dates="occupiedDates"
          :number-of-rooms="numberOfRooms"
          @error="handleDateError"
        />
      </div>

      <div v-if="showPrice" class="total-price">
        <div>
          Общая стоимость: <u>{{ formatPrice(totalPrice) }}</u> руб.
        </div>
      </div>

      <button 
        class="book-button"
        :disabled="!canBook"
        :class="{ disabled: !canBook}"
        :title="buttonTooltip"
        @click="handleBooking"
      >
        Забронировать
      </button>
      <div class="servis-mas">Пока вы ни за что не платите</div>
    </div>
  </div>
</template>

<script>
import GuestsInput from './GuestsInput.vue';
import DateRangePicker from './DateRangePicker.vue';
import CalendarStatus from './CalendarStatus.vue';

export default {
  name: 'BookingForm',
  components: {
    GuestsInput,
    DateRangePicker,
    CalendarStatus,
  },
  props: {
    guestsCount: {
    type: Number,
    default: 1
  },
    startDate: Date,
    endDate: Date,
    pricePeriods: {
      type: Array,
      default: () => []
    },
    bookings: {
      type: Array,
      default: () => []
    },
    numberOfRooms: {
      type: Number,
      default: 0
    },
    maxGuests: {
      type: Number,
      required: true
    },
  },
  emits: ['update:startDate', 'update:endDate', 'booking-change', 'booking-submit'],
  data() {
    return {
      showDatePicker: false,
      dateError: false,
      guestsError: false,
      errorMessage: '',
      isFixed: false,
    };
  },
  computed: {
    fixedClass() {
      return this.isFixed ? "fixed" : "absolute";
    },
    formattedStartDate() {
      return this.dateToISOString(this.startDate);
    },
    formattedEndDate() {
      return this.dateToISOString(this.endDate);
    },
    occupiedDates() {
      const occupied = {};
      this.bookings.forEach(booking => {
        const start = new Date(booking.check_in_date);
        const end = new Date(booking.check_out_date);
        let current = new Date(start);
        end.setDate(end.getDate() - 1);

        while (current < end) {
          const dateStr = current.toISOString().split('T')[0];
          occupied[dateStr] = (occupied[dateStr] || 0) + 1;
          current.setDate(current.getDate() + 1);
        }
      });
      return occupied;
    },
    totalPrice() {
      if (!this.startDate || !this.endDate || 
          this.startDate >= this.endDate || 
          this.guestsCount < 1) {
        return 0;
      }

      let total = 0;
      const start = new Date(this.startDate);
      const end = new Date(this.endDate);
      let current = new Date(start);

      // Перебираем каждый день бронирования
      while (current < end) {
        let bestPeriod = null;
        
        // Ищем лучший период для текущего дня
        for (const period of this.pricePeriods) {
          const periodStart = new Date(period.start_date);
          const periodEnd = new Date(period.end_date);
          
          // Проверяем что день входит в период
          if (current >= periodStart && current <= periodEnd) {
            // Проверяем подходит ли по количеству гостей
            if (period.number_of_guests >= this.guestsCount) {
              // Ищем период с минимальным подходящим количеством гостей
              if (!bestPeriod || period.number_of_guests < bestPeriod.number_of_guests) {
                bestPeriod = period;
              }
            }
          }
        }

        if (bestPeriod) {
          total += bestPeriod.price;
        } else {
          // Если не нашли подходящий период - сбрасываем сумму
          return 0;
        }

        current.setDate(current.getDate() + 1);
      }

      return total;
    },
    showPrice() {
      return this.totalPrice > 0 && !this.hasErrors && this.startDate && this.endDate;
    },
    hasErrors() {
          // if (this.dateError){
          //   this.$emit('update:startDate', null);
          //   this.$emit('update:endDate', null);
          // }
      return this.dateError || this.guestsError;
    },
    canBook() {
      return !this.hasErrors && this.startDate && this.endDate && this.guestsCount > 0;
    },
    buttonTooltip() {
      if (!this.startDate || !this.endDate) return 'Выберите даты заезда и выезда';
      if (this.guestsCount <= 0) return 'Укажите количество гостей';
      if (this.hasErrors) return 'Исправьте ошибки в форме';
      return 'Подтвердить бронирование';
    }
  },
  watch: {
    guestsCount(newVal) {
      if (Number.isNaN(newVal)) {
        this.$emit('update:guestsCount', 1);
      }
      this.emitBookingData();
    },
    startDate() {
      this.emitBookingData();
    },
    endDate() {
      this.emitBookingData();
    }
  },
  methods: {
    handleGuestsUpdate(count) {
    this.$emit('update:guestsCount', count);
  },
    handleScroll() {
      const blockPosition = this.$refs.targetBlock.getBoundingClientRect().top + window.scrollY;
      this.isFixed = window.scrollY >= blockPosition; // Меняем значение при прокрутке вниз
    },

    handleKeyPress: function(event) {
    if (event.key === 'Escape') {
      this.handleClear();
    }
  },
    handleDateError(hasError) {
      this.dateError = hasError;

    },
    handleGuestsError(hasError) {
      this.guestsError = hasError;
    },

    handleBooking() {
      if (this.canBook) {
        this.$emit('booking-submit', {
          startDate: this.startDate,
          endDate: this.endDate,
          guests: this.guestsCount
        });
      }
    },
    dateToISOString(date) {
      if (!date) return '';
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${day}.${month}.${year}`;
    },
    dateDiffInDays(a, b) {
      const utc1 = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate());
      const utc2 = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate());
      return Math.floor((utc2 - utc1) / (1000 * 60 * 60 * 24));
    },
    formatPrice(price) {
      return price.toLocaleString('ru-RU');
    },
    updateStartDate(value) {
      const newDate = value ? new Date(value) : null;
      this.$emit('update:startDate', newDate);
    },
    updateEndDate(value) {
      const newDate = value ? new Date(value) : null;
      this.$emit('update:endDate', newDate);
    },
    emitBookingData() {
      this.$emit('booking-change', {
        startDate: this.startDate,
        endDate: this.endDate,
        guestsCount: this.guestsCount
      });
    },
    handleStartDateUpdate(newDate) {
      this.$emit('update:startDate', newDate);
    },
    handleEndDateUpdate(newDate) {
      this.$emit('update:endDate', newDate);
      if (newDate && this.startDate && newDate > this.startDate) {
        this.showDatePicker = false;
      }
    },
    handleClear() {
      
      this.showDatePicker = false;
      this.$emit('update:startDate', null);
      this.$emit('update:endDate', null);
    },
    handleClickOutside(event) {
      if (!this.$el.contains(event.target)) {
        this.showDatePicker = false;
      }
    }
  },  
  async mounted() {
    window.addEventListener("scroll", this.handleScroll);
    document.addEventListener('click', this.handleClickOutside);
  window.addEventListener('keydown', (e) => this.handleKeyPress(e)); // Исправлено: привязка контекста

  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
    document.removeEventListener('click', this.handleClickOutside);
  window.removeEventListener('keydown', (e) => this.handleKeyPress(e)); // Аналогично

  }
};
</script>
<style scoped>
.booking-form {
  box-shadow: rgba(0, 0, 0, 0.12) 0px 6px 16px;
  box-sizing: border-box;
  margin-top: 20px;
  padding: 24px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #ffffff;
  max-width: 358px;
  
}

.absolute {
  position: relative;
}

.fixed {
  top: 0;
  position: fixed;
}


.date-inputs {
  display: flex;

  cursor: pointer;

}

h6{
  font-size: 20px;
  margin:  0  0  20px 0;
  width: 100%;
}

.guests-input{
  border: 1px solid rgb(66, 66, 66);
  border-radius: 0 0 8px 8px;
  padding: 10px;
  border-top: none;
    
  

}


.guests-container>.guests-controls{
  top:0
}

.status{
  margin: 10px  0  20px 0 ;
}

.guests-container{
  padding: 0;
  
}

.input-group-inp{
  width: 100%;
    outline: none;
  box-shadow: none;
  color: #757587;
  border: none
}


.date-inputs > .input-group:first-of-type{
  border-radius: 8px 0 0 0px;
  border-right: none;
}
.date-inputs > .input-group:last-of-type{
  border-radius:0 8px 0  0px;
}

.input-group {
  padding: 10px;
  border: 1px solid rgb(66, 66, 66);
  
}

.input-group>div{
  font-size: 12px;
}

label {
  font-size: 0.9em;
  margin-bottom: 5px;
  color: #666;
}



.datepicker-wrapper {
  
  position: absolute;
  z-index: 10000;
  width: 700px;
  top: 121px;

  right: 23px;
  background: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-radius: 8px;
  padding: 10px;
}


.datepicker-fade-enter-active,
.datepicker-fade-leave-active {
  transition: all 0.3s ease;
}

.datepicker-fade-enter-from,
.datepicker-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.error-message {
  margin-top: 15px;
  color: #ff4444;
  font-weight: bold;
  padding: 10px;
  background: #ffecec;
  border-radius: 5px;
  border: 1px solid #ffcccc;
}

.total-price {
  margin: 15px 0 20px 0 ;
  font-size: 1.1em;
  font-weight: bold;
  color: #4a4a4a;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
}

.book-button{
  width: 100%;
  height: 42px;
  border-radius: 8px; 
  border: none;
  background: #4c4cf7;
  color: white;
  cursor: pointer;
  transition: 0.1s linear;
}

  
.book-button:hover {

    background: #c6c4fd;
  }

.disabled{
    background: #9f9fa5;

}

.servis-mas{
  margin-top: 10px;
  width: 100%;
  text-align: center;
  color: rgb(122, 104, 104);
}

</style>