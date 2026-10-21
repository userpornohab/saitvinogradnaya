<template>
  <section class="guest-chat" aria-label="Чат с администрацией">
    <h3>{{ admin ? 'Переписка с гостем' : 'Чат с администрацией' }}</h3>
    <p v-if="error" class="guest-error" role="alert">{{ error }}</p>
    <div class="guest-messages" ref="messages" role="log" aria-live="polite" aria-relevant="additions">
      <p v-if="!items.length" class="guest-muted">{{ loading ? 'Загружаем сообщения...' : 'Сообщений пока нет' }}</p>
      <article v-for="item in items" :key="item.id" class="guest-message" :class="{ 'guest-message--own': item.from_admin === admin }">
        <strong>{{ item.from_admin ? 'Администрация' : 'Гость' }}</strong>
        <p>{{ item.body }}</p><small>{{ new Date(item.created_at).toLocaleString('ru-RU') }}</small>
      </article>
    </div>
    <form @submit.prevent="send" class="guest-chat-form">
      <textarea v-model="body" aria-label="Сообщение" placeholder="Ваше сообщение" maxlength="4000" required></textarea>
      <button class="guest-primary" :disabled="sending || !body.trim()" title="Отправить сообщение" aria-label="Отправить сообщение"><Send :size="20"/></button>
    </form>
  </section>
</template>
<script>
import { Send } from '@lucide/vue';
import api from '@/api';
import guestApi, { errorText, requestKey } from '@/guestApi';
export default {
  components: { Send }, props: { reservationId: { type: Number, required: true }, admin: Boolean },
  data() { return { items: [], body: '', error: '', loading: false, sending: false, timer: null, requestKey: '', pendingBody: '', stopped: false }; },
  computed: { client() { return this.admin ? api : guestApi; }, endpoint() { return `${this.admin ? '/guest-admin' : '/guest'}/reservations/${this.reservationId}/messages`; } },
  mounted() { this.refresh(); }, beforeUnmount() { this.stopped = true; clearTimeout(this.timer); },
  methods: {
    async refresh() {
      if (this.loading || this.stopped) return;
      this.loading = true;
      try {
        if (!document.hidden) {
          const result = await this.client.get(this.endpoint, { params: { after_id: this.items.at(-1)?.id || 0 } });
          if (this.stopped) return;
          const nearBottom = !this.items.length || this.$refs.messages.scrollHeight - this.$refs.messages.scrollTop - this.$refs.messages.clientHeight < 80;
          this.items.push(...result.data); this.error = '';
          if (nearBottom && result.data.length) this.$nextTick(() => { if (this.$refs.messages) this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight; });
        }
      } catch (error) { this.error = errorText(error); }
      finally { this.loading = false; if (!this.stopped) { clearTimeout(this.timer); this.timer = setTimeout(this.refresh, 5000); } }
    },
    async send() {
      if (!this.body.trim() || this.sending) return;
      this.sending = true;
      if (this.pendingBody !== this.body || !this.requestKey) { this.requestKey = requestKey(); this.pendingBody = this.body; }
      try {
        await this.client.post(this.endpoint, { body: this.body, request_key: this.requestKey });
        this.body = ''; this.requestKey = ''; await this.refresh();
      } catch (error) { this.error = errorText(error); }
      finally { this.sending = false; }
    }
  }
};
</script>
