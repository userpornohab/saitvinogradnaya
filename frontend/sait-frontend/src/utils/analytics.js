import api from '@/api';

export function trackEvent(eventType, { roomId = null, path = window.location.pathname } = {}) {
  return api.post('/analytics/events', {
    event_type: eventType,
    room_id: roomId ? Number(roomId) : null,
    path,
  }).catch(() => {});
}
