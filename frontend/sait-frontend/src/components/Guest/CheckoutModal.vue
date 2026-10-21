<template>
  <Teleport to="body">
    <div class="guest-ui guest-overlay" @click.self="close" @keydown="onKeydown">
      <section ref="dialog" class="guest-dialog" role="dialog" aria-modal="true" aria-labelledby="checkout-title" tabindex="-1">
        <button class="guest-icon" title="Закрыть" aria-label="Закрыть" @click="close"><X :size="22"/></button>
        <h2 id="checkout-title">Бронирование номера</h2>
        <p class="guest-muted">{{ dayLabel(dates.check_in_date) }} — {{ dayLabel(dates.check_out_date) }} · Гостей: {{ dates.guests }}</p>
        <p v-if="loading" role="status">Проверяем данные...</p>
        <p v-if="error" class="guest-error" role="alert">{{ error }}</p>
        <template v-if="!loading && policy">
          <p v-if="!policy.available" class="guest-notice">Онлайн-бронирование временно недоступно.</p>
          <GuestAuthPanel v-else-if="!state.user" @authenticated="prepare"/>
          <div v-else-if="!state.user.email_verified">
            <p>Для бронирования подтвердите почту {{ state.user.email }} по ссылке из письма.</p>
            <div class="guest-actions"><button class="guest-secondary" @click="resend">Отправить письмо</button><button class="guest-primary" @click="prepare">Я подтвердил почту</button></div>
            <p v-if="notice" role="status">{{ notice }}</p>
          </div>
          <form v-else-if="quote" class="guest-form" @submit.prevent="reserve">
            <h3>{{ quote.room_title }}</h3>
            <dl class="guest-summary">
              <div><dt>Проживание</dt><dd>{{ money(quote.total_kopeks) }}</dd></div>
              <div><dt>Предоплата {{ quote.deposit_rule === 'first_night' ? 'за первую ночь' : quote.deposit_rule }}</dt><dd class="guest-sum">{{ money(quote.deposit_kopeks) }}</dd></div>
              <div><dt>При заселении</dt><dd>{{ money(quote.total_kopeks - quote.deposit_kopeks) }}</dd></div>
            </dl>
            <label>Имя гостя<input v-model.trim="name" required minlength="2" maxlength="100" autocomplete="name"></label>
            <label>Телефон<input v-model.trim="phone" type="tel" required pattern="\+?[0-9 \(\)\-]{7,25}" autocomplete="tel" maxlength="25"></label>
            <label class="guest-check"><input v-model="accepted" type="checkbox" required><span>Принимаю <a :href="policy.terms_url" target="_blank" rel="noopener noreferrer">условия бронирования и отмены</a> и ознакомлен с <a :href="policy.privacy_url" target="_blank" rel="noopener noreferrer">политикой конфиденциальности</a>.</span></label>
            <p v-if="policy.is_test" class="guest-notice">Тестовый режим. Реальная бронь не создаётся.</p>
            <p class="guest-muted">На оплату предоплаты отводится {{ policy.hold_minutes }} минут.</p>
            <button class="guest-primary" :disabled="busy || !accepted"><CreditCard :size="20"/>{{ busy ? 'Создаём бронирование...' : 'Перейти к оплате' }}</button>
          </form>
          <button v-else-if="state.user?.email_verified && policy.available" class="guest-secondary" @click="prepare">Обновить расчёт</button>
        </template>
      </section>
    </div>
  </Teleport>
</template>
<script>
import { X, CreditCard } from '@lucide/vue';
import guestApi, { guestState, loadGuest, money, dayLabel, errorText, requestKey } from '@/guestApi';
import GuestAuthPanel from './GuestAuthPanel.vue';
import '@/assets/guest.css';
const dateKey = value => { const d = new Date(value); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; };
export default {
  components: { X, CreditCard, GuestAuthPanel },
  props: { bookingData: { type: Object, required: true }, modelValue: Boolean }, emits: ['update:modelValue'],
  data() { return { state: guestState, loading: true, busy: false, policy: null, quote: null, name: '', phone: '', accepted: false, error: '', notice: '', requestKey: requestKey(), previousFocus: null, previousOverflow: '' }; },
  computed: { dates() { return { room_id: Number(this.bookingData.roomId), check_in_date: dateKey(this.bookingData.checkin), check_out_date: dateKey(this.bookingData.checkout), guests: Number(this.bookingData.guests) }; } },
  mounted() { this.previousFocus = document.activeElement; this.previousOverflow = document.body.style.overflow; document.body.style.overflow = 'hidden'; this.$refs.dialog.focus(); this.prepare(); },
  beforeUnmount() { document.body.style.overflow = this.previousOverflow; this.previousFocus?.focus(); },
  methods: {
    money, dayLabel, close() { if (!this.busy) this.$emit('update:modelValue', false); },
    onKeydown(event) {
      if (event.key === 'Escape') this.close();
      if (event.key !== 'Tab') return;
      const elements = [...this.$refs.dialog.querySelectorAll('button:not(:disabled),input:not(:disabled),a[href]')];
      if (event.shiftKey && (document.activeElement === elements[0] || document.activeElement === this.$refs.dialog)) { event.preventDefault(); elements.at(-1)?.focus(); }
      else if (!event.shiftKey && document.activeElement === elements.at(-1)) { event.preventDefault(); elements[0]?.focus(); }
    },
    async prepare() {
      this.loading = true; this.error = ''; this.quote = null;
      try {
        await loadGuest(); this.policy = (await guestApi.get('/guest/booking-policy')).data;
        if (this.state.user?.email_verified && this.policy.available) {
          this.name ||= this.state.user.name; this.phone ||= this.state.user.phone;
          this.quote = (await guestApi.post('/guest/quote', this.dates)).data;
          this.accepted = false; this.requestKey = requestKey();
        }
      } catch (error) { this.error = errorText(error); }
      finally { this.loading = false; }
    },
    async resend() {
      try { this.notice = (await guestApi.post('/guest/auth/verification')).data.message; }
      catch (error) { this.error = errorText(error); }
    },
    async reserve() {
      if (this.busy || !this.accepted) return;
      this.busy = true; this.error = '';
      try {
        const response = await guestApi.post('/guest/reservations', { ...this.dates,
          guest_name: this.name, guest_phone: this.phone, accepted_terms: true, request_key: this.requestKey,
          terms_version: this.quote.terms_version, quoted_total_kopeks: this.quote.total_kopeks, quoted_deposit_kopeks: this.quote.deposit_kopeks });
        this.$emit('update:modelValue', false);
        this.$router.push({ path: '/account', query: { reservation: response.data.id } });
      } catch (error) { this.error = errorText(error); if (error.response?.status === 409) this.quote = null; }
      finally { this.busy = false; }
    }
  }
};
</script>
