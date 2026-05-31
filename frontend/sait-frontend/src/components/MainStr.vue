<template>
  <div class="home-page">
    <!-- 1. Hero Block с формой поиска -->
    <section id="hero" class="hero" :style="heroBackgroundStyle">
      <div class="hero-overlay"></div>
      <div class="hero-content container">
        <h1 class="hero-title">Виноградная Лоза</h1>
        <p class="hero-subtitle">
          Гостеприимство и уют ждут вас в нашем гостевом домике на южном берегу Крыма
        </p>
        <SearchForm
          @search="handleSearch"
          :fetchAllRooms="fetchAllRooms"
          @clire="Clire"
        />
      </div>
    </section>

    <!-- 2. About Us + Advantages (объединённая секция) -->
    <section id="about" class="section">
      <div class="container">
        <div class="about-grid">
          <div class="about-image">
            <img
              :src="aboutImageSrc"
              alt="Территория гостевого дома"
              loading="lazy"
            />
          </div>
          <div class="about-content">
            <h2 class="section-title">О нашем гостевом доме</h2>
            <p class="about-text">{{ siteInfo?.main_description || '' }}</p>
          </div>
        </div>

        <div class="about-advantages">
          <div class="advantages-grid">
            <div class="advantage-card" v-for="(adv, index) in advantages" :key="index">
              <div class="advantage-icon-wrap">
                <img :src="adv.icon" :alt="adv.title" loading="lazy" />
              </div>
              <div class="advantage-text">
                <h3 class="advantage-title">{{ adv.title }}</h3>
                <p class="advantage-desc">{{ adv.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. Rooms Block -->
    <section id="rooms" class="section section--gray">
      <div class="container">
        <h2 class="section-title text-center">Наши номера</h2>

        <RoomComponent
          :pfoto_dvor="getPhotoDvor"
          :rooms="filteredRooms"
          :url_data="urldata"
          :is-loading="isLoading"
        />
      </div>
    </section>

    <!-- 5. Territory Gallery -->
    <section id="territory" class="section territory-section">
      <div class="container">
        <div class="territory-header">
          <h2 class="section-title">Места, где проходит отпуск</h2>
          <span class="eyebrow">Территория и отдых</span>
        </div>

        <div v-if="territoryGroups.length" class="territory-groups">
          <article
            v-for="group in territoryGroups"
            :key="group.category"
            class="territory-group-card"
          >
            <div class="territory-group-main">
              <img :src="activeTerritoryPhoto(group).fullUrl" :alt="group.label" class="territory-image" loading="lazy" />
              <div class="territory-caption">
                <h3>{{ group.label }}</h3>
                <p>{{ group.description }}</p>
              </div>
            </div>
            <div v-if="group.photos.length > 1" class="territory-thumbs">
              <button
                v-for="photo in group.photos.slice(0, 3)"
                :key="photo.id"
                type="button"
                class="territory-thumb"
                :class="{ 'territory-thumb--active': activeTerritoryPhoto(group).id === photo.id }"
                @click="setTerritoryPhoto(group.category, photo.id)"
              >
                <img :src="photo.fullUrl" :alt="group.label" loading="lazy" />
              </button>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 5. FAQ Block -->
    <section id="faq" class="section">
      <div class="container">
        <div class="faq-header">
          <h2 class="section-title faq-title">Часто задаваемые вопросы</h2>
          <span class="eyebrow">Вопрос — ответ</span>
        </div>
          
        <div class="faq-layout">
          <aside class="faq-illustration" aria-hidden="true">
            <img :src="faqImage" alt="" class="faq-illustration-img" />
          </aside>

          <div class="faq-content">

            <div class="faq-list">
              <div
                v-for="(faq, index) in siteInfo?.faqs || []"
                :key="faq.id"
                class="faq-item"
              >
                <button class="faq-question" @click="toggleFaq(index)">
                  <span class="faq-question-text">{{ faq.question }}</span>
                  <span class="faq-icon" :class="{ 'active': openFaqIndex === index }">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M6 9l6 6 6-6"/>
                    </svg>
                  </span>
                </button>
                <transition name="faq-expand">
                  <div v-if="openFaqIndex === index" class="faq-answer">
                    {{ faq.answer }}
                  </div>
                </transition>
              </div>
              <p v-if="!siteInfo?.faqs || siteInfo.faqs.length === 0" class="text-center text-gray">
                Вопросы скоро появятся
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. How to Get Us Block + Карта -->
    <section id="directions" class="section section--gray">
      <div class="container">
        <h2 class="section-title text-center">Как добраться</h2>
        <div style="display: flex; justify-content: center;">        <span class="eyebrow" >Быстый путь</span>
</div>

        <div class="directions-grid">
          <!-- Трансфер -->
          <div class="direction-card">
            <div class="direction-icon">
              <img :src="iconTransfer" alt="" loading="lazy" />
            </div>
            <h3 class="direction-title">Трансфер</h3>
            <p class="direction-text">
              Мы организуем трансфер из аэропорта Симферополя или ж/д вокзала.
              Свяжитесь с нами заранее для заказа.
            </p>
          </div>

          <!-- Общественный транспорт -->
          <div class="direction-card">
            <div class="direction-icon">
              <img :src="iconBus" alt="" loading="lazy" />
            </div>
            <h3 class="direction-title">Общественный транспорт</h3>
            <p class="direction-text">
              Из Алушты: автобус №31 до остановки «Рыбачье».
              Из Симферополя: троллейбус до Алушты, далее автобус.
            </p>
          </div>

          <!-- На машине -->
          <div class="direction-card">
            <div class="direction-icon">
              <img :src="iconCar" alt="" loading="lazy" />
            </div>
            <h3 class="direction-title">На машине</h3>
            <p class="direction-text">
              Адрес: Алушта, с. Рыбачье, ул. Школьная 1/2.
              Бесплатная парковка на территории. Координаты: 44.6478, 34.3172
            </p>
          </div>
        </div>

        <!-- Карта -->
        <div class="map-container">
          <iframe
            src="https://yandex.ru/map-widget/v1/?z=12&ol=biz&oid=92950545738"
            width="100%"
            height="420"
            frameborder="0"
            allowfullscreen
            loading="lazy"
            class="map-iframe"
          ></iframe>
          
        </div>
      </div>
    </section>

    <!-- 7. Landmarks Block (Знаковые места поблизости) -->
    <section class="section landmarks-section">
      <div class="container">
        <div class="landmarks-header">
          <h2 class="section-title">Знаковые места поблизости</h2>
          <span class="eyebrow">Рядом с домом</span>
        </div>

        <div class="landmarks-grid">
          <article
            v-for="(landmark, index) in landmarks"
            :key="index"
            class="landmark-card"
            :class="[`landmark-card--${index + 1}`]"
            tabindex="0"
          >
            <img class="landmark-img" :src="landmark.image" :alt="landmark.title" loading="lazy" />
            <div class="landmark-hover">
              <span class="landmark-distance">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                {{ landmark.distance }}
              </span>
              <h3 class="landmark-title">{{ landmark.title }}</h3>
              <p class="landmark-desc">{{ landmark.desc }}</p>
            </div>
            <span class="landmark-label">{{ landmark.title }}</span>
          </article>
        </div>
      </div>
    </section>

    <!-- 8. Testimonials Block (Отзывы - слайдер) -->
    <section id="reviews" class="section section--gray reviews-section">
      <div class="container">
        <div class="reviews-header">
          <h2 class="section-title text-center">Отзывы наших гостей</h2>
          <span class="eyebrow">Впечатления гостей</span>
        </div>
        <div class="testimonials-slider" v-if="siteInfo?.testimonials?.length">
          <div class="testimonials-track" ref="testimonialsTrack">
            <article class="testimonial-card" v-for="testimonial in siteInfo.testimonials" :key="testimonial.id">
              <div class="testimonial-header">
                <img
                  v-if="getTestimonialAvatarUrl(testimonial.author_icon_url)"
                  :src="getTestimonialAvatarUrl(testimonial.author_icon_url)"
                  :alt="testimonial.author_name"
                  class="testimonial-avatar"
                />
                <span v-else class="testimonial-avatar testimonial-avatar--fallback">
                  {{ getTestimonialInitials(testimonial.author_name) }}
                </span>
                <div class="testimonial-author">
                  <strong>{{ testimonial.author_name }}</strong>
                  <span>Гость Виноградной Лозы</span>
                </div>
              </div>
              <div class="testimonial-quote-mark">“</div>
              <p
                class="testimonial-text"
                :class="{ 'testimonial-text--expanded': expandedTestimonials[testimonial.id] }"
              >
                {{ testimonial.comment }}
              </p>
              <button
                v-if="isLongTestimonial(testimonial.comment)"
                type="button"
                class="testimonial-more"
                @click="toggleTestimonial(testimonial.id)"
              >
                {{ expandedTestimonials[testimonial.id] ? 'Свернуть' : 'Читать полностью' }}
              </button>
            </article>
          </div>
        </div>
        <p v-else class="text-center text-gray">Отзывы скоро появятся</p>
      </div>
    </section>
  </div>
</template>

<script>
import SearchForm from './SearchForm.vue';
import RoomComponent from './RoomComponent.vue';
import api, { API_BASE_URL } from '@/api';
import defaultImage from '@/assets/rybache1.jpg';
import { absoluteMediaUrl, setPageMeta } from '@/utils/seo';

// Иконки преимуществ
import iconShop from '@/assets/advantages/advantage-cafe.png';
import iconPlace from '@/assets/advantages/advantage-trips.png';
import iconGames from '@/assets/advantages/advantage-water.png';
import iconBeach from '@/assets/advantages/advantage-beach.png';
import iconJur from '@/assets/advantages/advantage-landmarks.png';
import iconFootball from '@/assets/advantages/advantage-sport.png';
import iconBus from '@/assets/icons/bus-transportvehicle-svgrepo-com.svg';
import iconCar from '@/assets/icons/car-transport-navigation-svgrepo-com.svg';
import iconTransfer from '@/assets/icons/car-sedan-automobile-svgrepo-com.svg';
import landmarkSea from '@/assets/landmarks/sea.jpg';
import landmarkJurJur from '@/assets/landmarks/jurjur.jpg';
import landmarkAlushta from '@/assets/landmarks/Alushta.jpg';
import landmarkDemerdzhi from '@/assets/landmarks/demerji.jpg';
import landmarkAivaz from '@/assets/landmarks/park.jpg';
import landmarkSudak from '@/assets/landmarks/nowiy-swet.jpg';

// Иллюстрация для блока FAQ
import faqImage from '@/assets/qwshions.png';

export default {
  components: {
    SearchForm,
    RoomComponent,
  },
  data() {
    return {
      isLoading: false,
      urldata: null,
      rooms: [],
      filteredRooms: [],
      siteInfo: null,
      defaultImage: defaultImage,
      faqImage,
      iconBus,
      iconCar,
      iconTransfer,
      openFaqIndex: null,
      activeTerritoryPhotos: {},
      expandedTestimonials: {},
    };
  },
  computed: {
    heroBackgroundStyle() {
      let backgroundImage = this.defaultImage;
      if (this.siteInfo?.main_photo) {
        backgroundImage = this.siteInfo.main_photo.startsWith('http')
          ? this.siteInfo.main_photo
          : `${API_BASE_URL}${this.siteInfo.main_photo}`;
      }
      return {
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      };
    },
    getPhotoDvor() {
      const yardPhotos = this.sortedCourtyardPhotos.filter(photo => (photo.category || 'yard') === 'yard');
      return yardPhotos.length ? yardPhotos : this.sortedCourtyardPhotos.slice(1);
    },
    aboutImageSrc() {
      const yardPhotos = this.sortedCourtyardPhotos.filter(photo => (photo.category || 'yard') === 'yard');
      const photo = yardPhotos[1] || yardPhotos[0];
      return photo?.url
        ? `${API_BASE_URL}${photo.url}`
        : defaultImage;
    },
    sortedCourtyardPhotos() {
      return [...(this.siteInfo?.courtyard_photos || [])].sort((a, b) => {
        const orderDiff = (a.sort_order || 0) - (b.sort_order || 0);
        return orderDiff || a.id - b.id;
      });
    },
    advantages() {
      return [
        { icon: iconShop, title: 'Магазины и кафе', desc: 'Всё необходимое рядом' },
        { icon: iconPlace, title: 'Поездки по Крыму', desc: 'Экскурсии и маршруты' },
        { icon: iconGames, title: 'Пляжные развлечения', desc: 'Спорт и отдых на пляже' },
        { icon: iconBeach, title: 'Пляж бесплатный', desc: 'Чистый галечный пляж' },
        { icon: iconJur, title: 'Знаковые места', desc: 'Достопримечательности рядом' },
        { icon: iconFootball, title: 'Стадион и парк', desc: 'Активный отдых поблизости' },
      ];
    },
    territoryGroups() {
      const groups = [
        { category: 'kitchen', label: 'Кухня', description: 'Место для завтраков, домашней еды и спокойных вечеров' },
        { category: 'rest', label: 'Зона отдыха', description: 'Уютные уголки для семейного отдыха и разговоров после моря' },
        { category: 'yard', label: 'Двор', description: 'Территория гостевого дома, где удобно отдыхать между прогулками' },
      ];

      return groups
        .map(group => ({
          ...group,
          photos: this.sortedCourtyardPhotos
            .filter(photo => (photo.category || 'yard') === group.category)
            .map(photo => ({ ...photo, fullUrl: `${API_BASE_URL}${photo.url}` }))
        }))
        .filter(group => group.photos.length);
    },
    landmarks() {
      return [
        { title: 'Море', distance: '10 мин пешком', desc: 'Чистый галечный пляж с живописными видами на горы', image: landmarkSea },
        { title: 'Водопад Джур-Джур', distance: '20 мин на машине', desc: 'Самый полноводный водопад Крыма среди вековых буков', image: landmarkJurJur },
        { title: 'Алушта', distance: '30 мин на машине', desc: 'Город с набережными, ресторанами и аквапарком', image: landmarkAlushta },
        { title: 'Гора Демерджи', distance: '35 мин на машине', desc: 'Долина Привидений и знаменитые каменные изваяния', image: landmarkDemerdzhi },
        { title: 'Парк Айвазовское', distance: '50 мин на машине', desc: 'Ландшафтный парк с реликтовыми растениями', image: landmarkAivaz },
        { title: 'Судак и Новый Свет', distance: '40 мин на машине', desc: 'Генуэзская крепость и можжевеловые рощи', image: landmarkSudak },
      ];
    },
  },
  watch: {
    rooms: {
      immediate: true,
      handler(newRooms) {
        this.filteredRooms = [...newRooms];
      }
    }
  },
  async created() {
    setPageMeta({
      title: 'Виноградная Лоза - гостевой дом в Рыбачьем, Крым',
      description: 'Номера у моря в гостевом доме Виноградная Лоза: двор, пляж рядом, отдых с детьми и бронирование онлайн.',
      image: absoluteMediaUrl(this.siteInfo?.main_photo),
      url: window.location.origin + '/'
    });
    await this.fetchSiteInfo();
    setPageMeta({
      title: 'Виноградная Лоза - гостевой дом в Рыбачьем, Крым',
      description: 'Номера у моря в гостевом доме Виноградная Лоза: двор, пляж рядом, отдых с детьми и бронирование онлайн.',
      image: absoluteMediaUrl(this.siteInfo?.main_photo),
      url: window.location.origin + '/'
    });
    await this.fetchAllRooms();
  },
  methods: {
    activeTerritoryPhoto(group) {
      const activePhotoId = this.activeTerritoryPhotos[group.category];
      return group.photos.find(photo => photo.id === activePhotoId) || group.photos[0];
    },
    setTerritoryPhoto(category, photoId) {
      this.activeTerritoryPhotos = {
        ...this.activeTerritoryPhotos,
        [category]: photoId
      };
    },
    toggleFaq(index) {
      this.openFaqIndex = this.openFaqIndex === index ? null : index;
    },
    Clire() {
      this.urldata = null;
    },
    getTestimonialAvatarUrl(url) {
      if (!url) return '';
      return url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
    },
    getTestimonialInitials(name) {
      const cleanName = (name || 'Гость').trim();
      return cleanName.slice(0, 1).toUpperCase();
    },
    isLongTestimonial(comment) {
      return (comment || '').length > 220;
    },
    toggleTestimonial(id) {
      this.expandedTestimonials = {
        ...this.expandedTestimonials,
        [id]: !this.expandedTestimonials[id]
      };
    },
    scrollTestimonials(direction) {
      const track = this.$refs.testimonialsTrack;
      if (track) {
        const cardWidth = 340;
        track.scrollBy({ left: cardWidth * direction, behavior: 'smooth' });
      }
    },
    async fetchSiteInfo() {
      try {
        const response = await api.get('/site/');
        this.siteInfo = response.data;
      } catch (error) {
        console.error('Ошибка загрузки информации о сайте:', error);
        this.siteInfo = {};
      }
    },
    async fetchAllRooms() {
      try {
        const response = await api.get('/rooms/');
        this.rooms = response.data;
      } catch (error) {
        console.error('Ошибка загрузки комнат:', error);
      }
    },
    async handleSearch(searchData) {
      try {
        this.urldata = {
          guests: searchData.guests,
          start: searchData.check_in_date,
          end: searchData.check_out_date
        };

        this.isLoading = true;
        await new Promise(resolve => setTimeout(resolve, 300));

        const response = await api.post(
          '/rooms/filter/',
          searchData
        );

        this.filteredRooms = response.data;

        // Скролл к номерам
        this.$nextTick(() => {
          const roomsSection = document.getElementById('rooms');
          if (roomsSection) {
            roomsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });
      } catch (error) {
        console.error('Ошибка при поиске комнат:', error);
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
/* ======================================
   HERO SECTION
   ====================================== */
.hero {
  position: relative;
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* overflow: visible — чтобы выпадающий календарь мог вылезать за границы hero */
  overflow: visible;
  z-index: 1;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.45) 0%,
    rgba(0, 0, 0, 0.2) 100%
  );
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: white;
  padding: var(--spacing-3xl) var(--spacing-xl);
}

.hero-title {
  font-size: clamp(2.5rem, 5vw + 1rem, 4.5rem);
  font-weight: 700;
  color: white;
  margin-bottom: var(--spacing-md);
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: var(--text-lg);
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--spacing-xl);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  text-shadow: 0 1px 10px rgba(0, 0, 0, 0.3);
}

/* ======================================
   ABOUT SECTION
   ====================================== */
.about-grid {
  position: relative;
  display: grid;
  grid-template-columns: minmax(280px, 0.95fr) minmax(320px, 1.05fr);
  gap: clamp(24px, 4vw, 56px);
  align-items: center;
  padding: clamp(18px, 3vw, 34px);
  border: 1px solid rgba(198, 196, 253, 0.45);
  border-radius: var(--radius-2xl);
  background:
    linear-gradient(135deg, rgba(198, 196, 253, 0.18), rgba(255, 255, 255, 0.9) 42%),
    var(--color-white);
  overflow: hidden;
}

.about-grid::before {
  content: "";
  position: absolute;
  width: 180px;
  height: 180px;
  right: -70px;
  top: -90px;
  border-radius: 50%;
  border: 36px solid rgba(198, 196, 253, 0.22);
  pointer-events: none;
}

.about-image {
  position: relative;
}

.about-image::after {
  content: "";
  position: absolute;
  inset: auto 18px -14px 18px;
  height: 26px;
  background: rgba(86, 81, 216, 0.18);
  filter: blur(16px);
  border-radius: 999px;
}

.about-image img {
  width: 100%;
  height: clamp(280px, 34vw, 380px);
  object-fit: cover;
  border-radius: 28px 10px 28px 10px;
  box-shadow: 0 18px 44px rgba(24, 24, 27, 0.12);
  transform: rotate(-1.2deg);
}

.about-content .section-title {
  text-align: left;
  margin-bottom: var(--spacing-lg);
  max-width: 420px;
}

.about-text {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--color-gray-700);
  max-width: 58ch;
}

.about-content {
  position: relative;
  z-index: 1;
}

:global(body.calendar-popup-open) .hero {
  z-index: 100000;
}

/* Разделитель между «О нас» и «Почему выбирают нас» внутри одной секции */
.about-advantages {
  padding-top: var(--spacing-2xl);
}

.about-advantages-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-gray-900);
  text-align: center;
  margin: 0 0 var(--spacing-lg);
}

/* ======================================
   ADVANTAGES SECTION — 3×2, иконка слева, текст справа
   ====================================== */
.advantages-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
}

.advantage-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.advantage-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.advantage-icon-wrap {
  flex-shrink: 0;
  width: 68px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.advantage-icon-wrap img {
  width: 68px;
  height: 68px;
  object-fit: cover;
}

.advantage-text {
  flex: 1;
}

.advantage-title {
  font-size: var(--text-base);
  font-weight: 600;
  margin-bottom: 2px;
  margin-top: 0;
  line-height: 1.3;
}

.advantage-desc {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
  margin: 0;
  line-height: 1.4;
}

/* ======================================
   TERRITORY GALLERY
   ====================================== */
.territory-section {
  background: var(--color-white);
}

.territory-header {
  max-width: 680px;
  margin: 0 auto var(--spacing-2xl);
  text-align: center;
}

.territory-lead {
  margin: var(--spacing-sm) 0 0;
  color: var(--color-gray-600);
  font-size: var(--text-lg);
  line-height: var(--leading-relaxed);
}

.territory-groups {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}

.territory-group-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  min-width: 0;
}

.territory-group-main {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: var(--color-gray-200);
  aspect-ratio: 4 / 5;
}

.territory-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 700ms cubic-bezier(0.22, 1, 0.36, 1);
}

.territory-group-main:hover .territory-image {
  transform: scale(1.04);
}

.territory-caption {
  position: absolute;
  inset: auto 0 0;
  padding: var(--spacing-lg);
  color: var(--color-white);
  background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.72));
}

.territory-caption h3 {
  margin: 0 0 4px;
  color: var(--color-white);
  font-size: var(--text-lg);
}

.territory-caption p {
  margin: 0;
  max-width: 40ch;
  color: rgba(255, 255, 255, 0.88);
  font-size: var(--text-sm);
  line-height: 1.45;
}

.territory-thumbs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-sm);
}

.territory-thumb {
  position: relative;
  padding: 0;
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  overflow: hidden;
}

.territory-thumb img {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  display: block;
  background: var(--color-gray-200);
  transition: transform var(--transition-base), filter var(--transition-base);
}

.territory-thumb:hover img,
.territory-thumb--active img {
  transform: scale(1.04);
  filter: saturate(1.08);
}

.territory-thumb--active {
  border-color: #c6c4fd;
}

@media (max-width: 900px) {
  .territory-groups {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 560px) {
  .territory-groups {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  .territory-lead {
    font-size: var(--text-base);
  }
  .territory-group-main {
    aspect-ratio: 4 / 3;
  }
  .territory-group-card {
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid rgba(198, 196, 253, 0.65);
  }
  .territory-group-card:last-child {
    padding-bottom: 0;
    border-bottom: 0;
  }
}

/* ======================================
   FAQ SECTION
   ====================================== */
.faq-layout {
  display: grid;
  grid-template-columns: minmax(260px, 420px) 1fr;
  gap: var(--spacing-3xl);
  align-items: center;
}

.faq-illustration {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Мягкий фон-круг под иллюстрацией, чтобы PNG «вписалась» в секцию */
.faq-illustration::before {
  content: '';
  position: absolute;
  inset: 8% 8%;
  background: radial-gradient(
    circle at 50% 45%,
    rgba(198, 196, 253, 0.22) 0%,
    rgba(76, 76, 247, 0.04) 55%,
    transparent 75%
  );
  border-radius: 50%;
  z-index: 0;
}

.faq-illustration-img {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 380px;
  height: auto;
  object-fit: contain;
  /* Лёгкая тень, чтобы PNG смотрелась объёмно без заметной рамки */
  animation: faq-illustration-float 6s ease-in-out infinite;
}

@keyframes faq-illustration-float {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-8px); }
}

.faq-content {
  min-width: 0;
}

.faq-content .eyebrow {
}

.faq-title {
  margin-bottom: var(--spacing-sm);
}

.faq-lead {
  margin: 0 0 var(--spacing-lg);
  color: var(--color-gray-600);

  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  max-width: 52ch;
}

.faq-list {
  margin: 0;
}

/* Планшет: картинка чуть меньше */
@media (max-width: 960px) {
  .faq-layout {
    grid-template-columns: minmax(220px, 320px) 1fr;
    gap: var(--spacing-2xl);
  }
}

/* Мобильный: иллюстрация сверху, компактнее */
@media (max-width: 640px) {
  .faq-layout {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  .faq-illustration-img {
    max-width: 220px;
  }
  .faq-title,
  .faq-content .eyebrow,
  .faq-lead {
    text-align: center;
  }
  .faq-lead {
    margin-left: auto;
    margin-right: auto;
  }
}

.faq-item {
  border-bottom: 1px solid var(--color-gray-200);
}

.faq-question {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) 0;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--color-gray-900);
  transition: color var(--transition-fast);
}

.faq-question:hover {
  color: #5651d8;
}

.faq-icon {
  flex-shrink: 0;
  transition: transform var(--transition-base);
}

.faq-icon.active {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 0 var(--spacing-lg);
  color: var(--color-gray-600);
  line-height: var(--leading-relaxed);
}

.faq-expand-enter-active,
.faq-expand-leave-active {
  transition: all var(--transition-slow);
  overflow: hidden;
}

.faq-expand-enter-from,
.faq-expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.faq-expand-enter-to,
.faq-expand-leave-from {
  opacity: 1;
  max-height: 200px;
}

/* ======================================
   DIRECTIONS SECTION
   ====================================== */
.directions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-2xl);
}

.direction-card {
  position: relative;
  isolation: isolate;
  background: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  padding: 18px 20px;
  min-height: 132px;
  overflow: hidden;
  box-shadow: none;
  text-align: left;
  transition: all var(--transition-base);
}

.direction-card:hover {
  transform: translateY(-1px);
  border-color: rgba(198, 196, 253, 0.75);
  box-shadow: 0 8px 20px rgba(24, 24, 27, 0.05);
}

.direction-icon {
  position: absolute;
  top: 50%;
  right: 14px;
  z-index: -1;
  width: min(120px, 38%);
  height: calc(100% - 26px);
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.13;
  transform: translateY(-50%);
  pointer-events: none;
}

.direction-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: invert(29%) sepia(33%) saturate(2331%) hue-rotate(222deg) brightness(91%) contrast(91%);
}

.direction-title {
  position: relative;
  z-index: 1;
  font-size: var(--text-base);
  font-weight: 600;
  margin: 0 0 6px;
  line-height: 1.25;
}

.direction-text {
  position: relative;
  z-index: 1;
  font-size: var(--text-sm);
  color: var(--color-gray-600);
  line-height: 1.55;
  margin: 0;
}

.map-container {
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.map-iframe {
  display: block;
  width: 100%;
}

/* ======================================
   LANDMARKS SECTION — modern bento grid
   ====================================== */
.landmarks-section {
  background:
    radial-gradient(1200px 400px at 85% -10%, rgba(198, 196, 253, 0.22), transparent 60%),
    radial-gradient(900px 400px at -10% 110%, rgba(63, 125, 91, 0.08), transparent 60%),
    var(--color-white);
}

.landmarks-header {
  max-width: 640px;
  margin: 0 auto var(--spacing-2xl);
  text-align: center;
}

.eyebrow {
  display: inline-block;
  padding: 6px 14px;
  margin-bottom: var(--spacing-md);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #5651d8;
  background: rgba(198, 196, 253, 0.24);
  border-radius: var(--radius-full);
}

.landmarks-lead {
  margin: var(--spacing-sm) 0 0;
  color: var(--color-gray-600);
  font-size: var(--text-lg);
  line-height: var(--leading-relaxed);
}

.landmarks-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: var(--spacing-md);
  max-height: 900px;
  height: clamp(560px, 70vw, 900px);
}

/* Мозаика: большой / вертикальный / маленькие / горизонтальные */
.landmark-card--1 { grid-column: 1 / span 2; grid-row: 1 / span 2; } /* big */
.landmark-card--2 { grid-column: 3 / span 1; grid-row: 1 / span 2; } /* vertical */
.landmark-card--3 { grid-column: 4 / span 1; grid-row: 1 / span 1; } /* small */
.landmark-card--4 { grid-column: 4 / span 1; grid-row: 2 / span 1; } /* small */
.landmark-card--5 { grid-column: 1 / span 2; grid-row: 3 / span 1; } /* horizontal */
.landmark-card--6 { grid-column: 3 / span 2; grid-row: 3 / span 1; } /* horizontal */

.landmark-card {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: var(--color-gray-200, #eee);
  cursor: pointer;
  outline: none;
  isolation: isolate;
  transition: transform var(--transition-base);
}

.landmark-card:hover { transform: translateY(-2px); }
.landmark-card:focus-visible { box-shadow: 0 0 0 3px rgba(198, 196, 253, 0.55); }

.landmark-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 700ms cubic-bezier(0.22, 1, 0.36, 1),
              filter var(--transition-base);
  will-change: transform;
}

.landmark-card:hover .landmark-img,
.landmark-card:focus-visible .landmark-img {
  transform: scale(1.05);
  filter: brightness(0.6);
}

/* Тонкая подпись внизу — видна всегда, скрывается при наведении */
.landmark-label {
  position: absolute;
  left: var(--spacing-md);
  bottom: var(--spacing-md);
  padding: 6px 12px;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-white);
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border-radius: var(--radius-full);
  transition: opacity var(--transition-base), transform var(--transition-base);
  z-index: 2;
}

.landmark-card:hover .landmark-label,
.landmark-card:focus-visible .landmark-label {
  opacity: 0;
  transform: translateY(8px);
}

/* Всплывающая информация при наведении */
.landmark-hover {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 8px;
  padding: var(--spacing-lg);
  color: var(--color-white);
  background: linear-gradient(180deg, rgba(0,0,0,0) 30%, rgba(0,0,0,0.72) 100%);
  opacity: 0;
  transform: translateY(12px);
  transition: opacity var(--transition-base), transform var(--transition-base);
  pointer-events: none;
}

.landmark-card:hover .landmark-hover,
.landmark-card:focus-visible .landmark-hover {
  opacity: 1;
  transform: translateY(0);
}

.landmark-distance {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  align-self: flex-start;
  padding: 4px 10px;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-white);
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-full);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.landmark-title {
  margin: 0;
  font-size: var(--text-xl);
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--color-white);
}

.landmark-desc {
  margin: 0;
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: rgba(255, 255, 255, 0.88);
}

/* Tablet: 3 кол × 4 ряда, с сохранением разных размеров */
@media (max-width: 1024px) {
  .landmarks-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(4, 1fr);
    height: clamp(640px, 95vw, 900px);
  }
  .landmark-card--1 { grid-column: 1 / span 2; grid-row: 1 / span 2; } /* big */
  .landmark-card--2 { grid-column: 3 / span 1; grid-row: 1 / span 2; } /* vertical */
  .landmark-card--3 { grid-column: 1 / span 1; grid-row: 3 / span 1; } /* small */
  .landmark-card--4 { grid-column: 2 / span 1; grid-row: 3 / span 1; } /* small */
  .landmark-card--5 { grid-column: 3 / span 1; grid-row: 3 / span 2; } /* vertical */
  .landmark-card--6 { grid-column: 1 / span 2; grid-row: 4 / span 1; } /* horizontal */
}

/* Mobile: на сенсорных устройствах hover обычно недоступен,
   поэтому overlay показываем всегда (статично).
   Сохраняем вариативность: большой → два маленьких → горизонтальный → два маленьких */
@media (max-width: 600px) {

  
.about-advantages {
  padding-top: 0;
}
  .landmarks-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: 240px 320px 240px 320px;
    gap: var(--spacing-sm);
    height: auto;
    max-height: none;
  }
  .landmark-card--1 { grid-column: 1 / -1; grid-row: 1 / span 1; } /* большой */
  .landmark-card--2 { grid-column: 1 / span 1; grid-row: 2 / span 1; } /* маленький */
  .landmark-card--3 { grid-column: 2 / span 1; grid-row: 2 / span 1; } /* маленький */
  .landmark-card--4 { grid-column: 1 / -1; grid-row: 3 / span 1; } /* горизонтальный */
  .landmark-card--5 { grid-column: 1 / span 1; grid-row: 4 / span 1; } /* маленький */
  .landmark-card--6 { grid-column: 2 / span 1; grid-row: 4 / span 1; } /* маленький */

  .landmark-label { display: none; }
  .landmark-hover {
    opacity: 1;
    transform: none;
    padding: var(--spacing-sm);
    gap: 4px;
  }
  .landmark-card .landmark-img {
    filter: brightness(0.7);
  }

  /* Компактная типографика для маленьких карточек,
     чтобы весь текст влезал без обрезки */
  .landmark-distance {
    padding: 3px 8px;
    font-size: 10px;
    gap: 4px;
  }
  .landmark-distance svg { width: 10px; height: 10px; }

  .landmark-title {
    font-size: var(--text-base);
    line-height: 1.2;
  }

  .landmark-desc {
    font-size: 12px;
    line-height: 1.35;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  /* Большая карточка — крупнее текст, больше место под описание */
  .landmark-card--1 .landmark-hover { padding: var(--spacing-md); gap: 6px; }
  .landmark-card--1 .landmark-title { font-size: var(--text-xl); }
  .landmark-card--1 .landmark-desc {
    font-size: var(--text-sm);
    -webkit-line-clamp: 3;
    line-clamp: 3;
  }

  /* Горизонтальная карточка (ряд 3) — чуть просторнее */
  .landmark-card--4 .landmark-hover { padding: 10px var(--spacing-md); }
  .landmark-card--4 .landmark-title { font-size: var(--text-lg); }
  .landmark-card--4 .landmark-desc { -webkit-line-clamp: 1; line-clamp: 1; }
  .landmarks-lead {
    font-size: var(--text-base);
  }
}

/* ======================================
   TESTIMONIALS SECTION
   ====================================== */
.reviews-section {
  overflow: hidden;
}

.reviews-header {
  max-width: 680px;
  margin: 0 auto var(--spacing-xl);
  text-align: center;
}

.testimonials-slider {
  position: relative;
  overflow: hidden;
  margin-top: var(--spacing-xl);
}

.testimonials-track {
  display: flex;
  gap: var(--spacing-lg);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  padding: var(--spacing-md) var(--spacing-md) var(--spacing-lg);
}

.testimonials-track::-webkit-scrollbar {
  display: none;
}

.testimonial-card {
  position: relative;
  flex: 0 0 clamp(280px, 28vw, 360px);
  scroll-snap-align: start;
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  min-height: 280px;
  border: 1px solid rgba(198, 196, 253, 0.45);
  overflow: hidden;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base);
}

.testimonial-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 4px;
  background: linear-gradient(90deg, #c6c4fd, #7bd7c3);
}

.testimonial-card:hover {
  transform: translateY(-3px);
  border-color: rgba(86, 81, 216, 0.35);
  box-shadow: 0 22px 54px rgba(24, 24, 27, 0.12);
}

.testimonial-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  position: relative;
  z-index: 1;
}

.testimonial-avatar {
  width: 54px;
  height: 54px;
  border-radius: var(--radius-full);
  object-fit: cover;
  background: var(--color-gray-200);
  border: 3px solid rgba(198, 196, 253, 0.45);
  box-shadow: 0 8px 20px rgba(86, 81, 216, 0.12);
  flex: 0 0 54px;
}

.testimonial-avatar--fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #3730a3;
  background: linear-gradient(135deg, rgba(198, 196, 253, 0.75), rgba(255, 255, 255, 0.95));
  font-size: var(--text-xl);
  font-weight: 800;
}

.testimonial-author {
  min-width: 0;
}

.testimonial-author strong {
  display: block;
  font-size: var(--text-base);
  color: var(--color-gray-900);
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.testimonial-author span {
  display: block;
  margin-top: 3px;
  color: var(--color-gray-500);
  font-size: var(--text-xs);
  font-weight: 600;
}

.testimonial-quote-mark {
  position: absolute;
  right: var(--spacing-lg);
  top: 54px;
  color: rgba(198, 196, 253, 0.5);
  font-family: Georgia, serif;
  font-size: 5rem;
  line-height: 1;
  pointer-events: none;
}

.testimonial-text {
  position: relative;
  z-index: 1;
  margin: 0;
  max-height: 132px;
  overflow: hidden;
  color: var(--color-gray-700);
  font-size: var(--text-sm);
  line-height: 1.65;
  overflow-wrap: anywhere;
}

.testimonial-text::before {
  content: "«";
}

.testimonial-text::after {
  content: "»";
}

.testimonial-text--expanded {
  max-height: 260px;
  overflow-y: auto;
  padding-right: 4px;
}

.testimonial-text:not(.testimonial-text--expanded) {
  display: -webkit-box;
  -webkit-line-clamp: 5;
  line-clamp: 5;
  -webkit-box-orient: vertical;
}

.testimonial-more {
  position: relative;
  z-index: 1;
  margin-top: var(--spacing-md);
  padding: 0;
  border: 0;
  background: transparent;
  color: #5651d8;
  font-size: var(--text-sm);
  font-weight: 800;
  cursor: pointer;
}

.testimonial-more:hover {
  color: #3730a3;
}
.faq-header{
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;

}
.faq-header {
    text-align: center;

}


.slider-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  background: var(--color-white);
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all var(--transition-fast);
  border: none;
  color: var(--color-gray-700);
}

.slider-btn:hover {
  background: #5651d8;
  color: white;
  box-shadow: var(--shadow-lg);
}

.slider-btn-prev { left: var(--spacing-md); }
.slider-btn-next { right: var(--spacing-md); }

/* ======================================
   RESPONSIVE
   ====================================== */
@media (max-width: 900px) {
  .about-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }

  .about-image img {
    height: 220px;
  }

  .directions-grid {
    grid-template-columns: 1fr;
  }

  .advantages-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero {
    min-height: 60vh;
  }
}

@media (max-width: 600px) {
  .hero-title {
    font-size: clamp(2rem, 6vw, 3rem);
  }

  .section-title {
    font-size: var(--text-2xl);
  }

  .advantages-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .advantage-card {
    padding: var(--spacing-md);
    gap: var(--spacing-sm);
  }

  .advantage-icon-wrap {
    width: 56px;
    height: 56px;
  }

  .advantage-icon-wrap img {
    width: 56px;
    height: 56px;
  }

  .testimonial-card {
    flex: 0 0 min(86vw, 340px);
    min-height: 260px;
    padding: var(--spacing-lg);
  }

  .testimonial-avatar {
    width: 48px;
    height: 48px;
    flex-basis: 48px;
  }

  .testimonial-quote-mark {
    top: 50px;
    right: var(--spacing-md);
    font-size: 4rem;
  }

  .testimonial-text {
    max-height: 118px;
  }

  .landmark-card {
    flex: 0 0 260px;
  }

  .slider-btn {
    width: 36px;
    height: 36px;
  }
}
</style>
