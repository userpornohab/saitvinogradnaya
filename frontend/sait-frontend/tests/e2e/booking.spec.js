const { test, expect } = require('@playwright/test');

const room = {
  id: 1, title: 'Семейный номер', title_dop: '', description: 'Номер для семейного отдыха',
  max_guests: 4, number_of_rooms: 1, floor: 2, area: 25, amenities: [], bed_options: [],
  photos: [{ id: 1, room_id: 1, is_main: true, sort_order: 0, url: '/static/photo.webp' }],
  price_periods: [{ id: 1, room_id: 1, number_of_guests: 4, start_date: '2030-06-01', end_date: '2030-08-31', price: 3000 }]
};

async function fixtures(page, busy = false) {
  await page.clock.setFixedTime(new Date('2030-06-01T12:00:00Z'));
  await page.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin === 'http://127.0.0.1:8097') return route.continue();
    const path = url.pathname.replace(/\/$/, '');
    let json;
    if (path === '/site') json = { main_description: 'Гостевой дом', main_photo: '', courtyard_photos: [], testimonials: [], testimonial_images: [], faqs: [] };
    else if (path === '/rooms' || path === '/rooms/admin' || path === '/rooms/filter') json = [room];
    else if (path === '/rooms/1') json = room;
    else if (path === '/bookings/rooms/1') json = busy ? [{ room_id: 1, check_in_date: '2030-06-21', check_out_date: '2030-06-23' }] : [];
    else if (path === '/users/me') json = { id: 1, email: 'admin@example.test', is_superuser: true };
    else if (path === '/token') json = { access_token: 'test-token', token_type: 'bearer' };
    else if (path === '/guest/auth/session') return route.fulfill({ status: 401, json: { detail: 'Sign in' } });
    else if (path === '/guest/booking-policy') json = { available: true, enabled: true, is_test: true, hold_minutes: 20 };
    else if (path === '/analytics/events') json = {};
    else if (path === '/bookings/booking-stats') json = {
      period: { start_date: '2030-05-25', end_date: '2030-06-01' }, filter: { room_title: 'Все комнаты' },
      statistics: { total_bookings: 1, total_income: 9000, total_guests: 2, total_nights: 3, avg_duration: 3, avg_check: 9000, occupancy_rate: 37.5 },
      previous_period: { changes: {} }, monthly_income: [{ month: '2030-06', income: 9000 }],
      monthly_occupancy: [{ month: '2030-06', occupancy_rate: 37.5 }],
      room_statistics: [1, 2].map(id => ({ room_id: id, room_title: room.title + id, booking_count: 1, total_income: 9000, total_guests: 2 }))
    };
    else if (path === '/analytics/stats') json = {
      totals: { room_clicks: 1, booking_clicks: 1, phone_clicks: 0 },
      daily: [{ date: '2030-06-01', room_click: 1, booking_click: 1, phone_click: 0 }],
      room_statistics: [1, 2].map(id => ({ room_id: id, room_title: room.title + id, room_clicks: 1, booking_clicks: 1, phone_clicks: 0 }))
    };
    else if (path.startsWith('/static/')) return route.fulfill({ status: 200, contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="#a6bca4"/></svg>' });
    else if (['/site/faqs', '/amenities', '/bed-options'].includes(path)) json = [];
    else return route.abort();
    return route.fulfill({ json });
  });
}

test('search transfers dates, calculates price and opens booking details', async ({ page }) => {
  await fixtures(page);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await page.locator('#startDate').click();
  const month = page.locator('.calendars.visible .calendar-wrapper').first();
  await month.locator('.day').filter({ hasText: /^20$/ }).click();
  await month.locator('.day').filter({ hasText: /^23$/ }).click();
  const search = page.waitForRequest(request => request.url().includes('/rooms/filter'));
  await page.locator('#findBtn').click();
  expect((await search).postDataJSON()).toMatchObject({ check_in_date: '2030-06-20', check_out_date: '2030-06-23' });
  await page.locator('.room_serch .room').first().click();
  await expect(page).toHaveURL(/\/rooms\/1-/);
  await expect(page.locator('.booking-form .total-price')).toContainText(/9\s*000/);
  await expect(page.locator('.book-button')).toBeEnabled();
  await page.locator('.book-button').click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('dialog').getByRole('button', { name: 'Войти', exact: true })).toBeVisible();
  expect(errors).toEqual([]);
  await page.screenshot({ path: test.info().outputPath('booking.png'), fullPage: true });
});

test('occupied nights block booking even from a direct URL', async ({ page }) => {
  await fixtures(page, true);
  await page.goto('/rooms/1-semeynyy-nomer?start=2030-06-20&end=2030-06-24&guests=1');
  await expect(page.locator('.book-button')).toBeDisabled();
  await page.locator('.booking-form .date-inputs').click();
  const day = page.locator('.datepicker-wrapper .calendar-wrapper').first().locator('.day').filter({ hasText: /^21$/ });
  await expect(day).toHaveClass(/disabled/);
  await expect(page.locator('.book-button')).toBeDisabled();
  await expect(page.locator('.booking-form .total-price')).toHaveCount(0);
});

test('booking waits for availability and remains blocked on a loading failure', async ({ page }) => {
  await fixtures(page);
  let release;
  const pending = new Promise(resolve => { release = resolve; });
  await page.route('**/bookings/rooms/1', async route => {
    await pending;
    await route.fulfill({ status: 503, json: { detail: 'Unavailable' } });
  });
  await page.goto('/rooms/1-semeynyy-nomer?start=2030-06-20&end=2030-06-24&guests=1');
  await expect(page.locator('.book-button')).toBeDisabled();
  await expect(page.getByRole('status')).toContainText('Проверяем занятость');
  release();
  await expect(page.getByRole('status')).toContainText('Не удалось проверить занятость');
  await expect(page.locator('.book-button')).toBeDisabled();
});

test('anonymous admin visit redirects to login; successful login opens rooms', async ({ page }) => {
  await fixtures(page);
  await page.goto('/admin/rooms');
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute('content', 'noindex, nofollow');
  await page.locator('input[type="email"]').fill('admin@example.test');
  await page.locator('input[type="password"]').fill('test-password');
  await page.getByRole('button', { name: 'Войти', exact: true }).click();
  await expect(page).toHaveURL(/\/admin\/rooms$/);
  await expect(page.getByText('Список номеров', { exact: true })).toBeVisible();
  await expect(page.locator('.room-list')).toContainText(room.title);
});

test('statistics charts load on demand after admin login', async ({ page }) => {
  await fixtures(page);
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/login');
  await page.locator('input[type="email"]').fill('admin@example.test');
  await page.locator('input[type="password"]').fill('test-password');
  await page.getByRole('button', { name: 'Войти', exact: true }).click();
  await expect(page).toHaveURL(/\/admin\/rooms$/);
  await page.goto('/admin/stats');
  await expect(page.locator('.apexcharts-canvas').first()).toBeVisible();
  await expect(page.locator('.apexcharts-canvas')).toHaveCount(6);
  expect(errors).toEqual([]);
});
