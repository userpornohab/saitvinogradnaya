const { test, expect } = require('@playwright/test');

async function fixture(page, signedIn = true) {
  const state = { signedIn, messages: [], saved: null, created: null };
  const user = { id: 1, email: 'guest@example.com', name: 'Анна', phone: '+79990000001', email_verified: true };
  const policy = { enabled: true, available: true, deposit_mode: 'percent', deposit_percent: 30, hold_minutes: 20,
    terms_url: '/terms', privacy_url: '/privacy', terms_version: '1', is_test: true, configuration_errors: [] };
  const room = { id: 1, title: 'Семейный номер', description: 'Светлый номер для семейного отдыха', max_guests: 4,
    number_of_rooms: 1, floor: 2, area: 25, amenities: [], bed_options: [],
    photos: [{ id: 1, room_id: 1, is_main: true, url: '/static/photo.webp' }],
    price_periods: [{ id: 1, room_id: 1, number_of_guests: 4, start_date: '2030-06-01', end_date: '2030-08-31', price: 3000 }] };
  state.reservation = { id: 31, room_id: 1, room_title: room.title, guest_name: user.name, guest_phone: user.phone,
    guests: 2, check_in_date: '2030-06-10', check_out_date: '2030-06-13', total_kopeks: 900000, deposit_kopeks: 270000,
    deposit_rule: '30%', paid_kopeks: 0, remaining_kopeks: 900000, status: 'awaiting_payment', is_test: true,
    expires_at: '2030-06-01T13:00:00Z', terms_url: '/terms', terms_version: '1', chat_available: false };
  await page.clock.setFixedTime(new Date('2030-06-01T12:00:00Z'));
  await page.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin === 'http://127.0.0.1:8097') return route.continue();
    if (url.hostname === 'auth.robokassa.ru') return route.fulfill({ contentType: 'text/javascript', body: 'window.Robokassa = { Render: function(params) { window.testPayment = params; } };' });
    const path = url.pathname.replace(/\/$/, '');
    const method = route.request().method();
    const payload = () => route.request().postDataJSON();
    let json;
    if (path === '/guest/auth/session') {
      if (!state.signedIn) return route.fulfill({ status: 401, json: { detail: 'Войдите' } });
      json = { user, csrf: 'fixture-csrf' };
    } else if (path === '/guest/auth/login') { state.signedIn = true; json = { user, csrf: 'fixture-csrf' }; }
    else if (['/guest/auth/register', '/guest/auth/verify', '/guest/auth/reset', '/guest/auth/forgot'].includes(path)) json = { message: 'Письмо отправлено или действие выполнено' };
    else if (path === '/guest/auth/logout') { state.signedIn = false; json = { ok: true }; }
    else if (path === '/guest/booking-policy' || path === '/guest-admin/payment-settings') {
      if (method === 'PUT') { state.saved = payload(); Object.assign(policy, state.saved); }
      json = policy;
    } else if (path === '/guest/quote') json = { total_kopeks: 900000, deposit_kopeks: 270000, deposit_rule: '30%', terms_version: '1', room_title: room.title };
    else if (path === '/guest/reservations') {
      if (method === 'POST') { state.created = payload(); json = state.reservation; }
      else json = { items: [state.reservation], total: 1 };
    } else if (path === '/guest-admin/reservations') json = { items: [state.reservation], total: 1 };
    else if (path === '/guest/reservations/31') json = state.reservation;
    else if (path === '/guest/reservations/31/payment') json = { action: 'https://auth.robokassa.ru/Merchant/Index.aspx', params: { MerchantLogin: 'test-store', InvId: 31, OutSum: '2700.00', SignatureValue: 'signed-by-server', IsTest: 1 } };
    else if (path.endsWith('/reservations/31/messages')) {
      if (method === 'POST') { state.messages.push({ id: state.messages.length + 1, body: payload().body, from_admin: path.startsWith('/guest-admin'), created_at: '2030-06-01T12:01:00Z' }); json = { ok: true }; }
      else json = state.messages.filter(item => item.id > Number(url.searchParams.get('after_id') || 0));
    } else if (path === '/rooms/1') json = room;
    else if (path === '/rooms') json = [room];
    else if (path === '/bookings/rooms/1' || path === '/site/faqs') json = [];
    else if (path === '/users/me') json = { id: 2, is_superuser: true, email: 'admin@example.com' };
    else if (path === '/token') json = { access_token: 'admin-test' };
    else if (path === '/site') json = { courtyard_photos: [], testimonials: [], faqs: [] };
    else if (path === '/analytics/events') json = {};
    else if (path.startsWith('/static/')) return route.fulfill({ contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="#bdd0bc"/></svg>' });
    else return route.abort();
    return route.fulfill({ json });
  });
  return state;
}

test('checkout shows server deposit, opens SBP widget, then chat follows server confirmation', async ({ page }) => {
  const state = await fixture(page);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/rooms/1-semeynyy-nomer?start=2030-06-10&end=2030-06-13&guests=2');
  await page.locator('.book-button').click();
  const modal = page.getByRole('dialog');
  await expect(modal).toContainText(/2\s*700/);
  await modal.getByRole('checkbox').check();
  await modal.getByRole('button', { name: 'Перейти к оплате' }).click();
  await expect(page).toHaveURL(/account\?reservation=31/);
  expect(state.created.quoted_deposit_kopeks).toBe(270000);
  expect(state.created.accepted_terms).toBe(true);
  await page.getByRole('button', { name: 'Оплатить через СБП' }).click();
  await expect.poll(() => page.evaluate(() => window.testPayment?.OutSum)).toBe('2700.00');
  const params = await page.evaluate(() => window.testPayment);
  expect(JSON.parse(params.Settings).PaymentMethods).toEqual(['SBP']);
  await expect(page.locator('.guest-chat')).toHaveCount(0);
  state.reservation = { ...state.reservation, status: 'confirmed', paid_kopeks: 270000, remaining_kopeks: 630000, chat_available: true };
  await expect(page.locator('.guest-chat')).toBeVisible({ timeout: 12000 });
  await page.getByRole('textbox', { name: 'Сообщение' }).fill('Приедем в 18:00. <script>window.unwanted = true</script>');
  await page.getByRole('button', { name: 'Отправить сообщение' }).click();
  await expect(page.locator('.guest-message')).toContainText('Приедем в 18:00.');
  expect(await page.evaluate(() => window.unwanted)).toBeUndefined();
  expect(await page.evaluate(() => localStorage.getItem('access_token'))).toBeNull();
  expect(errors).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.screenshot({ path: test.info().outputPath('guest-account.png'), fullPage: true });
});

test('guest can register and return to login without admin credentials', async ({ page }) => {
  await fixture(page, false);
  await page.goto('/account');
  await page.getByRole('tab', { name: 'Регистрация' }).click();
  await page.getByLabel('Ваше имя').fill('Анна');
  await page.getByLabel('Электронная почта').fill('guest@example.com');
  await page.locator('input[autocomplete="new-password"]').fill('a-long-secure-password');
  await page.getByRole('button', { name: 'Зарегистрироваться', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('Письмо');
  await page.getByRole('tab', { name: 'Вход', exact: true }).click();
  await page.locator('input[autocomplete="current-password"]').fill('a-long-secure-password');
  await page.getByRole('button', { name: 'Войти', exact: true }).click();
  await expect(page.locator('.guest-reservation')).toContainText('Семейный номер');
});

test('admin can save percentage settings and answer a guest', async ({ page }) => {
  const state = await fixture(page);
  state.reservation.status = 'confirmed'; state.reservation.chat_available = true;
  await page.addInitScript(() => localStorage.setItem('access_token', 'admin-test'));
  await page.goto('/admin/online');
  await page.getByRole('tab', { name: 'Предоплата', exact: true }).click();
  await page.getByLabel('Предоплата, %').fill('40');
  await page.getByRole('button', { name: 'Сохранить настройки' }).click();
  await expect(page.getByRole('status')).toContainText('Настройки сохранены');
  expect(state.saved.deposit_percent).toBe(40);
  await page.getByRole('tab', { name: 'Бронирования', exact: true }).click();
  await page.getByRole('textbox', { name: 'Сообщение' }).fill('Здравствуйте! Ваш номер будет готов.');
  await page.getByRole('button', { name: 'Отправить сообщение' }).click();
  await expect(page.locator('.guest-message')).toContainText('Ваш номер будет готов');
  expect(state.messages[0].from_admin).toBe(true);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.screenshot({ path: test.info().outputPath('admin-online.png'), fullPage: true });
});

test('verification secret is removed from the address bar before submission', async ({ page }) => {
  await fixture(page, false);
  await page.goto('/account#action=verify&token=one-use-secret-for-email-verification');
  await expect(page).toHaveURL(/\/account$/);
  await page.getByRole('button', { name: 'Подтвердить почту', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('действие выполнено');
});
