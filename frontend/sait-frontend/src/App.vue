<template>
  <div id="app">
    <!-- Навигационная панель -->
    <nav v-if="showNavigation" class="main-nav" :class="{ 'main-nav--open': mobileMenuOpen }">
      <div class="main-nav-cont">
        <div class="nav-brand">
          <router-link to="/" class="nav-logo" @click="closeMobileMenu">
            <img src="@/assets/logo.png" alt="Виноградная Лоза" class="nav-logo-img">
          </router-link>
        </div>

        <!-- Центральные ссылки на разделы главной страницы -->
        <div class="nav-sections" v-if="isHomePage">
          <a
            v-for="item in sectionLinks"
            :key="item.id"
            :href="`#${item.id}`"
            class="nav-section-link"
            @click.prevent="scrollToSection(item.id)"
          >{{ item.label }}</a>
        </div>

        <div class="nav-links">
          <template v-if="!isAuthenticated">
            <router-link to="/login" class="nav-link" @click="closeMobileMenu">Вход</router-link>
          </template>
          <template v-else>
            <router-link
              v-if="isAdmin"
              to="/admin/rooms"
              class="nav-link admin-link"
              @click="closeMobileMenu"
            >
              Админ-панель
            </router-link>
            <button @click="handleLogout" class="nav-button">Выход</button>
          </template>
        </div>

        <!-- Кнопка бургер -->
        <button
          class="nav-burger"
          :class="{ 'nav-burger--open': mobileMenuOpen }"
          @click="mobileMenuOpen = !mobileMenuOpen"
          :aria-label="mobileMenuOpen ? 'Закрыть меню' : 'Открыть меню'"
          :aria-expanded="mobileMenuOpen"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <!-- Мобильное меню -->
      <transition name="mobile-menu">
        <div v-if="mobileMenuOpen" class="mobile-menu">
          <template v-if="isHomePage">
            <a
              v-for="item in sectionLinks"
              :key="item.id"
              :href="`#${item.id}`"
              class="mobile-menu-link"
              @click.prevent="scrollToSection(item.id)"
            >{{ item.label }}</a>
          </template>
          <router-link v-if="!isAuthenticated" to="/login" class="mobile-menu-link" @click="closeMobileMenu">Вход</router-link>
          <router-link v-if="isAuthenticated && isAdmin" to="/admin/rooms" class="mobile-menu-link mobile-menu-link--primary" @click="closeMobileMenu">Админ-панель</router-link>
          <button v-if="isAuthenticated" @click="handleLogout(); closeMobileMenu()" class="mobile-menu-link mobile-menu-link--btn">Выход</button>
        </div>
      </transition>
    </nav>

    <!-- Основное содержимое -->
    <main class="main-content">
      <router-view 
      />
    </main>

    <!-- Уведомления -->
    <transition name="fade">
      <div v-if="notification.message" :class="['notification', notification.type]">
        {{ notification.message }}
      </div>
    </transition>

    <footer class="site-footer">
      <div class="footer-container">
        <div class="footer-grid">
          <!-- Контакты -->
          <div class="footer-col">
            <h4 class="footer-heading">Контакты</h4>
            <a href="tel:+79788028912" class="footer-contact">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
              </svg>
              +7 (978) 802-89-12
            </a>
            <a href="mailto:loza-vinogradnaya@mail.ru" class="footer-contact">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
              </svg>
              loza-vinogradnaya@mail.ru
            </a>
            <a href="https://yandex.ru/maps/org/gostevoy_domik_vinogradnaya_loza/92950545738/"
               target="_blank" rel="noopener noreferrer" class="footer-contact">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/>
              </svg>
              Алушта, с. Рыбачье, ул. Школьная 1/2
            </a>
          </div>

          <!-- Навигация -->
          <div class="footer-col footer-col--nav">
            <h4 class="footer-heading">Навигация</h4>
            <a href="#rooms" class="footer-link">Номера</a>
            <a href="#about" class="footer-link">О нас</a>
            <a href="#faq" class="footer-link">Вопросы</a>
            <a href="#reviews" class="footer-link">Отзывы</a>
          </div>

          <!-- Соц-сети -->
          <div class="footer-col footer-col--social">
            <h4 class="footer-heading">Мы в соц-сетях</h4>
            <div class="social-icons">
              <a href="https://vk.com/rubachie" target="_blank" rel="noopener noreferrer" class="social-icon" title="ВКонтакте">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.785 16.241s.288-.032.436-.194c.136-.148.132-.427.132-.427s-.02-1.304.587-1.496c.598-.189 1.365 1.26 2.179 1.817.615.42 1.083.328 1.083.328l2.175-.03s1.14-.07.599-.964c-.044-.073-.314-.661-1.617-1.869-1.364-1.264-1.182-1.06.462-3.246.998-1.328 1.398-2.139 1.273-2.486-.12-.331-.854-.244-.854-.244l-2.444.015s-.182-.025-.315.056c-.131.079-.216.263-.216.263s-.387 1.028-.904 1.903c-1.089 1.85-1.525 1.948-1.703 1.834-.414-.265-.31-1.065-.31-1.634 0-1.776.27-2.515-.524-2.708-.264-.064-.458-.106-1.134-.113-.866-.009-1.599.003-2.014.207-.277.136-.491.441-.361.458.161.021.527.099.72.363.25.339.241 1.103.241 1.103s.143 2.09-.333 2.349c-.327.178-.775-.185-1.736-1.845-.492-.851-.863-1.792-.863-1.792s-.072-.176-.2-.27c-.155-.114-.372-.15-.372-.15l-2.322.015s-.349.01-.477.161c-.114.135-.009.413-.009.413s1.819 4.258 3.876 6.404c1.887 1.967 4.032 1.838 4.032 1.838h.971z"/>
                </svg>
              </a>
              <a href="#" class="social-icon" title="Instagram">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </a>
              <a href="#" class="social-icon" title="Одноклассники">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 4.5a3 3 0 1 1 0 6 3 3 0 0 1 0-6zm4.394 9.438c-.16.244-.44.382-.728.382-.16 0-.32-.046-.46-.14-.98-.654-2.06-.98-3.206-.98-1.146 0-2.226.326-3.206.98-.29.194-.674.212-.986.046-.312-.166-.476-.486-.476-.828 0-.342.164-.662.476-.828 1.26-.84 2.68-1.26 4.192-1.26s2.932.42 4.192 1.26c.48.32.584.964.262 1.444z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>

        <div class="footer-bottom">
          <p class="footer-copyright">
            © {{ new Date().getFullYear() }} Гостевой дом "Виноградная Лоза". Все права защищены.
          </p>
        </div>
      </div>
    </footer>

  </div>
</template>

<script>
import api from '@/api';

export default {
  data() {
    return {
      rooms: [],
      isAuthenticated: false,
      isAdmin: false,
      mobileMenuOpen: false,
      isMobileScreen: window.innerWidth <= 768,
      sectionLinks: [
        { id: 'hero',       label: 'Поиск' },
        { id: 'about',      label: 'О нас' },
        { id: 'rooms',      label: 'Номера' },
        { id: 'directions', label: 'Как добраться' },
        { id: 'faq',        label: 'Вопросы' },
        { id: 'reviews',    label: 'Отзывы' }
      ],
      notification: {
        message: '',
        type: 'info' // info | success | error
      }
    };
  },
  computed: {
    showNavigation() {
      // Скрываем навигацию на страницах входа/регистрации
      // На RoomDetail скрываем только на мобильных
      if (this.$route.name === 'RoomDetail' && this.isMobileScreen) return false;
      return !['Login', 'SignUp'].includes(this.$route.name);
    },
    isHomePage() {
      return this.$route.name === 'Home';
    }
  },
  async created() {
    await this.checkAuth();
  },
  mounted() {
    this._onResize = () => { this.isMobileScreen = window.innerWidth <= 768; };
    window.addEventListener('resize', this._onResize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this._onResize);
  },
  watch: {
    $route() {
      this.checkAuth();
      this.mobileMenuOpen = false;
    }
  },
  methods: {
    async checkAuth() {
      const token = localStorage.getItem('access_token');
      this.isAuthenticated = !!token;

      if (token) {
        try {
          const response = await api.get('/users/me/')
          this.isAdmin = response.data.is_superuser;
        } catch (error) {
          this.showNotification('Сессия истекла, войдите снова', 'error');
          this.handleLogout();
        }
      }
    },

    handleLogout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_expiration');
      this.isAuthenticated = false;
      this.isAdmin = false;
      this.$router.push('/login');
      this.showNotification('Вы успешно вышли из системы', 'success');
    },

    showNotification(message, type = 'info') {
      this.notification = { message, type };
      setTimeout(() => {
        this.notification.message = '';
      }, 5000);
    },

    closeMobileMenu() {
      this.mobileMenuOpen = false;
    },

    async scrollToSection(id) {
      this.closeMobileMenu();
      // Если мы не на главной странице — сначала переходим туда
      if (!this.isHomePage) {
        await this.$router.push({ name: 'Home', hash: `#${id}` });
      }
      this.$nextTick(() => {
        const el = document.getElementById(id);
        if (!el) return;
        const navHeight = document.querySelector('.main-nav')?.offsetHeight || 0;
        const top = el.getBoundingClientRect().top + window.pageYOffset - navHeight - 8;
        window.scrollTo({ top, behavior: 'smooth' });
      });
    }
  }
};
</script>

<style>
/* ==========================================================================
   DESIGN TOKENS (глобальные CSS-переменные)
   Изменяйте значения здесь — они применяются ко всему сайту.
   ========================================================================== */
:root {
  /* --- Основные цвета (бордово-винный) --- */
  --color-primary:        #B63A47;
  --color-primary-dark:   #922A36;
  --color-primary-light:  #D25C69;
  --color-primary-soft:   rgba(182, 58, 71, 0.08);

  /* --- Вторичные (зелень винограда) --- */
  --color-secondary:       #3F7D5B;
  --color-secondary-dark:  #2F6147;
  --color-secondary-light: #5E9C7A;

  /* --- Нейтральные / серые --- */
  --color-gray-900: #1A1A1A;
  --color-gray-800: #2D2D2D;
  --color-gray-700: #4A4A4A;
  --color-gray-600: #5E5E5E;
  --color-gray-500: #767676;
  --color-gray-400: #9A9A9A;
  --color-gray-300: #C4C4C4;
  --color-gray-200: #E8E8E8;
  --color-gray-100: #F7F7F7;
  --color-gray-50:  #FAFAFA;
  --color-white:    #FFFFFF;
  --color-black:    #000000;

  /* --- Статусные --- */
  --color-success:      #008A05;
  --color-success-soft: rgba(0, 138, 5, 0.08);
  --color-warning:      #FFA726;
  --color-warning-soft: rgba(255, 167, 38, 0.08);
  --color-error:        #E74C3C;
  --color-error-soft:   rgba(231, 76, 60, 0.08);
  --color-info:         #3498DB;
  --color-info-soft:    rgba(52, 152, 219, 0.08);

  /* --- Тёплые оттенки --- */
  --color-warm-bg:     #FFF8F0;
  --color-warm-accent: #F69E66;
  --color-warm-light:  #FDE8D8;

  /* --- Шрифты --- */
  --font-family-base:    'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-heading: 'Inter', 'Segoe UI', Roboto, sans-serif;

  /* --- Размеры текста --- */
  --text-xs:   0.75rem;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-lg:   1.125rem;
  --text-xl:   1.25rem;
  --text-2xl:  clamp(1.375rem, 1.25rem + 0.4vw, 1.5rem);
  --text-3xl:  clamp(1.625rem, 1.4rem  + 0.6vw, 1.875rem);
  --text-4xl:  clamp(1.875rem, 1.5rem  + 0.9vw, 2.25rem);
  --text-5xl:  clamp(2.25rem,  1.75rem + 1.2vw, 2.875rem);

  /* --- Межстрочный интервал --- */
  --leading-none:    1;
  --leading-tight:   1.25;
  --leading-snug:    1.375;
  --leading-normal:  1.5;
  --leading-relaxed: 1.625;

  /* --- Отступы --- */
  --spacing-xs:  0.25rem;
  --spacing-sm:  0.5rem;
  --spacing-md:  1rem;
  --spacing-lg:  1.2rem;
  --spacing-xl:  2rem;
  --spacing-2xl: clamp(2.5rem, 2rem + 1vw, 3rem);
  --spacing-3xl: clamp(3rem,   2rem + 2vw, 4rem);

  /* --- Скругления --- */
  --radius-sm:   0.375rem;
  --radius-md:   0.5rem;
  --radius-lg:   0.75rem;
  --radius-xl:   1rem;
  --radius-2xl:  1.5rem;
  --radius-full: 9999px;

  /* --- Тени --- */
  --shadow-sm:  0 1px 2px  rgba(24, 24, 27, 0.04), 0 1px 1px  rgba(24, 24, 27, 0.03);
  --shadow-md:  0 4px 10px -2px rgba(24, 24, 27, 0.08), 0 2px 4px  -1px rgba(24, 24, 27, 0.04);
  --shadow-lg:  0 10px 24px -4px rgba(24, 24, 27, 0.10), 0 4px 10px -2px rgba(24, 24, 27, 0.05);
  --shadow-xl:  0 20px 40px -8px rgba(24, 24, 27, 0.12), 0 8px 16px -4px rgba(24, 24, 27, 0.05);
  --shadow-2xl: 0 32px 60px -12px rgba(24, 24, 27, 0.22);

  /* --- Переходы --- */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

  /* --- Z-index --- */
  --z-dropdown:        1000;
  --z-sticky:          1020;
  --z-fixed:           1030;
  --z-modal-backdrop:  1040;
  --z-modal:           1050;
  --z-popover:         1060;
  --z-tooltip:         1070;
  --z-calendar:        10000;
  --z-calendar-fullscreen: 10001;

  /* --- Навигация (шапка) --- */
  --nav-height:            64px;
  --nav-height-mobile:     60px;
  --nav-bg:                rgba(255, 255, 255, 0.95);
  --nav-shadow:            0 1px 3px rgba(0, 0, 0, 0.08);
  --nav-text:              var(--color-gray-700);
  --nav-text-hover:        var(--color-gray-900);
  --nav-link-hover-bg:     rgba(0, 0, 0, 0.05);
  --nav-accent:            var(--color-primary);
  --nav-mobile-menu-bg:    rgba(255, 255, 255, 0.98);
  --nav-burger-color:      var(--color-gray-900);

  /* --- Уведомления --- */
  --notif-radius: var(--radius-xl);
  --notif-shadow: var(--shadow-lg);

  /* --- Футер --- */
  --footer-bg:           #1A1A1A;
  --footer-text:         #C4C4C4;
  --footer-heading:      #FFFFFF;
  --footer-link-hover:   #FFFFFF;
  --footer-copyright:    #767676;
  --footer-social-bg:    rgba(255, 255, 255, 0.1);
  --footer-social-hover: var(--color-primary);

  /* --- Макет --- */
  --container-max:    1120px;
  --container-pad-x:  16px;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: var(--font-family-base);
}

/* Когда открыт мобильный fullscreen-календарь — прячем шапку,
   чтобы бургер не перекрывал кнопку закрытия */
body.calendar-fullscreen-open .main-nav {
  display: none !important;
}

[id] {
  scroll-margin-top: 80px;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ======================================
   НАВИГАЦИЯ
   ====================================== */
.main-nav {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  background: var(--nav-bg);
  backdrop-filter: blur(10px);
  box-shadow: var(--nav-shadow);
}

.main-nav-cont {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: var(--nav-height);
}

.nav-brand {
  font-size: 1.25rem;
  font-weight: 700;
}

.nav-logo {
  display: inline-flex;
  align-items: center;
  color: var(--color-gray-900);
  text-decoration: none;
  font-weight: 700;
}

.nav-logo-img {
  height: 38px;
  width: auto;
  display: block;
}

.nav-sections {
  display: flex;
  gap: 0.25rem;
  align-items: center;
  flex: 1;
  justify-content: center;
}

.nav-section-link {
  position: relative;
  color: var(--nav-text);
  text-decoration: none;
  padding: 0.5rem 0.9rem;
  border-radius: var(--radius-full);
  font-size: 0.9rem;
  font-weight: 500;
  transition: background var(--transition-base), color var(--transition-base);
  white-space: nowrap;
  cursor: pointer;
}

.nav-section-link::after {
  content: "";
  position: absolute;
  left: 50%;
  right: 50%;
  bottom: 4px;
  height: 2px;
  background: var(--nav-accent);
  border-radius: 2px;
  transition: left var(--transition-base), right var(--transition-base);
}

.nav-section-link:hover {
  background: var(--nav-link-hover-bg);
  color: var(--nav-text-hover);
  text-decoration: none;
}

.nav-section-link:hover::after {
  left: 20%;
  right: 20%;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* ======================================
   БУРГЕР
   ====================================== */
.nav-burger {
  display: none;
  width: 40px;
  height: 40px;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
  margin-left: 8px;
}

.nav-burger span {
  position: absolute;
  left: 10px;
  right: 10px;
  height: 2px;
  background: var(--nav-burger-color);
  border-radius: 2px;
  transition: transform 0.25s ease, opacity 0.2s ease, top 0.25s ease, bottom 0.25s ease;
}

.nav-burger span:nth-child(1) { top: 13px; }
.nav-burger span:nth-child(2) { top: 19px; }
.nav-burger span:nth-child(3) { top: 25px; }

.nav-burger--open span:nth-child(1) { top: 19px; transform: rotate(45deg); }
.nav-burger--open span:nth-child(2) { opacity: 0; }
.nav-burger--open span:nth-child(3) { top: 19px; transform: rotate(-45deg); }

/* ======================================
   МОБИЛЬНОЕ МЕНЮ
   ====================================== */
.mobile-menu {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem var(--container-pad-x) 1rem;
  border-top: 1px solid rgba(0,0,0,0.06);
  background: var(--nav-mobile-menu-bg);
  backdrop-filter: blur(10px);
}

/* Скрываем мобильное меню на больших экранах (даже если v-if=true) */
@media (min-width: 961px) {
  .mobile-menu { display: none !important; }
}

.mobile-menu-link {
  display: block;
  padding: 0.85rem 0.75rem;
  color: var(--color-gray-900);
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
  border-radius: var(--radius-md);
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast);
  font-family: inherit;
  width: 100%;
}

.mobile-menu-link:hover {
  background: var(--nav-link-hover-bg);
  text-decoration: none;
  color: var(--color-primary);
}

.mobile-menu-link--primary {
  background: var(--color-primary);
  color: var(--color-white) !important;
  text-align: center;
}

.mobile-menu-link--primary:hover {
  background: var(--color-primary-dark);
}

.mobile-menu-link--btn {
  border: 1px solid var(--color-gray-300);
  text-align: center;
  margin-top: 0.25rem;
}

.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease, max-height 0.25s ease;
  overflow: hidden;
  max-height: 500px;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-8px);
}

.nav-link {
  color: var(--nav-text);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 500;
  transition: all var(--transition-base);
}

.nav-link:hover {
  background: var(--nav-link-hover-bg);
  color: var(--color-primary);
  text-decoration: none;
}

.admin-link {
  background: var(--color-primary);
  color: var(--color-white) !important;
}

.admin-link:hover {
  background: var(--color-primary-dark) !important;
  color: var(--color-white) !important;
}

.nav-button {
  background: none;
  border: 1px solid var(--color-gray-300);
  color: var(--nav-text);
  padding: 0.4rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all var(--transition-base);
}

.nav-button:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* ======================================
   ОСНОВНОЙ КОНТЕНТ
   ====================================== */
.main-content {
  flex: 1;
}

/* ======================================
   УВЕДОМЛЕНИЯ
   ====================================== */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  color: white;
  z-index: 2000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 0.9rem;
}

.notification.info { background: #3498db; }
.notification.success { background: #2ecc71; }
.notification.error { background: #e74c3c; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ======================================
   ФУТЕР
   ====================================== */
.site-footer {
  background: #1A1A1A;
  color: #C4C4C4;
  padding: 3rem 0 1.5rem;
  margin-top: auto;
}

.footer-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 16px;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-heading {
  color: white;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.footer-contact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #C4C4C4;
  text-decoration: none;
  padding: 0.4rem 0;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.footer-contact:hover {
  color: white;
  text-decoration: none;
}

.footer-link {
  display: block;
  color: #C4C4C4;
  text-decoration: none;
  padding: 0.3rem 0;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: white;
  text-decoration: none;
}

.social-icons {

  display: flex;
  gap: 0.75rem;
}


.footer-col--nav {
  text-align: center;
}

.footer-col--nav .footer-heading,
.footer-col--nav .footer-link {
  text-align: center;
}

.footer-col--social {
  text-align: right;
}

.footer-col--social .footer-heading {
  text-align: right;
}

.footer-col .social-icons {
  justify-content: flex-end;
}

.social-icon {
  
  right: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transition: all 0.2s;
}

.social-icon:hover {
  background: var(--color-primary, #FF5A5F);
  transform: translateY(-2px);
  text-decoration: none;
  color: white;
}

.footer-bottom {
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-copyright {
  text-align: center;
  color: #767676;
  font-size: 0.85rem;
  margin: 0;
}

/* ======================================
   АДАПТИВНОСТЬ
   ====================================== */
@media (max-width: 960px) {
  .nav-sections { display: none; }
  .nav-burger { display: block; }
  .nav-links { display: none; }
  
.footer-col--nav {
  text-align: left;
}

.footer-col--nav .footer-heading,
.footer-col--nav .footer-link {
  text-align: left;
}

.footer-col--social {
  text-align: left;
}

.footer-col--social .footer-heading {
  text-align: left;
}

.footer-col .social-icons {
  justify-content: flex-start;
}
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .site-footer {
    padding: 2rem 0 1rem;
  }

  .main-nav-cont {
    padding: 0 12px;
    height: var(--nav-height-mobile);
  }
}

@media (max-width: 480px) {
  .social-icons {
    flex-wrap: wrap;
  }
}
</style>