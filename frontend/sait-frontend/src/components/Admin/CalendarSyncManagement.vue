<template>
  <div class="section-card calendar-sync-card">
    <div class="edit-header">
      <div>
        <h3>Синхронизация календарей — {{ room.title }}</h3>
        <p class="sync-subtitle">Импортируйте занятость из агрегаторов и отдавайте им календарь сайта.</p>
      </div>
      <button @click="$emit('close')" class="btn-close">✕</button>
    </div>

    <div class="sync-layout">
      <section class="sync-panel export-panel">
        <div class="sync-panel-header">
          <div>
            <h4>Ссылка для агрегаторов</h4>
            <p>Эту ссылку нужно вставить в Суточно, Airbnb или другой сервис как внешний календарь.</p>
          </div>
          <button class="btn-outline" @click="loadExportLink" :disabled="loadingExport">
            {{ loadingExport ? 'Создаю...' : exportLink ? 'Обновить' : 'Создать ссылку' }}
          </button>
        </div>

        <div v-if="exportLink" class="export-link-box">
          <input :value="exportLink.url" readonly>
          <button class="btn-primary" @click="copyExportLink">
            {{ copied ? 'Скопировано' : 'Копировать' }}
          </button>
        </div>
        <p v-else class="muted-text">Ссылка появится после нажатия на кнопку.</p>
      </section>

      <section class="sync-panel import-panel">
        <div class="sync-panel-header">
          <div>
            <h4>Календари для импорта</h4>
            <p>Например ссылка Суточно вида <span class="inline-code">/calendar/ical/...ics/</span>.</p>
          </div>
          <button class="btn-outline" @click="syncAllSources" :disabled="!activeSources.length || isSyncingAll">
            {{ isSyncingAll ? 'Синхронизация...' : 'Синхронизировать все' }}
          </button>
        </div>

        <form class="source-form" @submit.prevent="createSource">
          <label>
            <span>Название</span>
            <input v-model.trim="newSource.name" placeholder="Например: Суточно">
          </label>
          <label class="source-url-field">
            <span>Ссылка .ics</span>
            <input v-model.trim="newSource.url" placeholder="https://.../calendar.ics">
          </label>
          <button class="btn-primary" type="submit" :disabled="isCreatingSource">
            {{ isCreatingSource ? 'Добавляю...' : 'Добавить' }}
          </button>
        </form>

        <div class="sources-list">
          <p v-if="!sources.length" class="muted-text">Внешних календарей пока нет.</p>
          <article v-for="source in sources" :key="source.id" class="source-item">
            <div class="source-main">
              <div>
                <h5>{{ source.name }}</h5>
                <p>{{ source.url }}</p>
              </div>
              <span :class="['source-status', source.is_active ? 'active' : 'paused']">
                {{ source.is_active ? 'Активен' : 'Отключен' }}
              </span>
            </div>

            <div class="source-meta">
              <span>Событий: {{ sourceEventCount(source.id) }}</span>
              <span>Последняя синхронизация: {{ formatDateTime(source.last_synced_at) }}</span>
            </div>
            <p v-if="source.last_error" class="source-error">{{ source.last_error }}</p>

            <div class="source-actions">
              <button class="btn-outline" @click="syncSource(source)" :disabled="syncingIds[source.id]">
                {{ syncingIds[source.id] ? 'Синхронизация...' : 'Синхронизировать' }}
              </button>
              <button class="btn-ghost" @click="toggleSource(source)">
                {{ source.is_active ? 'Отключить' : 'Включить' }}
              </button>
              <button class="btn-danger" @click="deleteSource(source)">Удалить</button>
            </div>
          </article>
        </div>
      </section>

      <section class="sync-panel events-panel">
        <div class="sync-panel-header">
          <div>
            <h4>Импортированная занятость</h4>
            <p>Эти периоды уже участвуют в поиске свободных номеров.</p>
          </div>
          <button class="btn-outline" @click="loadEvents" :disabled="loadingEvents">Обновить</button>
        </div>

        <div class="events-list">
          <p v-if="!events.length" class="muted-text">Импортированных периодов пока нет.</p>
          <article v-for="event in sortedEvents" :key="event.id" class="event-item">
            <div>
              <strong>{{ formatDate(event.start_date) }} — {{ formatDate(event.end_date) }}</strong>
              <span>{{ event.summary || 'Забронировано' }}</span>
            </div>
            <small>{{ sourceName(event.source_id) }}</small>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'CalendarSyncManagement',
  props: {
    room: { type: Object, required: true }
  },
  emits: ['close', 'notify'],
  data() {
    return {
      exportLink: null,
      sources: [],
      events: [],
      newSource: { name: '', url: '' },
      loadingExport: false,
      loadingEvents: false,
      isCreatingSource: false,
      isSyncingAll: false,
      syncingIds: {},
      copied: false
    };
  },
  computed: {
    activeSources() {
      return this.sources.filter(source => source.is_active);
    },
    sortedEvents() {
      return [...this.events].sort((a, b) => {
        const dateDiff = new Date(a.start_date) - new Date(b.start_date);
        return dateDiff || a.id - b.id;
      });
    }
  },
  watch: {
    'room.id': {
      immediate: true,
      async handler() {
        await this.loadInitialData();
      }
    }
  },
  methods: {
    async loadInitialData() {
      if (!this.room?.id) return;
      await Promise.all([
        this.loadExportLink(),
        this.loadSources(),
        this.loadEvents()
      ]);
    },
    async loadExportLink() {
      try {
        this.loadingExport = true;
        const response = await api.get(`/calendar-sync/rooms/${this.room.id}/export-link`);
        this.exportLink = response.data;
      } catch (error) {
        this.handleError(error, 'Не удалось получить ссылку календаря');
      } finally {
        this.loadingExport = false;
      }
    },
    async loadSources() {
      try {
        const response = await api.get(`/calendar-sync/rooms/${this.room.id}/sources`);
        this.sources = response.data;
      } catch (error) {
        this.handleError(error, 'Не удалось загрузить внешние календари');
      }
    },
    async loadEvents() {
      try {
        this.loadingEvents = true;
        const response = await api.get(`/calendar-sync/rooms/${this.room.id}/events`);
        this.events = response.data;
      } catch (error) {
        this.handleError(error, 'Не удалось загрузить импортированную занятость');
      } finally {
        this.loadingEvents = false;
      }
    },
    async createSource() {
      if (!this.newSource.name || !this.newSource.url) {
        this.notify('error', 'Укажите название и ссылку календаря');
        return;
      }
      try {
        this.isCreatingSource = true;
        const response = await api.post(`/calendar-sync/rooms/${this.room.id}/sources`, {
          name: this.newSource.name,
          url: this.newSource.url,
          is_active: true
        });
        this.sources.push(response.data);
        this.newSource = { name: '', url: '' };
        this.notify('success', 'Календарь добавлен');
      } catch (error) {
        this.handleError(error, 'Не удалось добавить календарь');
      } finally {
        this.isCreatingSource = false;
      }
    },
    async syncSource(source) {
      try {
        this.syncingIds = { ...this.syncingIds, [source.id]: true };
        const result = await api.post(`/calendar-sync/sources/${source.id}/sync`);
        await Promise.all([this.loadSources(), this.loadEvents()]);
        if (result.data.last_error) {
          this.notify('error', result.data.last_error);
        } else {
          this.notify('success', `Импортировано периодов: ${result.data.imported_count}`);
        }
      } catch (error) {
        this.handleError(error, 'Не удалось синхронизировать календарь');
      } finally {
        this.syncingIds = { ...this.syncingIds, [source.id]: false };
      }
    },
    async syncAllSources() {
      try {
        this.isSyncingAll = true;
        const response = await api.post(`/calendar-sync/rooms/${this.room.id}/sync-all`);
        await Promise.all([this.loadSources(), this.loadEvents()]);
        const failed = response.data.filter(item => item.last_error);
        const imported = response.data.reduce((sum, item) => sum + item.imported_count, 0);
        this.notify(failed.length ? 'error' : 'success', failed.length ? 'Часть календарей не синхронизировалась' : `Импортировано периодов: ${imported}`);
      } catch (error) {
        this.handleError(error, 'Не удалось синхронизировать календари');
      } finally {
        this.isSyncingAll = false;
      }
    },
    async toggleSource(source) {
      try {
        const response = await api.patch(`/calendar-sync/sources/${source.id}`, {
          is_active: !source.is_active
        });
        this.sources = this.sources.map(item => item.id === source.id ? response.data : item);
      } catch (error) {
        this.handleError(error, 'Не удалось изменить статус календаря');
      }
    },
    async deleteSource(source) {
      if (!confirm(`Удалить календарь "${source.name}" и его импортированные периоды?`)) return;
      try {
        await api.delete(`/calendar-sync/sources/${source.id}`);
        this.sources = this.sources.filter(item => item.id !== source.id);
        await this.loadEvents();
        this.notify('success', 'Календарь удален');
      } catch (error) {
        this.handleError(error, 'Не удалось удалить календарь');
      }
    },
    async copyExportLink() {
      if (!this.exportLink?.url) return;
      try {
        await navigator.clipboard.writeText(this.exportLink.url);
        this.copied = true;
        this.notify('success', 'Ссылка скопирована');
        setTimeout(() => { this.copied = false; }, 2000);
      } catch {
        this.notify('error', 'Не удалось скопировать ссылку');
      }
    },
    sourceName(sourceId) {
      return this.sources.find(source => source.id === sourceId)?.name || `Источник #${sourceId}`;
    },
    sourceEventCount(sourceId) {
      return this.events.filter(event => event.source_id === sourceId).length;
    },
    formatDate(value) {
      if (!value) return '—';
      return new Date(value).toLocaleDateString('ru-RU');
    },
    formatDateTime(value) {
      if (!value) return 'еще не было';
      return new Date(value).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    notify(type, message) {
      this.$emit('notify', { type, message });
    },
    handleError(error, fallbackMessage) {
      const detail = error.response?.data?.detail;
      this.notify('error', Array.isArray(detail) ? fallbackMessage : (detail || fallbackMessage));
    }
  }
}
</script>

<style scoped>
.calendar-sync-card {
  overflow: hidden;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-lg);
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-gray-200);
}

.edit-header h3,
.sync-panel h4,
.source-item h5 {
  margin: 0;
  color: var(--color-gray-900);
}

.sync-subtitle,
.sync-panel-header p,
.muted-text,
.source-main p,
.source-meta,
.event-item span,
.event-item small {
  margin: 0;
  color: var(--color-gray-600);
}

.sync-subtitle,
.sync-panel-header p {
  margin-top: 4px;
  font-size: var(--text-sm);
}

.btn-close {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--radius-full);
  background: var(--color-gray-100);
  cursor: pointer;
}

.sync-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.9fr);
  gap: var(--spacing-md);
}

.sync-panel {
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  background: var(--color-white);
}

.export-panel,
.events-panel {
  grid-column: 1 / -1;
}

.sync-panel-header {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-md);
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.export-link-box,
.source-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--spacing-sm);
  align-items: end;
}

.source-form {
  grid-template-columns: minmax(160px, 0.35fr) minmax(260px, 1fr) auto;
  margin-bottom: var(--spacing-md);
}

.source-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-gray-700);
}

.export-link-box input,
.source-form input {
  width: 100%;
  min-height: 42px;
  padding: 0 var(--spacing-md);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-md);
  font: inherit;
}

.inline-code {
  font-family: monospace;
  color: var(--color-gray-900);
}

.sources-list,
.events-list {
  display: grid;
  gap: var(--spacing-sm);
}

.source-item,
.event-item {
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  background: var(--color-gray-50);
}

.source-main,
.source-actions,
.source-meta,
.event-item {
  display: flex;
  gap: var(--spacing-sm);
}

.source-main,
.event-item {
  justify-content: space-between;
  align-items: flex-start;
}

.source-main p {
  margin-top: 4px;
  font-size: var(--text-xs);
  word-break: break-all;
}

.source-status {
  flex-shrink: 0;
  padding: 4px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 700;
}

.source-status.active {
  color: var(--color-success);
  background: rgba(34, 197, 94, 0.12);
}

.source-status.paused {
  color: var(--color-gray-600);
  background: var(--color-gray-200);
}

.source-meta {
  margin-top: var(--spacing-sm);
  flex-wrap: wrap;
  font-size: var(--text-xs);
}

.source-error {
  margin: var(--spacing-sm) 0 0;
  color: var(--color-error);
  font-size: var(--text-xs);
}

.source-actions {
  margin-top: var(--spacing-sm);
  flex-wrap: wrap;
}

.event-item div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.btn-primary,
.btn-outline,
.btn-ghost,
.btn-danger {
  min-height: 38px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  color: white;
  background: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.btn-outline,
.btn-ghost {
  color: var(--color-gray-800);
  background: var(--color-white);
  border: 1px solid var(--color-gray-300);
}

.btn-danger {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.16);
}

.btn-primary:disabled,
.btn-outline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .sync-layout,
  .source-form,
  .export-link-box {
    grid-template-columns: 1fr;
  }

  .sync-panel-header,
  .source-main,
  .event-item {
    flex-direction: column;
  }
}
</style>
