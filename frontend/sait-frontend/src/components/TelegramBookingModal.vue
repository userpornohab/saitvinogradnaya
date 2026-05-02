<template>
  <transition name="tg-modal-fade">
    <div
      v-if="modelValue"
      class="tg-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="tg-modal-title"
      @click.self="close"
      @keydown.esc="close"
    >
      <div class="tg-modal-card" tabindex="-1" ref="card">
        <button class="tg-modal-close" aria-label="Закрыть" @click="close">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>

        <div class="tg-modal-header">
          <h3 id="tg-modal-title" class="tg-modal-title">Подтверждение бронирования</h3>
          <p class="tg-modal-sub">Проверьте детали бронирования и свяжитесь с нами удобным способом.</p>
        </div>

        <dl class="tg-modal-details">
          <div class="tg-row">
            <dt>Дата заезда</dt>
            <dd>{{ formatHumanDate(bookingData.checkin) }}</dd>
          </div>
          <div class="tg-row">
            <dt>Дата выезда</dt>
            <dd>{{ formatHumanDate(bookingData.checkout) }}</dd>
          </div>
          <div class="tg-row">
            <dt>Гостей</dt>
            <dd>{{ bookingData.guests }}</dd>
          </div>
          <div class="tg-row" v-if="nights > 0">
            <dt>Ночей</dt>
            <dd>{{ nights }}</dd>
          </div>
          <div class="tg-row tg-row--accent">
            <dt>Итоговая стоимость</dt>
            <dd>{{ formatMoney(bookingData.price) }} ₽</dd>
          </div>
          <div class="tg-row tg-row--prepay">
            <dt>
              Предоплата
              <span class="tg-hint">(1 ночь)</span>
            </dt>
            <dd>{{ formatMoney(prepayment) }} ₽</dd>
          </div>
        </dl>

        <div class="tg-actions">
          <a class="tg-btn tg-btn--call" href="tel:+79788028912">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
            Позвонить
          </a>

          <div class="tg-btn-row">
            <a
              class="tg-btn tg-btn--telegram"
              :href="telegramLink"
              target="_blank"
              rel="noopener noreferrer"
              @click="onTelegramClick"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M9.999 15.2L9.85 18.9c.21 0 .3-.09.41-.2l2-1.9 4.13 3.02c.76.42 1.3.2 1.5-.7l2.72-12.74c.27-1.19-.43-1.66-1.17-1.39L2.33 10.16c-1.17.47-1.15 1.13-.2 1.43l4.37 1.36 10.14-6.4c.48-.3.91-.13.55.18L9.999 15.2z"/>
              </svg>
              Telegram
            </a>
            <a class="tg-btn tg-btn--whatsapp" href="https://wa.me/79788028912" target="_blank" rel="noopener noreferrer">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="ffffff" aria-hidden="true">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.1-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.241-.579-.487-.5-.67-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
              Max
            </a>
          </div>
        </div>

        <p class="tg-disclaimer">
          Выберите удобный способ связи.
        </p>
      </div>
    </div>
  </transition>
</template>

<script>
import { buildTelegramBookingLink } from '@/utils/telegramLink';

export default {
  name: 'TelegramBookingModal',
  props: {
    modelValue: { type: Boolean, required: true },
    bookingData: {
      type: Object,
      required: true,
      // ожидается: { checkin, checkout, guests, price, prepay?, roomId? }
    },
    botUsername: {
      type: String,
      default: () => process.env.VUE_APP_TELEGRAM_BOT || '',
    },
  },
  emits: ['update:modelValue', 'telegram-click'],

  computed: {
    nights() {
      const { checkin, checkout } = this.bookingData || {};
      if (!checkin || !checkout) return 0;
      const a = new Date(checkin); a.setHours(0,0,0,0);
      const b = new Date(checkout); b.setHours(0,0,0,0);
      return Math.max(0, Math.round((b - a) / (1000 * 60 * 60 * 24)));
    },
    prepayment() {
      const explicit = Number(this.bookingData?.prepay);
      if (explicit > 0) return Math.round(explicit);
      // fallback: средняя цена за ночь
      if (this.nights > 0 && this.bookingData?.price) {
        return Math.round(Number(this.bookingData.price) / this.nights);
      }
      return 0;
    },
    telegramLink() {
      return buildTelegramBookingLink({
        botUsername: this.botUsername,
        checkin: this.bookingData?.checkin,
        checkout: this.bookingData?.checkout,
        guests: this.bookingData?.guests,
        price: this.bookingData?.price,
        prepay: this.prepayment,
        roomId: this.bookingData?.roomId,
      });
    },
  },

  watch: {
    modelValue(val) {
      if (val) {
        document.body.style.overflow = 'hidden';
        this.$nextTick(() => this.$refs.card?.focus());
        window.addEventListener('keydown', this.onKeydown);
      } else {
        document.body.style.overflow = '';
        window.removeEventListener('keydown', this.onKeydown);
      }
    },
  },

  beforeUnmount() {
    document.body.style.overflow = '';
    window.removeEventListener('keydown', this.onKeydown);
  },

  methods: {
    close() {
      this.$emit('update:modelValue', false);
    },
    onKeydown(e) {
      if (e.key === 'Escape') this.close();
    },
    onTelegramClick() {
      this.$emit('telegram-click', this.telegramLink);
      // Закрываем модалку с небольшой задержкой, чтобы переход успел открыться
      setTimeout(() => this.close(), 150);
    },
    formatMoney(value) {
      const num = Number(value) || 0;
      return Math.round(num).toLocaleString('ru-RU');
    },
    formatHumanDate(date) {
      if (!date) return '—';
      const d = date instanceof Date ? date : new Date(date);
      if (Number.isNaN(d.getTime())) return '—';
      return d.toLocaleDateString('ru-RU', {
        day: '2-digit', month: 'long', year: 'numeric',
      });
    },
  },
};
</script>

<style scoped>
.tg-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 2500;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overscroll-behavior: contain;
}

.tg-modal-card {
  position: relative;
  width: 100%;
  max-width: 440px;
  background: #fff;
  border-radius: 22px;
  padding: 32px 28px 24px;
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.25);
  outline: none;
}

.tg-modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #f1f5f9;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}
.tg-modal-close:hover { background: #e2e8f0; color: #0f172a; }

.tg-modal-header {
  text-align: center;
  margin-bottom: 22px;
}
.tg-modal-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, #229ED9 0%, #2AABEE 100%);
  box-shadow: 0 10px 20px rgba(34, 158, 217, 0.35);
}
.tg-modal-title {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}
.tg-modal-sub {
  margin: 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.5;
}

.tg-modal-details {
  margin: 0 0 22px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.tg-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  font-size: 14px;
}
.tg-row dt {
  color: #64748b;
  font-weight: 500;
}
.tg-row dd {
  margin: 0;
  color: #0f172a;
  font-weight: 600;
  text-align: right;
}
.tg-row--accent {
  padding-top: 10px;
  border-top: 1px dashed #cbd5e1;
}
.tg-row--accent dd { font-size: 18px; color: #0f172a; }
.tg-row--prepay dd { color: #2563eb; }
.tg-hint {
  margin-left: 4px;
  color: #94a3b8;
  font-weight: 400;
  font-size: 12px;
}

.tg-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 8px;
}

.tg-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px 18px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  border-radius: 12px;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.tg-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.tg-btn:active { transform: translateY(0); }

/* Большая кнопка Позвонить */
.tg-btn--call {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 10px 22px rgba(16, 185, 129, 0.35);
  font-size: 17px;
  padding: 16px 20px;
}

.tg-btn--call:hover {
  box-shadow: 0 14px 28px rgba(16, 185, 129, 0.45);
}

/* Ряд маленьких кнопок */
.tg-btn-row {
  display: flex;
  gap: 10px;
}

.tg-btn-row .tg-btn {
  flex: 1;
  padding: 12px 14px;
  font-size: 14px;
}

/* Telegram */
.tg-btn--telegram {
  background: linear-gradient(135deg, #229ED9 0%, #2AABEE 100%);
  box-shadow: 0 8px 18px rgba(34, 158, 217, 0.3);
}

.tg-btn--telegram:hover {
  box-shadow: 0 12px 24px rgba(34, 158, 217, 0.4);
}

/* WhatsApp */
.tg-btn--whatsapp {
  background: linear-gradient(135deg, #2531d3 0%, #12478c 100%);
  box-shadow: 0 8px 18px rgba(37, 40, 211, 0.555);
}

.tg-btn--whatsapp:hover {
  box-shadow: 0 12px 24px rgba(52, 55, 243, 0.555);
}

.tg-disclaimer {
  margin: 14px 0 0;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.5;
  text-align: center;
}

.tg-modal-fade-enter-active,
.tg-modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.tg-modal-fade-enter-active .tg-modal-card,
.tg-modal-fade-leave-active .tg-modal-card {
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}
.tg-modal-fade-enter-from,
.tg-modal-fade-leave-to {
  opacity: 0;
}
.tg-modal-fade-enter-from .tg-modal-card,
.tg-modal-fade-leave-to .tg-modal-card {
  transform: translateY(12px) scale(0.98);
}

@media (max-width: 480px) {
  .tg-modal-card { padding: 26px 20px 20px; border-radius: 18px; }
  .tg-modal-title { font-size: 18px; }
  .tg-cta { font-size: 15px; }
}
</style>
