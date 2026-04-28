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

      <!-- Основные карточки статистики -->
      <div class="stats-cards" v-if="statistics">
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
      </div>

      <!-- Информация о периоде -->
      <div class="period-info" v-if="statistics">
        <p><strong>Период:</strong> {{ formatDate(statistics.period.start_date) }} — {{ formatDate(statistics.period.end_date) }}</p>
        <p v-if="statistics.filter.room_title"><strong>Фильтр:</strong> {{ statistics.filter.room_title }}</p>
      </div>

      <!-- Графики по номерам (только когда выбраны ВСЕ номера) -->
      <div class="charts-grid" v-if="statistics && statistics.room_statistics?.length > 1">
        <!-- График бронирований по номерам -->
        <div class="chart-card">
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
        <div class="chart-card">
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
      <div class="room-stats" v-if="statistics && statistics.room_statistics?.length">
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
            </div>
          </div>
        </div>
      </div>

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

        const response = await api.get('/bookings/booking-stats', { params });
        this.statistics = response.data;
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
      return date.toISOString().split('T')[0];
    },
    formatCurrency(amount) {
      if (!amount && amount !== 0) return '0 ₽';
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(amount);
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-card-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-soft);
  border-radius: var(--radius-lg);
}

.stat-card-content {
  flex: 1;
}

.stat-card-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-gray-900);
  line-height: 1.2;
}

.stat-card-label {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
  margin-top: var(--spacing-xs);
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
