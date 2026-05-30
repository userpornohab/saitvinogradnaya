<template>
  <div class="booking-stats">

    <div class="stats-container">
      <AdminHeader />
      <!-- Фильтры и выбор периода -->
      <div class="filters-card">
        <div class="filters-row">
          <!-- Быстрый выбор периода -->
          <div class="period-selector">
            <label class="filter-label">Период:</label>
            <div class="period-buttons">
              <button
                v-for="period in periodOptions"
                :key="period.value"
                class="period-btn"
                :class="{ 'period-btn--active': selectedPeriod === period.value }"
                @click="selectPeriod(period.value)"
              >
                {{ period.label }}
              </button>
            </div>
          </div>

          <!-- Произвольные даты -->
          <div class="date-inputs" v-if="selectedPeriod === 'custom'">
            <div class="date-group">
              <label class="filter-label">С:</label>
              <input type="date" v-model="customStartDate" @change="fetchStatistics" class="form-input" />
            </div>
            <div class="date-group">
              <label class="filter-label">По:</label>
              <input type="date" v-model="customEndDate" @change="fetchStatistics" class="form-input" />
            </div>
          </div>

          <!-- Выбор комнаты -->
          <div class="room-filter">
            <label class="filter-label">Комната:</label>
            <select v-model="selectedRoomId" @change="fetchStatistics" class="form-input">
              <option value="all">Все номера</option>
              <option v-for="room in rooms" :key="room.id" :value="room.id">
                {{ room.title }}
              </option>
            </select>
          </div>

          <!-- Обновить -->
          <button class="btn btn--primary" @click="fetchStatistics" :disabled="loading">
            {{ loading ? 'Загрузка...' : 'Обновить' }}
          </button>
        </div>
      </div>

      <section class="stats-section" v-if="statistics">
        <div class="stats-section-header">
          <h2 class="stats-section-title">Данные о бронированиях</h2>
          <p class="stats-section-subtitle">Доход, загрузка, гости и разрез по номерам за выбранный период.</p>
        </div>

        <!-- Основные карточки статистики -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-card-icon">📊</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ statistics.statistics.total_bookings }}</div>
              <div class="stat-card-label">Всего броней</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-icon">💰</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ formatCurrency(statistics.statistics.total_income) }}</div>
              <div class="stat-card-label">Общий доход</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-icon">👥</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ statistics.statistics.total_guests }}</div>
              <div class="stat-card-label">Всего гостей</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-icon">📅</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ statistics.statistics.avg_duration || 0 }}</div>
              <div class="stat-card-label">Среднее пребывание (ночей)</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-icon">%</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ statistics.statistics.occupancy_rate || 0 }}%</div>
              <div class="stat-card-label">Загрузка номерного фонда</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-icon">₽</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ formatCurrency(statistics.statistics.avg_check) }}</div>
              <div class="stat-card-label">Средний чек</div>
            </div>
          </div>
        </div>

        <!-- Информация о периоде -->
        <div class="period-info">
          <p><strong>Период:</strong> {{ formatDate(statistics.period.start_date) }} — {{ formatDate(statistics.period.end_date) }}</p>
          <p v-if="statistics.filter.room_title"><strong>Фильтр:</strong> {{ statistics.filter.room_title }}</p>
          <p v-if="statistics.previous_period">
            <strong>К прошлому периоду:</strong>
            броней {{ formatChange(statistics.previous_period.changes.bookings_percent) }},
            доход {{ formatChange(statistics.previous_period.changes.income_percent) }},
            загрузка {{ formatChange(statistics.previous_period.changes.occupancy_percent) }}
          </p>
        </div>

        <!-- Графики по номерам (только когда выбраны ВСЕ номера) -->
        <div class="charts-grid" v-if="statistics.monthly_income?.length || statistics.monthly_occupancy?.length || statistics.room_statistics?.length > 1">
          <div class="chart-card" v-if="statistics.monthly_income?.length">
            <h3 class="chart-title">Доход по месяцам</h3>
            <ApexChartComponent
              :key="'monthly-' + customStartDate + '-' + customEndDate"
              type="line"
              height="300"
              width="100%"
              :options="monthlyIncomeChartOptions"
              :series="monthlyIncomeChartSeries"
            />
          </div>

          <div class="chart-card" v-if="statistics.monthly_occupancy?.length">
            <h3 class="chart-title">Загрузка по месяцам</h3>
            <ApexChartComponent
              :key="'occupancy-' + customStartDate + '-' + customEndDate + '-' + selectedRoomId"
              type="line"
              height="300"
              width="100%"
              :options="monthlyOccupancyChartOptions"
              :series="monthlyOccupancyChartSeries"
            />
          </div>

          <!-- График бронирований по номерам -->
          <div class="chart-card" v-if="statistics.room_statistics?.length > 1">
            <h3 class="chart-title">Бронирования по номерам</h3>
            <ApexChartComponent
              :key="'bookings-' + customStartDate + '-' + customEndDate"
              type="bar"
              height="300"
              width="100%"
              :options="bookingsChartOptions"
              :series="bookingsChartSeries"
            />
          </div>

          <!-- График дохода по номерам -->
          <div class="chart-card" v-if="statistics.room_statistics?.length > 1">
            <h3 class="chart-title">Доход по номерам</h3>
            <ApexChartComponent
              :key="'income-' + customStartDate + '-' + customEndDate"
              type="bar"
              height="300"
              width="100%"
              :options="incomeChartOptions"
              :series="incomeChartSeries"
            />
          </div>
        </div>

        <!-- Статистика по номерам -->
        <div class="room-stats" v-if="statistics.room_statistics?.length">
          <h3 class="room-stats-title">Статистика по номерам</h3>
          <div class="room-stats-grid">
            <div v-for="roomStat in statistics.room_statistics" :key="roomStat.room_id" class="room-stat-card">
              <h4 class="room-stat-title">{{ roomStat.room_title }}</h4>
              <div class="room-stat-details">
                <div class="room-stat-item">
                  <span class="room-stat-label">Броней:</span>
                  <span class="room-stat-value">{{ roomStat.booking_count }}</span>
                </div>
                <div class="room-stat-item">
                  <span class="room-stat-label">Доход:</span>
                  <span class="room-stat-value">{{ formatCurrency(roomStat.total_income) }}</span>
                </div>
                <div class="room-stat-item">
                  <span class="room-stat-label">Гостей:</span>
                  <span class="room-stat-value">{{ roomStat.total_guests }}</span>
                </div>
                <div class="room-stat-item">
                  <span class="room-stat-label">Загрузка:</span>
                  <span class="room-stat-value">{{ roomStat.occupancy_rate || 0 }}%</span>
                </div>
                <div class="room-stat-item">
                  <span class="room-stat-label">Ночей:</span>
                  <span class="room-stat-value">{{ roomStat.total_nights || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="stats-section stats-section--clicks" v-if="analytics">
        <div class="stats-section-header">
          <h2 class="stats-section-title">Статистика кликов</h2>
          <p class="stats-section-subtitle">Интерес к номерам и действия гостей на сайте.</p>
        </div>

        <div class="stats-cards">
          <div class="stat-card stat-card--analytics">
            <div class="stat-card-icon">👆</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ analytics.totals.room_clicks }}</div>
              <div class="stat-card-label">Клики по номерам</div>
            </div>
          </div>

          <div class="stat-card stat-card--analytics">
            <div class="stat-card-icon">✓</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ analytics.totals.booking_clicks }}</div>
              <div class="stat-card-label">Клики «Забронировать»</div>
            </div>
          </div>

          <div class="stat-card stat-card--analytics">
            <div class="stat-card-icon">☎</div>
            <div class="stat-card-content">
              <div class="stat-card-value">{{ analytics.totals.phone_clicks }}</div>
              <div class="stat-card-label">Клики «Позвонить»</div>
            </div>
          </div>
        </div>

        <div class="charts-grid" v-if="analytics.daily?.length">
          <div class="chart-card">
            <h3 class="chart-title">Клики по дням</h3>
            <ApexChartComponent
              :key="'clicks-daily-' + customStartDate + '-' + customEndDate + '-' + selectedRoomId"
              type="line"
              height="300"
              width="100%"
              :options="clicksDailyChartOptions"
              :series="clicksDailyChartSeries"
            />
          </div>

          <div class="chart-card" v-if="analytics.room_statistics?.length">
            <h3 class="chart-title">Клики по номерам</h3>
            <ApexChartComponent
              :key="'clicks-rooms-' + customStartDate + '-' + customEndDate"
              type="bar"
              height="300"
              width="100%"
              :options="roomClicksChartOptions"
              :series="roomClicksChartSeries"
            />
          </div>
        </div>

        <div class="room-stats" v-if="analytics.room_statistics?.length">
          <h3 class="room-stats-title">Клики по каждому номеру</h3>
          <div class="room-stats-grid">
            <div v-for="roomStat in analytics.room_statistics" :key="'clicks-' + roomStat.room_id" class="room-stat-card">
              <h4 class="room-stat-title">{{ roomStat.room_title }}</h4>
              <div class="room-stat-details">
                <div class="room-stat-item">
                  <span class="room-stat-label">Карточка номера:</span>
                  <span class="room-stat-value">{{ roomStat.room_clicks }}</span>
                </div>
                <div class="room-stat-item">
                  <span class="room-stat-label">Забронировать:</span>
                  <span class="room-stat-value">{{ roomStat.booking_clicks }}</span>
                </div>
                <div class="room-stat-item">
                  <span class="room-stat-label">Позвонить:</span>
                  <span class="room-stat-value">{{ roomStat.phone_clicks }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Загрузка -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Загрузка статистики...</p>
      </div>

      <!-- Нет данных -->
      <div v-if="!loading && !statistics && !error" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
        <p>Выберите период для отображения статистики</p>
      </div>

      <!-- Ошибка -->
      <div v-if="error" class="error-state">
        <p>Ошибка: {{ error }}</p>
        <button class="btn btn--primary" @click="fetchStatistics">Попробовать снова</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/api';
import AdminHeader from './AdminHeader.vue';

export default {
  name: 'BookingStatistics',
  components: { AdminHeader },
  data() {
    return {
      selectedPeriod: 'week',
      customStartDate: '',
      customEndDate: '',
      selectedRoomId: 'all',
      rooms: [],
      statistics: null,
      analytics: null,
      loading: false,
      error: null,
      periodOptions: [
        { value: 'week', label: 'Неделя' },
        { value: 'month', label: 'Месяц' },
        { value: 'quarter', label: 'Квартал' },
        { value: 'year', label: 'Год' },
        { value: 'custom', label: 'Произвольно' },
      ]
    }
  },
  computed: {
    // График бронирований по номерам (столбчатая диаграмма)
    bookingsChartOptions() {
      const roomStats = this.statistics?.room_statistics || [];
      const categories = roomStats.map(r => r.room_title);
      return {
        chart: { toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
        colors: ['#FF5A5F'],
        plotOptions: { bar: { borderRadius: 6, columnWidth: '60%', horizontal: false } },
        xaxis: { categories: categories.length ? categories : ['Нет данных'], axisBorder: { show: false } },
        yaxis: { labels: { formatter: val => Math.round(val) } },
        grid: { borderColor: '#f0f0f0' },
        dataLabels: { enabled: false },
      };
    },
    bookingsChartSeries() {
      const roomStats = this.statistics?.room_statistics || [];
      return [{
        name: 'Бронирований',
        data: roomStats.map(r => r.booking_count)
      }];
    },
    // График дохода по номерам (столбчатая диаграмма)
    incomeChartOptions() {
      const roomStats = this.statistics?.room_statistics || [];
      const categories = roomStats.map(r => r.room_title);
      return {
        chart: { toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
        colors: ['#00A699'],
        plotOptions: { bar: { borderRadius: 6, columnWidth: '60%' } },
        xaxis: { categories: categories.length ? categories : ['Нет данных'], axisBorder: { show: false } },
        yaxis: { labels: { formatter: val => `${Math.round(val / 1000)}к ₽` } },
        grid: { borderColor: '#f0f0f0' },
        dataLabels: { enabled: false },
        tooltip: { y: { formatter: val => `${val.toLocaleString('ru-RU')} ₽` } },
      };
    },
    incomeChartSeries() {
      const roomStats = this.statistics?.room_statistics || [];
      return [{
        name: 'Доход',
        data: roomStats.map(r => r.total_income)
      }];
    },
    monthlyIncomeChartOptions() {
      const months = this.statistics?.monthly_income || [];
      return {
        chart: { toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
        colors: ['#4c4cf7'],
        stroke: { curve: 'smooth', width: 3 },
        markers: { size: 4 },
        xaxis: { categories: months.map(item => this.formatMonthLabel(item.month)), axisBorder: { show: false } },
        yaxis: {
          min: 0,
          forceNiceScale: true,
          labels: { formatter: val => `${Math.round(val / 1000)}к ₽` }
        },
        grid: { borderColor: '#f0f0f0' },
        dataLabels: { enabled: false },
        tooltip: { y: { formatter: val => `${val.toLocaleString('ru-RU')} ₽` } },
      };
    },
    monthlyIncomeChartSeries() {
      const months = this.statistics?.monthly_income || [];
      return [{
        name: 'Доход',
        data: months.map(item => item.income)
      }];
    },
    monthlyOccupancyChartOptions() {
      const months = this.statistics?.monthly_occupancy || [];
      return {
        chart: { toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
        colors: ['#6f6af8'],
        stroke: { curve: 'smooth', width: 3 },
        markers: { size: 4 },
        xaxis: { categories: months.map(item => this.formatMonthLabel(item.month)), axisBorder: { show: false } },
        yaxis: {
          min: 0,
          max: 100,
          labels: { formatter: val => `${Math.round(val)}%` }
        },
        grid: { borderColor: '#f0f0f0' },
        dataLabels: { enabled: false },
        tooltip: {
          y: { formatter: val => `${val}% загрузки` }
        },
      };
    },
    monthlyOccupancyChartSeries() {
      const months = this.statistics?.monthly_occupancy || [];
      return [{
        name: 'Загрузка',
        data: months.map(item => item.occupancy_rate)
      }];
    },
    clicksDailyChartOptions() {
      const days = this.analytics?.daily || [];
      return {
        chart: { toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
        colors: ['#4c4cf7', '#B63A47', '#3F7D5B'],
        stroke: { curve: 'smooth', width: 3 },
        markers: { size: 3 },
        xaxis: { categories: days.map(item => this.formatShortDate(item.date)), axisBorder: { show: false } },
        yaxis: {
          min: 0,
          forceNiceScale: true,
          labels: { formatter: val => Math.round(val) }
        },
        grid: { borderColor: '#f0f0f0' },
        dataLabels: { enabled: false },
      };
    },
    clicksDailyChartSeries() {
      const days = this.analytics?.daily || [];
      return [
        { name: 'Номера', data: days.map(item => item.room_click) },
        { name: 'Забронировать', data: days.map(item => item.booking_click) },
        { name: 'Позвонить', data: days.map(item => item.phone_click) },
      ];
    },
    roomClicksChartOptions() {
      const roomStats = this.analytics?.room_statistics || [];
      return {
        chart: { toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
        colors: ['#4c4cf7', '#B63A47'],
        plotOptions: { bar: { borderRadius: 6, columnWidth: '60%' } },
        xaxis: { categories: roomStats.map(room => room.room_title), axisBorder: { show: false } },
        yaxis: { min: 0, labels: { formatter: val => Math.round(val) } },
        grid: { borderColor: '#f0f0f0' },
        dataLabels: { enabled: false },
      };
    },
    roomClicksChartSeries() {
      const roomStats = this.analytics?.room_statistics || [];
      return [
        { name: 'Клики по номеру', data: roomStats.map(room => room.room_clicks) },
        { name: 'Забронировать', data: roomStats.map(room => room.booking_clicks) },
      ];
    },
  },
  mounted() {
    this.setDefaultDates();
    this.fetchRooms();
    this.fetchStatistics();
  },
  methods: {
    selectPeriod(period) {
      this.selectedPeriod = period;
      this.setDefaultDates();
      this.fetchStatistics();
    },
    setDefaultDates() {
      const now = new Date();
      let startDate;

      switch (this.selectedPeriod) {
        case 'week':
          startDate = new Date(now);
          startDate.setDate(startDate.getDate() - 7);
          break;
        case 'month':
          startDate = new Date(now);
          startDate.setMonth(startDate.getMonth() - 1);
          break;
        case 'quarter':
          startDate = new Date(now);
          startDate.setMonth(startDate.getMonth() - 3);
          break;
        case 'year':
          startDate = new Date(now);
          startDate.setFullYear(startDate.getFullYear() - 1);
          break;
        default:
          startDate = new Date(now);
          startDate.setDate(startDate.getDate() - 30);
      }

      this.customStartDate = this.formatDateForInput(startDate);
      this.customEndDate = this.formatDateForInput(now);
    },
    async fetchRooms() {
      try {
        const response = await api.get('/rooms/admin/');
        this.rooms = response.data;
      } catch (error) {
        console.error('Ошибка загрузки списка комнат:', error);
      }
    },
    async fetchStatistics() {
      if (!this.customStartDate || !this.customEndDate) return;

      this.loading = true;
      this.error = null;

      try {
        const params = {
          start_date: this.customStartDate,
          end_date: this.customEndDate
        };

        if (this.selectedRoomId !== 'all') {
          params.room_id = parseInt(this.selectedRoomId);
        }

        const [bookingResponse, analyticsResponse] = await Promise.all([
          api.get('/bookings/booking-stats', { params }),
          api.get('/analytics/stats', { params })
        ]);
        this.statistics = bookingResponse.data;
        this.analytics = analyticsResponse.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка загрузки статистики';
        console.error('Ошибка загрузки статистики:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    },
    formatDateForInput(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    formatCurrency(amount) {
      if (!amount && amount !== 0) return '0 ₽';
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(amount);
    },
    formatChange(value) {
      if (value === null || value === undefined) return 'нет базы';
      const sign = value > 0 ? '+' : '';
      return `${sign}${value}%`;
    },
    formatMonthLabel(month) {
      if (!month) return '';
      const [year, monthIndex] = month.split('-').map(Number);
      return new Date(year, monthIndex - 1, 1).toLocaleDateString('ru-RU', {
        month: 'short',
        year: '2-digit'
      });
    },
    formatShortDate(dateString) {
      if (!dateString) return '';
      const [year, month, day] = dateString.split('-').map(Number);
      return new Date(year, month - 1, day).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit'
      });
    }
  }
}
</script>

<style scoped>
.booking-stats {
  min-height: 100vh;
  background: var(--color-gray-50);
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

/* ======================================
   FILTERS CARD
   ====================================== */
.filters-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-xl);
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
  align-items: flex-end;
}

.period-selector {
  flex: 1;
  min-width: 300px;
}

.filter-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-gray-700);
  margin-bottom: var(--spacing-xs);
}

.period-buttons {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

.period-btn {
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-gray-300);
  background: var(--color-white);
  color: var(--color-gray-700);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.period-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.period-btn--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-white);
}

.date-inputs {
  display: flex;
  gap: var(--spacing-md);
}

.date-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.room-filter {
  min-width: 200px;
}

/* ======================================
   STATS CARDS
   ====================================== */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-card--analytics {
  border-left: 4px solid var(--color-secondary);
}

.stat-card-icon {
  font-size: 1.7rem;
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-soft);
  border-radius: var(--radius-md);
  flex: 0 0 46px;
}

.stat-card-content {
  flex: 1;
}

.stat-card-value {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-gray-900);
  line-height: 1.2;
}

.stat-card-label {
  font-size: 12px;
  color: var(--color-gray-500);
  margin-top: var(--spacing-xs);
  line-height: 1.35;
}

/* ======================================
   PERIOD INFO
   ====================================== */
.period-info {
  background: var(--color-white);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-xl);
  font-size: var(--text-sm);
  color: var(--color-gray-600);
}

.period-info p {
  margin: var(--spacing-xs) 0;
}

/* ======================================
   SECTIONS
   ====================================== */
.stats-section {
  margin-bottom: var(--spacing-2xl);
}

.stats-section-header {
  margin-bottom: var(--spacing-lg);
}

.stats-section-title {
  margin: 0;
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-gray-900);
}

.stats-section-subtitle {
  margin: var(--spacing-xs) 0 0;
  color: var(--color-gray-500);
  font-size: var(--text-sm);
}

.stats-section--clicks {
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--color-gray-200);
}

/* ======================================
   CHARTS
   ====================================== */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

@media (max-width: 900px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.chart-title {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
  color: var(--color-gray-900);
}

.chart-empty {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-lg);
  color: var(--color-gray-500);
  font-size: var(--text-base);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
}

/* ======================================
   ROOM STATS
   ====================================== */
.room-stats {
  margin-bottom: var(--spacing-xl);
}

.room-stats-title {
  font-size: var(--text-xl);
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  color: var(--color-gray-900);
}

.room-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-lg);
}

.room-stat-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.room-stat-title {
  font-size: var(--text-base);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-gray-200);
  color: var(--color-gray-900);
}

.room-stat-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-xs) 0;
}

.room-stat-label {
  color: var(--color-gray-500);
  font-size: var(--text-sm);
}

.room-stat-value {
  font-weight: 600;
  color: var(--color-gray-900);
  font-size: var(--text-sm);
}

/* ======================================
   LOADING / EMPTY / ERROR
   ====================================== */
.loading-state,
.empty-state,
.error-state {
  text-align: center;
  padding: var(--spacing-3xl);
  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.loading-state p,
.empty-state p,
.error-state p {
  color: var(--color-gray-500);
  margin-top: var(--spacing-md);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state svg {
  color: var(--color-gray-300);
  margin-bottom: var(--spacing-md);
}

.error-state {
  background: var(--color-error-soft);
}

.error-state p {
  color: var(--color-error);
  font-weight: 500;
}

.error-state .btn {
  margin-top: var(--spacing-md);
}

/* ======================================
   RESPONSIVE
   ====================================== */
@media (max-width: 768px) {
  .stats-container {
    padding: var(--spacing-md);
  }

  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .period-selector {
    min-width: auto;
  }

  .date-inputs {
    flex-direction: column;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .room-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
