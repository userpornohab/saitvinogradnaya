<template>
  <section class="guest-ui guest-shell">
    <header class="guest-top">
      <div><h1>Личный кабинет</h1><p>{{ state.user ? state.user.name + ', добро пожаловать' : 'Ваш отдых в «Виноградной Лозе»' }}</p></div>
      <div v-if="state.user" class="guest-actions"><button class="guest-secondary" @click="tab = tab === 'profile' ? 'bookings' : 'profile'"><UserRound :size="18"/>{{ tab === 'profile' ? 'Мои бронирования' : 'Профиль' }}</button><button class="guest-icon" title="Выйти" aria-label="Выйти" @click="logout"><LogOut :size="20"/></button></div>
    </header>
    <p v-if="loading" role="status">Загружаем личный кабинет...</p>
    <p v-if="error" class="guest-error" role="alert">{{ error }} <button class="guest-text-button" @click="init">Повторить</button></p>
    <GuestAuthPanel v-if="token || (!loading && !state.user)" :key="token || 'login'" :token="token" :action="action" @token-done="token = ''; action = ''; init()" @authenticated="init"/>
    <template v-else-if="state.user && !loading">
      <div v-if="!state.user.email_verified" class="guest-notice">Подтвердите почту {{ state.user.email }}. <button class="guest-text-button" @click="resend">Отправить письмо</button> <button class="guest-text-button" @click="init">Проверить подтверждение</button></div>
      <p v-if="notice" class="guest-notice" role="status">{{ notice }}</p>
      <form v-if="tab === 'profile'" class="guest-form guest-profile" @submit.prevent="saveProfile">
        <h2>Личные данные</h2><label>Имя<input v-model.trim="profile.name" required minlength="2" maxlength="100" autocomplete="name"></label>
        <label>Телефон<input v-model.trim="profile.phone" type="tel" required pattern="\+?[0-9 \(\)\-]{7,25}" maxlength="25" autocomplete="tel"></label>
        <p class="guest-muted">{{ state.user.email }}</p><button class="guest-primary" :disabled="busy">Сохранить данные</button>
        <button type="button" class="guest-text-button" @click="passwordReset">Отправить ссылку для смены пароля</button>
      </form>
      <template v-else>
        <p v-if="$route.query.payment" class="guest-notice">Статус оплаты проверяется на сервере. Если платёж уже выполнен, дождитесь обновления бронирования.</p>
        <div v-if="!items.length && !selected" class="guest-empty"><CalendarDays :size="42"/><h2>Ваш отдых ещё впереди</h2><p>Здесь появятся ваши бронирования и переписка с администрацией.</p><router-link to="/#rooms" class="guest-primary">Выбрать номер</router-link></div>
        <div v-else class="guest-layout">
          <aside class="guest-reservations" aria-label="Мои бронирования">
            <button v-for="item in items" :key="item.id" class="guest-reservation" :aria-pressed="selected?.id === item.id" @click="select(item)">
              <span class="guest-badge" :class="'guest-badge--' + item.status">{{ labels[item.status] }}</span><h3>{{ item.room_title }}</h3>
              <p>{{ dayLabel(item.check_in_date) }} — {{ dayLabel(item.check_out_date) }}</p><p class="guest-muted">№{{ item.id }} · {{ item.guests }} гостей</p><strong>{{ money(item.total_kopeks) }}</strong>
            </button>
            <nav v-if="total > 10" class="guest-pagination" aria-label="Страницы бронирований"><button class="guest-icon" :disabled="page === 1" aria-label="Предыдущая страница" @click="page--; loadList()"><ChevronLeft/></button><span>{{ page }} / {{ Math.ceil(total / 10) }}</span><button class="guest-icon" :disabled="page * 10 >= total" aria-label="Следующая страница" @click="page++; loadList()"><ChevronRight/></button></nav>
          </aside>
          <section v-if="selected" aria-label="Детали бронирования">
            <h2>{{ selected.room_title }}</h2><span class="guest-badge" :class="'guest-badge--' + selected.status">{{ labels[selected.status] }}</span>
            <dl class="guest-summary"><div><dt>Даты проживания</dt><dd>{{ dayLabel(selected.check_in_date) }} — {{ dayLabel(selected.check_out_date) }}</dd></div><div><dt>Гость</dt><dd>{{ selected.guest_name }}</dd></div><div><dt>Стоимость проживания</dt><dd>{{ money(selected.total_kopeks) }}</dd></div><div><dt>Получено предоплаты</dt><dd class="guest-sum">{{ money(selected.paid_kopeks) }}</dd></div><div v-if="selected.status !== 'refunded'"><dt>Остаток к оплате</dt><dd>{{ money(selected.remaining_kopeks) }}</dd></div></dl>
            <ReservationPayment v-if="selected.status === 'awaiting_payment'" :key="selected.id" :reservation="selected"/>
            <p v-if="selected.status === 'confirmed'" class="guest-notice"><CheckCircle2 :size="18"/> Предоплата получена. Ждём вас в гости!</p>
            <p v-if="selected.status === 'payment_review'" class="guest-error">Платёж получен, но автоматически подтвердить номер не удалось. Администрация должна проверить оплату и согласовать размещение или возврат. Повторно не оплачивайте.</p>
            <p v-if="selected.status === 'cancel_requested'" class="guest-notice">Запрос на отмену передан администрации. Возврат рассматривается по условиям бронирования.</p>
            <p v-if="selected.status === 'refunded'" class="guest-notice">Администратор зарегистрировал возврат. Основание: {{ selected.refund_reference }}.</p>
            <p v-if="selected.status === 'expired'" class="guest-notice">Время резерва истекло. Выберите даты заново. Если вы уже оплатили, дождитесь проверки платежа.</p>
            <p><a :href="selected.terms_url" target="_blank" rel="noopener noreferrer">Условия бронирования</a></p>
            <button v-if="['awaiting_payment','confirmed','test_paid'].includes(selected.status) && !confirmCancel" class="guest-text-button" @click="confirmCancel = true">{{ selected.status === 'awaiting_payment' ? 'Отменить неоплаченную заявку' : 'Запросить отмену' }}</button>
            <div v-if="confirmCancel" class="guest-notice"><p>Отправить запрос на отмену? Возврат оплаченной суммы не производится автоматически.</p><div class="guest-actions"><button class="guest-secondary" :disabled="busy" @click="cancel">Подтвердить отмену</button><button class="guest-text-button" @click="confirmCancel = false">Оставить бронь</button></div></div>
            <BookingChat v-if="selected.chat_available" :key="selected.id" :reservation-id="selected.id"/>
            <p v-else class="guest-muted">Чат с администрацией откроется после подтверждения бронирования.</p>
          </section>
        </div>
      </template>
    </template>
  </section>
</template>
<script>
import { CalendarDays, UserRound, LogOut, ChevronLeft, ChevronRight, CheckCircle2 } from '@lucide/vue';
import guestApi, { guestState, loadGuest, acceptSession, errorText, money, dayLabel, statusLabels } from '@/guestApi';
import GuestAuthPanel from './GuestAuthPanel.vue';
import BookingChat from './BookingChat.vue';
import ReservationPayment from './ReservationPayment.vue';
import '@/assets/guest.css';
export default {
  components: { CalendarDays, UserRound, LogOut, ChevronLeft, ChevronRight, CheckCircle2, GuestAuthPanel, BookingChat, ReservationPayment },
  data() { return { state: guestState, labels: statusLabels, items: [], selected: null, total: 0, page: 1, loading: true, error: '', notice: '', busy: false, tab: 'bookings', profile: { name: '', phone: '' }, timer: null, polling: false, stopped: false, token: '', action: '', confirmCancel: false }; },
  mounted() {
    const params = new URLSearchParams(this.$route.hash.slice(1));
    if (['verify','reset'].includes(params.get('action')) && params.get('token')) { this.action = params.get('action'); this.token = params.get('token'); this.$router.replace({ path: '/account', query: this.$route.query, hash: '' }); }
    this.init();
  },
  beforeUnmount() { this.stopped = true; clearTimeout(this.timer); },
  methods: {
    money, dayLabel,
    async init() {
      this.loading = true; this.error = ''; clearTimeout(this.timer);
      try {
        await loadGuest();
        if (this.state.user) {
          this.profile = { name: this.state.user.name || '', phone: this.state.user.phone || '' };
          await this.loadList();
          const id = Number(this.$route.query.reservation || this.$route.query.InvId);
          if (id > 0) this.selected = (await guestApi.get(`/guest/reservations/${id}`)).data;
          else if (!this.selected) this.selected = this.items[0] || null;
          this.schedule();
        }
      } catch (error) { this.error = errorText(error); }
      finally { this.loading = false; }
    },
    async loadList() { try { const { data } = await guestApi.get('/guest/reservations', { params: { page: this.page } }); this.items = data.items; this.total = data.total; } catch (error) { this.error = errorText(error); } },
    select(item) { this.selected = item; this.confirmCancel = false; this.$router.replace({ path: '/account', query: { reservation: item.id } }); },
    schedule() { clearTimeout(this.timer); if (!this.stopped) this.timer = setTimeout(this.poll, 5000); },
    async poll() {
      if (this.stopped || !this.state.user) return;
      try {
        if (this.selected && !document.hidden) {
          const row = (await guestApi.get(`/guest/reservations/${this.selected.id}`)).data;
          if (this.stopped) return;
          if (row.id === this.selected.id) { this.selected = row; const index = this.items.findIndex(item => item.id === row.id); if (index >= 0) this.items.splice(index, 1, row); }
        }
      } catch (error) { this.error = errorText(error); }
      finally { this.schedule(); }
    },
    async logout() { try { await guestApi.post('/guest/auth/logout'); acceptSession({ user: null, csrf: '' }); this.items = []; this.selected = null; clearTimeout(this.timer); } catch (error) { this.error = errorText(error); } },
    async resend() { try { this.notice = (await guestApi.post('/guest/auth/verification')).data.message; } catch (error) { this.error = errorText(error); } },
    async passwordReset() { try { this.notice = (await guestApi.post('/guest/auth/forgot', { email: this.state.user.email })).data.message; } catch (error) { this.error = errorText(error); } },
    async saveProfile() { this.busy = true; try { this.state.user = (await guestApi.patch('/guest/auth/profile', this.profile)).data; this.notice = 'Данные сохранены'; } catch (error) { this.error = errorText(error); } finally { this.busy = false; } },
    async cancel() { this.busy = true; try { this.selected = (await guestApi.post(`/guest/reservations/${this.selected.id}/cancel`)).data; this.confirmCancel = false; await this.loadList(); } catch (error) { this.error = errorText(error); } finally { this.busy = false; } }
  }
};
</script>
