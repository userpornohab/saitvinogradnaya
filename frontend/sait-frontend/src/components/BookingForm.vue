<template>
  <div>
    <div ref="targetBlock"></div>
    <div class="booking-form" :class="fixedClass">
      <h6>Бронирование
      </h6>
      <div class="date-inputs"  @click.stop="showDatePicker = true">
        <div class="input-group">
          <div style="font-size: 12px; transform: translateY(6px);">Заезд</div>
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

        <div class="input-group input-group--end">
          <div style="font-size: 12px; transform: translateY(6px);">Выезд</div>
          <input
            class="input-group-inp"
            type="text" 
            placeholder="Укажите дату" 
            :value="formattedEndDate"
            @input="updateEndDate($event.target.value)"
            readonly
            @focus="showDatePicker = true"
          >
          <button
            v-if="startDate || endDate"
            type="button"
            class="input-clear"
            aria-label="Очистить даты"
            @click.stop="handleClear"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
      <div  class="guests-input">
      <div style="font-size: 12px; transform: translateY(6px);">Гости</div>
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
            @close="showDatePicker = false"
            @error="handleDateError"
            :price-periods="pricePeriods"
            :isMobile="isMobile"

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
  emits: ['update:startDate', 'update:endDate', 'update:guestsCount', 'booking-change', 'booking-submit', 'close'],
  data() {
    return {
      showDatePicker: false,
      dateError: false,
      guestsError: false,
      errorMessage: '',
      isFixed: false,
      isMobile: false,
    };
  },
  computed: {
    fixedClass() {
      // На мобильных всегда absolute, на десктопе - fixed при прокрутке
      return this.isMobile ? "absolute" : (this.isFixed ? "fixed" : "absolute");
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
  
  // Нормализуем время для корректного сравнения дат
  start.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);
  
  let current = new Date(start);

  while (current < end) {
    // Убрали неиспользуемую переменную currentDateStr
    
    // Ищем все подходящие периоды для текущей даты
    const suitablePeriods = this.pricePeriods.filter(period => {
      const periodStart = new Date(period.start_date);
      const periodEnd = new Date(period.end_date);
      
      // Нормализуем время периодов
      periodStart.setHours(0, 0, 0, 0);
      periodEnd.setHours(0, 0, 0, 0);
      
      return current >= periodStart && 
             current <= periodEnd && 
             period.number_of_guests >= this.guestsCount;
    });

    if (suitablePeriods.length === 0) {
      // Если нет подходящего периода для этой даты - возвращаем 0
      return 0;
    }

    // Находим период с минимальной подходящей ценой
    const bestPeriod = suitablePeriods.reduce((minPeriod, period) => {
      return !minPeriod || period.price < minPeriod.price ? period : minPeriod;
    }, null);

    total += bestPeriod.price;
        current.setDate(current.getDate() + 1);
      }

      return total;
    },
    showPrice() {
      return this.totalPrice > 0 && !this.hasErrors && this.startDate && this.endDate;
    },
    firstNightPrice() {
      // Цена за первые сутки (используется как предоплата)
      if (!this.startDate || !this.endDate || this.startDate >= this.endDate) return 0;
      const start = new Date(this.startDate); start.setHours(0, 0, 0, 0);
      const suitable = this.pricePeriods.filter(period => {
        const ps = new Date(period.start_date); ps.setHours(0, 0, 0, 0);
        const pe = new Date(period.end_date);   pe.setHours(0, 0, 0, 0);
        return start >= ps && start <= pe && period.number_of_guests >= this.guestsCount;
      });
      if (!suitable.length) return 0;
      return suitable.reduce((min, p) => (!min || p.price < min.price ? p : min), null).price;
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
    handleGuestsUpdate(newCount) {
      this.$emit('update:guestsCount', newCount);
    },
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
      // Если это мобильное устройство, принудительно отключаем фиксацию
      if (this.isMobile) {
        this.isFixed = false;
      } else {
        // На десктопе запускаем проверку позиции при скролле
        this.handleScroll();
      }
    },
    
    handleScroll() {
      // Если мобильное устройство - не применяем фиксацию
      if (this.isMobile) {
        this.isFixed = false;
        return;
      }

      // Учитываем высоту фиксированной шапки навигации, чтобы форма не заезжала под неё
      const nav = document.querySelector('.main-nav');
      const navHeight = nav ? nav.offsetHeight : 0;
      const blockPosition = this.$refs.targetBlock.getBoundingClientRect().top + window.scrollY;
      this.isFixed = window.scrollY + navHeight >= blockPosition;
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
          guests: this.guestsCount,
          totalPrice: this.totalPrice,
          prepayment: this.firstNightPrice,
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
    this.checkMobile();
    window.addEventListener("scroll", this.handleScroll);
    window.addEventListener("resize", this.checkMobile);
    document.addEventListener('click', this.handleClickOutside);
    window.addEventListener('keydown', (e) => this.handleKeyPress(e));
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
    window.removeEventListener("resize", this.checkMobile);
    document.removeEventListener('click', this.handleClickOutside);
    window.removeEventListener('keydown', (e) => this.handleKeyPress(e));
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
  
}

.absolute {
  position: relative;
}

.fixed {
  top: var(--nav-height, 64px);
  position: fixed;
  max-width: 352px;
}

/* Мобильная версия - отключаем фиксацию */
@media (max-width: 768px) {
  .booking-form {
    position: relative !important;
    top: auto !important;
  }
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
  padding: 4px 8px;
  border-top: none;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.guests-input :deep(.guests-container){
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  position: static !important;
  padding: 0 !important;
  border: none !important;
  width: 100%;
}

.guests-input :deep(.guests-container > input),
.guests-input :deep(#guestsInput){
  flex: 1 1 auto;
  min-width: 0;
  padding: 0 !important;
  width: auto !important;
  text-align: left;
}

.guests-input :deep(.guests-controls){
  position: static !important;
  transform: translateY(-8PX) !important;
  top: auto !important;
  right: auto !important;
  gap: 4px;
  flex-shrink: 0;
}

.status{
  margin: 10px  0  20px 0 ;
}

.input-group-inp{
  font-size: 12px;
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
  padding: 4px 8px;
  border: 1px solid rgb(66, 66, 66);
  position: relative;
}

.input-group--end { padding-right: 28px; }

.input-clear {
  position: absolute;
  top: 50%;
  right: 6px;
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

.input-clear:hover {
  opacity: 1;
  color: #222;
  background: rgba(0, 0, 0, 0.06);
}
.label {
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

/* Мобильная адаптация для календаря */
@media (max-width: 768px) {
  .datepicker-wrapper {
    width: 100vw;
    left: 50%;
    right: auto;
    transform: translateX(-50%);
    top: 50%;
    transform: translate(-50%, -50%);
    position: fixed;
    height: 100vh;
    overflow-y: auto;
  }
}
</style>