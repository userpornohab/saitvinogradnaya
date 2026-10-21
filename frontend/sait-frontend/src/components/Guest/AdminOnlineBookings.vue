<template>
  <div class="guest-ui guest-shell">
    <AdminHeader/>
    <header class="guest-top"><div><h1>Онлайн-бронирования</h1><p>Предоплата и общение с гостями</p></div><button class="guest-icon" title="Обновить" aria-label="Обновить" @click="load"><RefreshCw :size="20"/></button></header>
    <div class="guest-tabs" role="tablist" aria-label="Онлайн-бронирования"><button role="tab" :aria-selected="tab === 'bookings'" @click="tab = 'bookings'">Бронирования</button><button role="tab" :aria-selected="tab === 'settings'" @click="tab = 'settings'">Предоплата</button></div>
    <p v-if="error" class="guest-error" role="alert">{{ error }}</p><p v-if="notice" class="guest-notice" role="status">{{ notice }}</p>
    <p v-if="loading" role="status">Загружаем данные...</p>
    <form v-if="tab === 'settings' && policy" class="guest-form guest-settings" @submit.prevent="saveSettings">
      <div class="guest-wide"><span class="guest-badge">{{ policy.is_test ? 'Тестовая среда Робокассы' : 'Настоящие платежи' }}</span><p v-for="item in policy.configuration_errors" :key="item" class="guest-error">{{ item }}</p></div>
      <label class="guest-check guest-wide"><input v-model="policy.enabled" type="checkbox">Принимать онлайн-бронирования</label>
      <label>Способ расчёта предоплаты<select v-model="policy.deposit_mode"><option value="first_night">Стоимость первой ночи</option><option value="percent">Процент от проживания</option></select></label>
      <label v-if="policy.deposit_mode === 'percent'">Предоплата, %<input v-model.number="policy.deposit_percent" type="number" min="1" max="100" required></label>
      <label>Резерв на оплату, минут<input v-model.number="policy.hold_minutes" type="number" min="10" max="60" required></label>
      <label>Ссылка на условия бронирования и отмены<input v-model.trim="policy.terms_url" placeholder="https://..." maxlength="500" :required="policy.enabled"></label>
      <label>Ссылка на политику конфиденциальности<input v-model.trim="policy.privacy_url" placeholder="https://..." maxlength="500" :required="policy.enabled"></label>
      <label>Версия условий<input v-model.trim="policy.terms_version" required maxlength="50"></label>
      <div class="guest-wide"><button class="guest-primary" :disabled="busy"><Save :size="18"/>Сохранить настройки</button></div>
    </form>
    <template v-if="tab === 'bookings'">
      <form class="guest-settings" @submit.prevent="page = 1; loadList()"><label>Имя гостя<input v-model.trim="search" type="search" maxlength="100" placeholder="Поиск по имени"></label><label>Статус<select v-model="filter" @change="page = 1; loadList()"><option value="">Все статусы</option><option v-for="(label, value) in labels" :key="value" :value="value">{{ label }}</option></select></label><div><button class="guest-secondary"><Search :size="18"/>Найти</button></div></form>
      <p v-if="!items.length && !loading" class="guest-muted">Бронирований по выбранным условиям нет.</p>
      <div class="guest-layout">
        <aside class="guest-reservations">
          <button v-for="row in items" :key="row.id" class="guest-reservation" :aria-pressed="selected?.id === row.id" @click="selected = row; refundConfirm = false; reference = ''">
            <span class="guest-badge" :class="'guest-badge--' + row.status">{{ labels[row.status] }}</span><h3>{{ row.guest_name }}</h3><p>{{ row.room_title }}</p><p>{{ dayLabel(row.check_in_date) }} — {{ dayLabel(row.check_out_date) }}</p><small>№{{ row.id }} · Получено {{ money(row.paid_kopeks) }}{{ row.is_test ? ' · Тест' : '' }}</small>
          </button>
          <nav v-if="total > 20" class="guest-pagination" aria-label="Страницы заявок"><button class="guest-icon" :disabled="page === 1" aria-label="Назад" @click="page--; loadList()"><ChevronLeft/></button><span>{{ page }} / {{ Math.ceil(total / 20) }}</span><button class="guest-icon" :disabled="page * 20 >= total" aria-label="Вперёд" @click="page++; loadList()"><ChevronRight/></button></nav>
        </aside>
        <section v-if="selected">
          <h2>Бронирование №{{ selected.id }}</h2><h3>{{ selected.guest_name }}</h3><p><a :href="'tel:' + selected.guest_phone">{{ selected.guest_phone }}</a></p>
          <dl class="guest-summary"><div><dt>Проживание</dt><dd>{{ money(selected.total_kopeks) }}</dd></div><div><dt>Предоплата</dt><dd>{{ money(selected.deposit_kopeks) }}</dd></div><div><dt>Получено</dt><dd class="guest-sum">{{ money(selected.paid_kopeks) }}</dd></div><div><dt>Остаток</dt><dd>{{ money(selected.remaining_kopeks) }}</dd></div><div><dt>Правило предоплаты</dt><dd>{{ selected.deposit_rule === 'first_night' ? 'Первая ночь' : selected.deposit_rule }}</dd></div></dl>
          <p v-if="selected.status === 'payment_review'" class="guest-error">Деньги получены, номер не подтверждён. Свяжитесь с гостем и согласуйте размещение или возврат. Повторный платёж не требуется.</p>
          <p v-if="selected.status === 'cancel_requested'" class="guest-notice">Гость запросил отмену. До завершения возврата номер остаётся занят.</p>
          <button v-if="['payment_review','cancel_requested'].includes(selected.status) && !refundConfirm" class="guest-secondary" @click="refundConfirm = true">Зарегистрировать выполненный возврат</button>
          <form v-if="refundConfirm" class="guest-form" @submit.prevent="recordRefund"><p class="guest-notice">Сначала выполните полный возврат {{ money(selected.paid_kopeks) }} в Робокассе. Это действие только записывает результат и освобождает номер, деньги не переводит.</p><label>Номер операции возврата<input v-model.trim="reference" required minlength="5" maxlength="200"></label><div class="guest-actions"><button class="guest-primary" :disabled="busy">Возврат выполнен, сохранить</button><button type="button" class="guest-text-button" @click="refundConfirm = false">Назад</button></div></form>
          <p v-if="selected.status === 'refunded'" class="guest-notice">Возврат: {{ selected.refund_reference }}</p>
          <BookingChat v-if="selected.chat_available" :key="selected.id" :reservation-id="selected.id" admin/>
        </section>
      </div>
    </template>
  </div>
</template>
<script>
import { RefreshCw, Save, Search, ChevronLeft, ChevronRight } from '@lucide/vue';
import api from '@/api';
import { errorText, money, dayLabel, statusLabels } from '@/guestApi';
import AdminHeader from '@/components/AdminHeader.vue';
import BookingChat from './BookingChat.vue';
import '@/assets/guest.css';
export default {
  components: { RefreshCw, Save, Search, ChevronLeft, ChevronRight, AdminHeader, BookingChat },
  data() { return { tab: 'bookings', policy: null, items: [], selected: null, labels: statusLabels, error: '', notice: '', loading: false, busy: false, search: '', filter: '', page: 1, total: 0, refundConfirm: false, reference: '', timer: null, stopped: false }; },
  mounted() { this.load(); }, beforeUnmount() { this.stopped = true; clearTimeout(this.timer); },
  methods: {
    money, dayLabel,
    async load() { this.loading = true; this.error = ''; try { this.policy = (await api.get('/guest-admin/payment-settings')).data; await this.loadList(); } catch (error) { this.error = errorText(error); } finally { this.loading = false; } },
    async loadList() {
      clearTimeout(this.timer);
      try { const { data } = await api.get('/guest-admin/reservations', { params: { page: this.page, search: this.search, state: this.filter } }); this.items = data.items; this.total = data.total; if (this.selected) this.selected = this.items.find(row => row.id === this.selected.id) || null; else this.selected = this.items[0] || null; }
      catch (error) { this.error = errorText(error); }
      finally { if (!this.stopped) this.timer = setTimeout(() => { if (document.hidden || this.tab !== 'bookings' || this.refundConfirm) this.timer = setTimeout(this.loadList, 15000); else this.loadList(); }, 15000); }
    },
    async saveSettings() {
      this.busy = true; this.error = ''; this.notice = '';
      try { const { enabled, deposit_mode, deposit_percent, hold_minutes, terms_url, privacy_url, terms_version } = this.policy; this.policy = (await api.put('/guest-admin/payment-settings', { enabled, deposit_mode, deposit_percent, hold_minutes, terms_url, privacy_url, terms_version })).data; this.notice = 'Настройки сохранены. Уже созданные счета не изменены.'; }
      catch (error) { this.error = errorText(error); } finally { this.busy = false; }
    },
    async recordRefund() { this.busy = true; try { await api.post(`/guest-admin/reservations/${this.selected.id}/refund-record`, { reference: this.reference }); this.refundConfirm = false; this.reference = ''; await this.loadList(); } catch (error) { this.error = errorText(error); } finally { this.busy = false; } }
  }
};
</script>
