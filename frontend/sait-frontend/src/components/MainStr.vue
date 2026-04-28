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

    <!-- 5. FAQ Block -->
    <section id="faq" class="section">
      <div class="container">
        <div class="faq-layout">
          <aside class="faq-illustration" aria-hidden="true">
            <img :src="faqImage" alt="" class="faq-illustration-img" />
          </aside>

          <div class="faq-content">
            <span class="eyebrow">Вопрос — ответ</span>
            <h2 class="section-title faq-title">Часто задаваемые вопросы</h2>
            <p class="faq-lead">Собрали самое важное о заселении, питании и досуге. Не нашли ответ — напишите нам, ответим лично.</p>

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

        <div class="directions-grid">
          <!-- Трансфер -->
          <div class="direction-card">
            <div class="direction-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M8 17h8M8 17a2 2 0 01-2-2V9a2 2 0 012-2h1.5l1.5-3h4L16.5 7H18a2 2 0 012 2v6a2 2 0 01-2 2M8 17a2 2 0 100 4 2 2 0 000-4zM16 17a2 2 0 100 4 2 2 0 000-4z"/>
              </svg>
            </div>
            <h3 class="direction-title">Трансфер</h3>
            <p class="direction-text">
              Мы организуем трансфер из аэропорта Симферополя или ж/д вокзала.
              Свяжитесь с нами заранее для заказа.
            </p>
            <a href="tel:+79788028912" class="btn btn--primary btn--rounded btn--sm">
              Заказать трансфер
            </a>
          </div>

          <!-- Общественный транспорт -->
          <div class="direction-card">
            <div class="direction-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="5" y="2" width="14" height="16" rx="2"/>
                <path d="M5 10h14M9 18v2M15 18v2M9 6h2M13 6h2"/>
              </svg>
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
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                <circle cx="12" cy="9" r="2.5"/>
              </svg>
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
          <span class="eyebrow">Рядом с домом</span>
          <h2 class="section-title">Знаковые места поблизости</h2>
          <p class="landmarks-lead">Море, горы, водопады и уютные городки — всё в шаговой или короткой автомобильной доступности.</p>
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
    <section id="reviews" class="section section--gray">
      <div class="container">
        <h2 class="section-title text-center">Отзывы наших гостей</h2>
        <div class="testimonials-slider" v-if="siteInfo?.testimonials?.length">
          <div class="testimonials-track" ref="testimonialsTrack">
            <div class="testimonial-card" v-for="testimonial in siteInfo.testimonials" :key="testimonial.id">
              <div class="testimonial-header">
                <img
                  :src="getTestimonialAvatarUrl(testimonial.author_icon_url)"
                  :alt="testimonial.author_name"
                  class="testimonial-avatar"
                />
                <div class="testimonial-author">
                  <strong>{{ testimonial.author_name }}</strong>
                </div>
              </div>
              <p class="testimonial-text">«{{ testimonial.comment }}»</p>
            </div>
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

// Иконки преимуществ
import iconShop from '@/assets/icons/shop.svg';
import iconPlace from '@/assets/icons/place.svg';
import iconGames from '@/assets/icons/games.svg';
import iconBeach from '@/assets/icons/beach.svg';
import iconJur from '@/assets/icons/jur.svg';
import iconFootball from '@/assets/icons/football.svg';
import landmarkSea from '@/assets/landmarks/sea.jpg';
import landmarkJurJur from '@/assets/landmarks/jurjur.jpeg';
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
      openFaqIndex: null,
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
      return this.siteInfo?.courtyard_photos || [];
    },
    aboutImageSrc() {
      return this.siteInfo?.courtyard_photos?.[0]?.url
        ? `${API_BASE_URL}${this.siteInfo.courtyard_photos[0].url}`
        : defaultImage;
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
    landmarks() {
      return [
        { title: 'Море', distance: '10 мин пешком', desc: 'Чистый галечный пляж с живописными видами на горы', image: landmarkSea },
        { title: 'Водопад Джур-Джур', distance: '30 мин на машине', desc: 'Самый полноводный водопад Крыма среди вековых буков', image: landmarkJurJur },
        { title: 'Алушта', distance: '20 мин на машине', desc: 'Город с набережными, ресторанами и аквапарком', image: landmarkAlushta },
        { title: 'Гора Демерджи', distance: '25 мин на машине', desc: 'Долина Привидений и знаменитые каменные изваяния', image: landmarkDemerdzhi },
        { title: 'Парк Айвазовское', distance: '15 мин на машине', desc: 'Ландшафтный парк с реликтовыми растениями', image: landmarkAivaz },
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
    await this.fetchSiteInfo();
    await this.fetchAllRooms();
  },
  methods: {
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
  min-height: 70vh;
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
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-2xl);
}

.about-image img {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.about-content .section-title {
  text-align: left;
  margin-bottom: var(--spacing-lg);
}

.about-text {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--color-gray-700);
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
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-soft);
  border-radius: var(--radius-lg);
}

.advantage-icon-wrap img {
  width: 28px;
  height: 28px;
  filter: invert(30%) sepia(80%) saturate(2000%) hue-rotate(330deg);
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
    var(--color-primary-soft, rgba(76, 76, 247, 0.12)) 0%,
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
  margin-bottom: var(--spacing-sm);
}

.faq-title {
  text-align: left;
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
  color: var(--color-primary);
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
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
}

.direction-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  text-align: center;
  transition: all var(--transition-base);
}

.direction-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.direction-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  background: var(--color-primary-soft);
  border-radius: var(--radius-full);
}

.direction-title {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.direction-text {
  font-size: var(--text-sm);
  color: var(--color-gray-600);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--spacing-md);
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
    radial-gradient(1200px 400px at 85% -10%, var(--color-primary-soft), transparent 60%),
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
  color: var(--color-primary-dark);
  background: var(--color-primary-soft);
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
.landmark-card:focus-visible { box-shadow: 0 0 0 3px var(--color-primary-soft); }

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
  padding: var(--spacing-md) 0;
}

.testimonials-track::-webkit-scrollbar {
  display: none;
}

.testimonial-card {
  flex: 0 0 320px;
  scroll-snap-align: start;
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.testimonial-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.testimonial-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  object-fit: cover;
  background: var(--color-gray-200);
}

.testimonial-author strong {
  font-size: var(--text-base);
  color: var(--color-gray-900);
}

.testimonial-text {
  font-size: var(--text-sm);
  color: var(--color-gray-600);
  line-height: var(--leading-relaxed);
  font-style: italic;
  margin: 0;
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
  background: var(--color-primary);
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
    width: 44px;
    height: 44px;
  }

  .advantage-icon-wrap img {
    width: 24px;
    height: 24px;
  }

  .testimonial-card {
    flex: 0 0 280px;
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
