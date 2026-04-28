/**
 * Утилиты для формирования deep-link в Telegram-бот.
 *
 * Формат итоговой ссылки:
 *   https://t.me/<bot_username>?start=<payload>
 *
 * Где <payload> — URL-safe base64 строки вида:
 *   checkin=YYYY-MM-DD&checkout=YYYY-MM-DD&guests=N&price=XXX&prepay=YYY
 *
 * Telegram разрешает в параметре start только [A-Za-z0-9_-], максимум 64 символа,
 * поэтому используем именно URL-safe base64 без '=' в конце.
 */

/**
 * Преобразует объект параметров в query-строку (без префикса '?').
 * Пропускает undefined/null значения.
 * @param {Object} params
 * @returns {string}
 */
function toQueryString(params) {
  return Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
    .join('&');
}

/**
 * URL-safe base64-кодирование UTF-8 строки.
 * @param {string} str
 * @returns {string}
 */
function encodeBase64Url(str) {
  // btoa работает с latin1, поэтому сначала преобразуем UTF-8 → latin1
  const utf8 = unescape(encodeURIComponent(str));
  return btoa(utf8)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
}

/**
 * Форматирует Date в 'YYYY-MM-DD'.
 * @param {Date|string|null|undefined} date
 * @returns {string}
 */
function formatDateISO(date) {
  if (!date) return '';
  const d = date instanceof Date ? date : new Date(date);
  if (Number.isNaN(d.getTime())) return '';
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/**
 * Компактная дата 'YYYYMMDD' — на 2 символа короче ISO.
 * @param {Date|string|null|undefined} date
 * @returns {string}
 */
function formatDateCompact(date) {
  const iso = formatDateISO(date);
  return iso ? iso.replace(/-/g, '') : '';
}

/**
 * Формирует payload-строку (без base64-кодирования) для бота.
 * @param {Object} data
 * @param {Date|string} data.checkin
 * @param {Date|string} data.checkout
 * @param {number} data.guests
 * @param {number} data.price        Итоговая цена
 * @param {number} [data.prepay]     Предоплата (1 ночь)
 * @param {number|string} [data.roomId]
 * @returns {string}
 */
export function buildBookingPayload({ checkin, checkout, guests, price, prepay, roomId }) {
  // Короткие ключи и YYYYMMDD — чтобы итоговый base64 влез в лимит
  // Telegram start-параметра (64 символа).
  return toQueryString({
    c: formatDateCompact(checkin),
    o: formatDateCompact(checkout),
    g: guests,
    p: price,
    d: prepay,
    r: roomId,
  });
}

/**
 * Полностью формирует ссылку на Telegram-бот.
 * @param {Object} opts
 * @param {string} opts.botUsername      Username бота (без @)
 * @param {Date|string} opts.checkin
 * @param {Date|string} opts.checkout
 * @param {number} opts.guests
 * @param {number} opts.price
 * @param {number} [opts.prepay]
 * @param {number|string} [opts.roomId]
 * @returns {string}
 */
export function buildTelegramBookingLink({ botUsername, checkin, checkout, guests, price, prepay, roomId }) {
  if (!botUsername) {
    // eslint-disable-next-line no-console
    console.warn('[telegramLink] botUsername не задан. Укажите VUE_APP_TELEGRAM_BOT в .env');
  }
  const rawPayload = buildBookingPayload({ checkin, checkout, guests, price, prepay, roomId });
  const encoded = encodeBase64Url(rawPayload);
  if (encoded.length > 64) {
    // eslint-disable-next-line no-console
    console.warn(
      `[telegramLink] payload ${encoded.length} символов > 64, Telegram отбросит параметр. ` +
      `Raw: ${rawPayload}`,
    );
  }
  return `https://t.me/${botUsername}?start=${encoded}`;
}
