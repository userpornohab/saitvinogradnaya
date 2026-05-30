import { API_BASE_URL } from '@/api';

const SITE_NAME = 'Виноградная Лоза';
const DEFAULT_TITLE = `${SITE_NAME} - гостевой дом в Крыму`;
const DEFAULT_DESCRIPTION = 'Уютный гостевой дом на южном берегу Крыма: номера, двор, пляж рядом и бронирование онлайн.';
const DEFAULT_IMAGE = 'https://vinegrape.ru/favicon.png';

export function slugifyRu(value) {
  const map = {
    а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'e', ж: 'zh', з: 'z',
    и: 'i', й: 'y', к: 'k', л: 'l', м: 'm', н: 'n', о: 'o', п: 'p', р: 'r',
    с: 's', т: 't', у: 'u', ф: 'f', х: 'h', ц: 'c', ч: 'ch', ш: 'sh',
    щ: 'sch', ъ: '', ы: 'y', ь: '', э: 'e', ю: 'yu', я: 'ya'
  };

  return String(value || '')
    .toLowerCase()
    .split('')
    .map(char => map[char] ?? char)
    .join('')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80) || 'room';
}

export function getRoomPath(room) {
  const slug = slugifyRu(room?.title);
  return `/rooms/${room.id}-${slug}`;
}

function setMetaAttribute(selector, attrName, attrValue, content) {
  let tag = document.head.querySelector(selector);
  if (!tag) {
    tag = document.createElement('meta');
    const [, value] = selector.match(/\[(?:name|property)="([^"]+)"\]/) || [];
    tag.setAttribute(attrName, value);
    document.head.appendChild(tag);
  }
  tag.setAttribute(attrValue, content);
}

export function setPageMeta({
  title = DEFAULT_TITLE,
  description = DEFAULT_DESCRIPTION,
  image = DEFAULT_IMAGE,
  url = window.location.href,
  type = 'website'
} = {}) {
  document.title = title;

  setMetaAttribute('meta[name="description"]', 'name', 'content', description);
  setMetaAttribute('meta[property="og:type"]', 'property', 'content', type);
  setMetaAttribute('meta[property="og:title"]', 'property', 'content', title);
  setMetaAttribute('meta[property="og:description"]', 'property', 'content', description);
  setMetaAttribute('meta[property="og:image"]', 'property', 'content', image);
  setMetaAttribute('meta[property="og:url"]', 'property', 'content', url);
  setMetaAttribute('meta[name="twitter:title"]', 'name', 'content', title);
  setMetaAttribute('meta[name="twitter:description"]', 'name', 'content', description);
  setMetaAttribute('meta[name="twitter:image"]', 'name', 'content', image);

  let canonical = document.head.querySelector('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement('link');
    canonical.setAttribute('rel', 'canonical');
    document.head.appendChild(canonical);
  }
  canonical.setAttribute('href', url);
}

export function absoluteMediaUrl(path) {
  if (!path) return DEFAULT_IMAGE;
  return path.startsWith('http') ? path : `${API_BASE_URL}${path}`;
}

export { DEFAULT_TITLE, DEFAULT_DESCRIPTION, DEFAULT_IMAGE };
