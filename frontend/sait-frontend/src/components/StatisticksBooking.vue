<template>
    
  <div class="booking-stats">
    <AdminHeader></AdminHeader>
    <div class="stats-header">
      <h2>Статистика бронирований</h2>
    </div>

    <div class="filters-container">
      <!-- Период -->
      <div class="filter-group">
        <label for="period-type">Тип периода:</label>
        <select id="period-type" v-model="periodType" @change="onPeriodTypeChange">
          <option value="custom">Произвольный период</option>
          <option value="month">По месяцам</option>
        </select>
      </div>

      <!-- Выбор месяца -->
      <div class="filter-group" v-if="periodType === 'month'">
        <label for="month">Месяц:</label>
        <select id="month" v-model="selectedMonth" @change="onMonthChange">
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.label }}
          </option>
        </select>
      </div>

      <!-- Произвольный период -->
      <div class="filter-group" v-if="periodType === 'custom'">
        <label for="start-date">С:</label>
        <input type="date" id="start-date" v-model="customStartDate" @change="fetchStatistics" />
      </div>

      <div class="filter-group" v-if="periodType === 'custom'">
        <label for="end-date">По:</label>
        <input type="date" id="end-date" v-model="customEndDate" @change="fetchStatistics" />
      </div>

      <!-- Выбор комнаты -->
      <div class="filter-group">
        <label for="room">Комната:</label>
        <select id="room" v-model="selectedRoomId" @change="fetchStatistics">
          <option value="all">Все номера</option>
          <option v-for="room in rooms" :key="room.id" :value="room.id">
            {{ room.title }}
          </option>
        </select>
      </div>

      <!-- Кнопка обновления -->
      <button class="refresh-btn" @click="fetchStatistics" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Обновить' }}
      </button>
    </div>

    <!-- Основная статистика -->
    <div class="stats-overview" v-if="statistics">
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.statistics.total_bookings }}</div>
            <div class="stat-label">Всего броней</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-value">{{ formatCurrency(statistics.statistics.total_income) }}</div>
            <div class="stat-label">Общий доход</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.statistics.total_guests }}</div>
            <div class="stat-label">Всего гостей</div>
          </div>
        </div>
      </div>

      <!-- Информация о периоде -->
      <div class="period-info">
        <p><strong>Период:</strong> {{ formatDate(statistics.period.start_date) }} - {{ formatDate(statistics.period.end_date) }}</p>
        <p><strong>Фильтр:</strong> {{ statistics.filter.room_title }}</p>
      </div>
    </div>

    <!-- Статистика по комнатам (только когда выбраны все номера) -->
    <div class="room-stats" v-if="statistics && statistics.room_statistics && statistics.room_statistics.length > 0">
      <h3>Статистика по номерам</h3>
      <div class="room-stats-grid">
        <div v-for="roomStat in statistics.room_statistics" :key="roomStat.room_id" class="room-stat-card">
          <h4>{{ roomStat.room_title }}</h4>
          <div class="room-stat-details">
            <div class="room-stat-item">
              <span class="label">Броней:</span>
              <span class="value">{{ roomStat.booking_count }}</span>
            </div>
            <div class="room-stat-item">
              <span class="label">Доход:</span>
              <span class="value">{{ formatCurrency(roomStat.total_income) }}</span>
            </div>
            <div class="room-stat-item">
              <span class="label">Гостей:</span>
              <span class="value">{{ roomStat.total_guests }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Сообщение о загрузке -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка статистики...</p>
    </div>

    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-message">
      <p>Ошибка: {{ error }}</p>
      <button @click="fetchStatistics">Попробовать снова</button>
    </div>

    <!-- Сообщение когда нет данных -->
    <div v-if="!loading && !statistics && !error" class="no-data">
      <p>Выберите параметры для отображения статистики</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

import AdminHeader  from './AdminHeader.vue';

export default {
    
  name: 'BookingStatistics',
  data() {
    return {
      periodType: 'month',
      selectedMonth: '',
      customStartDate: '',
      customEndDate: '',
      selectedRoomId: 'all',
      rooms: [],
      statistics: null,
      loading: false,
      error: null,
      months: []
    }
  },
  components: {
    AdminHeader
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  },
  mounted() {
    this.generateMonths()
    this.setDefaultDates()
    this.fetchRooms()
    this.fetchStatistics()
  },
  methods: {
    generateMonths() {
      const months = []
      const currentDate = new Date()
      const currentYear = currentDate.getFullYear()
      
      // Генерируем месяцы за последние 2 года
      for (let year = currentYear - 1; year <= currentYear + 1; year++) {
        for (let month = 1; month <= 12; month++) {
          const date = new Date(year, month - 1, 1)
          months.push({
            value: `${year}-${month.toString().padStart(2, '0')}`,
            label: date.toLocaleString('ru-RU', { month: 'long', year: 'numeric' })
          })
        }
      }
      
      this.months = months
    },
    
    setDefaultDates() {
      // Устанавливаем текущий месяц по умолчанию
      const now = new Date()
      this.selectedMonth = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}`
      this.onMonthChange()
      
      // Устанавливаем произвольный период (последние 30 дней)
      this.customEndDate = this.formatDateForInput(now)
      const thirtyDaysAgo = new Date(now)
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      this.customStartDate = this.formatDateForInput(thirtyDaysAgo)
    },
    
    onPeriodTypeChange() {
      if (this.periodType === 'month') {
        this.onMonthChange()
      } else {
        this.fetchStatistics()
      }
    },
    
    onMonthChange() {
      if (!this.selectedMonth) return
      
      const [year, month] = this.selectedMonth.split('-')
      const startDate = new Date(year, month - 1, 1)
      const endDate = new Date(year, month, 0) // Последний день месяца
      
      this.customStartDate = this.formatDateForInput(startDate)
      this.customEndDate = this.formatDateForInput(endDate)
      this.fetchStatistics()
    },
    
    async fetchRooms() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/rooms/admin/')
        this.rooms = response.data
      } catch (error) {
        console.error('Ошибка загрузки списка комнат:', error)
      }
    },
    
    async fetchStatistics() {
      if (!this.customStartDate || !this.customEndDate) return
      
      this.loading = true
      this.error = null
      
      try {
        const params = {
          start_date: this.customStartDate,
          end_date: this.customEndDate
        }
        
        if (this.selectedRoomId !== 'all') {
          params.room_id = parseInt(this.selectedRoomId)
        }
        
        const response = await axios.get('http://127.0.0.1:8000/bookings/booking-stats', { params })
        this.statistics = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка загрузки статистики'
        console.error('Ошибка загрузки статистики:', error)
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU')
    },
    
    formatDateForInput(date) {
      return date.toISOString().split('T')[0]
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(amount)
    }
  }
}
</script>

<style scoped>
.booking-stats {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.stats-header {
  text-align: center;
  margin-bottom: 30px;
}

.stats-header h2 {
  color: #333;
  margin: 0;
}

.filters-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  align-items: end;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.filter-group label {
  font-weight: 600;
  margin-bottom: 5px;
  color: #555;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  height: fit-content;
}

.refresh-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.refresh-btn:hover:not(:disabled) {
  background: #0056b3;
}

.stats-overview {
  margin-bottom: 30px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 2em;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8em;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #666;
  font-size: 0.9em;
}

.period-info {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.period-info p {
  margin: 5px 0;
}

.room-stats {
  margin-top: 30px;
}

.room-stats h3 {
  color: #333;
  margin-bottom: 20px;
}

.room-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.room-stat-card {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.room-stat-card h4 {
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.room-stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.room-stat-item .label {
  color: #666;
}

.room-stat-item .value {
  font-weight: 600;
  color: #333;
}

.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 40px;
  background: #ffe6e6;
  border-radius: 8px;
  color: #d63031;
}

.error-message button {
  margin-top: 10px;
  padding: 8px 16px;
  background: #d63031;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
}

@media (max-width: 768px) {
  .filters-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .room-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>