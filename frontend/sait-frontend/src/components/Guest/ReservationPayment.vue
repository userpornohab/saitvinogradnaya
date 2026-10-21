<template>
  <section aria-label="Оплата бронирования">
    <p v-if="reservation.is_test" class="guest-notice">Тестовый режим: реальная бронь не создаётся.</p>
    <p class="guest-muted">Срок оплаты до {{ new Date(reservation.expires_at).toLocaleString('ru-RU') }}. К оплате {{ money(reservation.deposit_kopeks) }}.</p>
    <p v-if="error" role="alert" class="guest-error">{{ error }}</p>
    <div class="guest-actions">
      <button class="guest-primary" :disabled="busy" @click="pay"><QrCode :size="20"/>{{ busy ? 'Открываем оплату...' : 'Оплатить через СБП' }}</button>
      <button v-if="fallback" class="guest-secondary" @click="redirect">Перейти на страницу Робокассы</button>
    </div>
  </section>
</template>
<script>
import { QrCode } from '@lucide/vue';
import guestApi, { errorText, money } from '@/guestApi';
let scriptPromise;
function loadPaymentScript() {
  if (window.Robokassa?.Render) return Promise.resolve();
  if (!scriptPromise) scriptPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const timer = setTimeout(() => { script.remove(); reject(new Error('timeout')); }, 12000);
    script.src = 'https://auth.robokassa.ru/Merchant/bundle/robokassa_iframe.js'; script.async = true;
    script.onload = () => { clearTimeout(timer); window.Robokassa?.Render ? resolve() : reject(new Error('widget')); };
    script.onerror = () => { clearTimeout(timer); script.remove(); reject(new Error('network')); };
    document.head.appendChild(script);
  }).catch(error => { scriptPromise = null; throw error; });
  return scriptPromise;
}
export default {
  components: { QrCode }, props: { reservation: { type: Object, required: true } },
  data() { return { busy: false, error: '', fallback: null }; },
  methods: {
    money,
    async parameters() { return (await guestApi.post(`/guest/reservations/${this.reservation.id}/payment`)).data; },
    async pay() {
      this.busy = true; this.error = ''; this.fallback = null;
      try {
        const payment = await this.parameters(); this.fallback = payment;
        await loadPaymentScript();
        window.Robokassa.Render({ ...payment.params, Settings: JSON.stringify({ PaymentMethods: ['SBP'], Mode: 'modal' }) });
      } catch (error) { this.error = error.response ? errorText(error) : 'Не удалось открыть виджет. Можно продолжить на защищённой странице Робокассы.'; }
      finally { this.busy = false; }
    },
    async redirect() {
      this.busy = true;
      try {
        const payment = await this.parameters();
        if (payment.action !== 'https://auth.robokassa.ru/Merchant/Index.aspx') throw new Error('Unexpected payment URL');
        const form = document.createElement('form'); form.method = 'POST'; form.action = payment.action;
        Object.entries(payment.params).forEach(([name, value]) => { const input = document.createElement('input'); input.type = 'hidden'; input.name = name; input.value = value; form.appendChild(input); });
        document.body.appendChild(form); form.submit(); form.remove();
      } catch (error) { this.error = errorText(error); }
      finally { this.busy = false; }
    }
  }
};
</script>
