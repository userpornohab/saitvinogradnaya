<template>
  <div id="app">
    <!-- Навигационная панель -->
    <nav v-if="showNavigation" class="main-nav">
      <div class="main-nav-cont">
        <div class="nav-brand">
        <router-link to="/" class="nav-logo">Отель</router-link>
      </div>
      
      <div class="nav-links">
        <router-link v-if="isAuthenticated" to="/profile" class="nav-link">
          Профиль
        </router-link>
        
        <template v-if="!isAuthenticated">
          <router-link to="/login" class="nav-link">Вход</router-link>
          <router-link to="/signup" class="nav-link">Регистрация</router-link>
        </template>

        <template v-else>
          <router-link 
            v-if="isAdmin"
            to="/admin/rooms" 
            class="nav-link admin-link"
          >
            Админ-панель
          </router-link>
          <button @click="handleLogout" class="nav-button">Выход</button>
        </template>
      </div>
      </div>

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

    <footer class="section__footer">
        <div class="container">
            <div class="footer">
                <div class="topfoot">
                    <a href="/"><img src="img/logo.svg" alt=""></a>
                    <a href="" data-easy-toggle="#bron" data-easy-class="show" class="batton">Забронировать</a>
                </div>
                <hr>
                <div class="backfoot">
                    <div class="backfoot__contacts">
                        <h3>Контактные данные</h3>
                        <a href="tel:+79788028912" class="info-items">
                            <img src="img/tel.svg" alt="">
                            <p>+7(978)802-89-12</p>
                        </a>
                        <a href="mailto:loza-vinogradnaya@mail.ru" class="info-items">
                            <img src="img/mail.svg" alt="">
                            <p>loza-vinogradnaya@mail.ru</p>
                        </a>
                        <a href="https://yandex.ru/maps/org/gostevoy_domik_vinogradnaya_loza/92950545738/?from=tabbar&ll=34.594544%2C44.771809&source=serp_navig&z=17"
                            class="info-items">
                            <img src="img/plase.svg" alt="">
                            <p>Алушта, с. РыБачье, ул. Школьная 1/2 </p>
                        </a>
                    </div>
                    <div class="backfoot__rooms">
                        <h3>Номера</h3>
                        <div>
                            <a href="#" data-easy-toggle="#room_four" data-easy-class="show" class="rooms-item">
                                <p>Номер на двоих</p>
                            </a>
                            <a href="#" data-easy-toggle="#modalWin" data-easy-class="show" class="rooms-item">
                                <p>Номер на четверых</p>
                            </a>
                            <a href="#" data-easy-toggle="#room_one" data-easy-class="show" class="rooms-item">
                                <p>Домик на троих</p>
                            </a>
                        </div>
                    </div>
                    <div class="backfoot__wk">
                        <h3>Соц-сети</h3>
                        <div class="wk-con">
                            <a href="https://vk.com/rubachie"><img src="img/wk.svg" alt=""></a>
                            <a href="#"><img src="img/inst.svg" alt=""></a>
                            <a href="#"><img src="img/ok.svg" alt=""></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </footer>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      rooms: [],
      isAuthenticated: false,
      isAdmin: false,
      notification: {
        message: '',
        type: 'info' // info | success | error
      }
    };
  },
  computed: {
    showNavigation() {
      // Скрываем навигацию на страницах входа/регистрации
      return !['Login', 'SignUp'].includes(this.$route.name);
    }
  },
  async created() {
    await this.checkAuth();
  },
  watch: {
    $route() {
      this.checkAuth();
    }
  },
  methods: {
    async checkAuth() {
      const token = localStorage.getItem('access_token');
      this.isAuthenticated = !!token;

      if (token) {
        try {
          const response = await axios.get('http://localhost:8000/users/me/', { // Добавлен слеш в конце
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
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
    }
  }
};
</script>

<style>
body{
  margin: 0;
}
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 2rem;
  background: #2c3e50;
  color: white;
}

.main-nav-cont{
  width: 1120px;
  display: flex;
  justify-content: space-between;
}

.nav-brand {
  font-size: 1.5rem;
}

.nav-logo {
  color: white;
  text-decoration: none;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: rgba(255,255,255,0.1);
}

.admin-link {
  background: #e74c3c;
}

.nav-button {
  background: none;
  border: 1px solid white;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-button:hover {
  background: white;
  color: #2c3e50;
}

.main-content {
  flex: 1;

}

.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 1rem 2rem;
  border-radius: 8px;
  color: white;
  z-index: 1000;
}

.notification.info {
  background: #3498db;
}

.notification.success {
  background: #2ecc71;
}

.notification.error {
  background: #e74c3c;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .main-nav {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }
  

}

.section__footer {
  display: flex;
  justify-content: center;
  background-color: #43474F;
  color: white;
  min-height: 400px;
}

.footer {
  width: 1120px;

  padding: 50px 0;
}

.footer a {
  color: white;
}

.topfoot {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
      -ms-flex-align: center;
          align-items: center;
  -webkit-box-pack: justify;
      -ms-flex-pack: justify;
          justify-content: space-between;
  margin-bottom: 20px;
}

.batton {
  font-size: 16px;
  color: white;
  padding: 14px 32px;
  background-color: #5F002A;
  border-radius: 30px;
  -webkit-transition: 0.2s ease all;
  -o-transition: 0.2s ease all;
  transition: 0.2s ease all;
}

.batton:hover {
  background-color: #6e0132;
}

.backfoot {
  margin-top: 36px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-pack: justify;
      -ms-flex-pack: justify;
          justify-content: space-between;
  -ms-flex-wrap: wrap;
      flex-wrap: wrap;
}

.backfoot__rooms div {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
      -ms-flex-direction: column;
          flex-direction: column;
  gap: 20px;
}

.backfoot div:not(:last-child) {
  margin-right: 20px;
  margin-bottom: 40px;
}

.backfoot > div > h3 {
  margin-bottom: 25px;
  color: white;
}

.info-items {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  gap: 20px;
  -webkit-box-align: center;
      -ms-flex-align: center;
          align-items: center;
  margin-bottom: 20px;
  -webkit-transition: 0.2s ease color;
  -o-transition: 0.2s ease color;
  transition: 0.2s ease color;
  color: #212121;
}

.info-items:hover {
  color: #5F002A;
}

.rooms-item {
  -webkit-transition: 0.2s ease color;
  -o-transition: 0.2s ease color;
  transition: 0.2s ease color;
  color: #212121;
}

.rooms-item:hover {
  color: #5F002A;
}

.wk-con {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  gap: 15px;
}
html,
body,
div,
span,
applet,
object,
iframe,
h1,
h2,
h3,
h4,
h5,
h6,
p,
blockquote,
pre,
a,
abbr,
acronym,
address,
big,
cite,
code,
del,
dfn,
em,
img,
ins,
kbd,
q,
s,
samp,
small,
strike,
strong,
sub,
sup,
tt,
var,
b,
u,
i,
center,
dl,
dt,
dd,
ol,
ul,
li,
fieldset,
form,
label,
legend,
table,
caption,
tbody,
tfoot,
thead,
tr,
th,
td,
article,
aside,
canvas,
details,
embed,
figure,
figcaption,
footer,
header,
hgroup,
menu,
nav,
output,
ruby,
section,
summary,
time,
mark,
audio,
video {
  margin: 0;
  padding: 0;
  border: 0;
  vertical-align: baseline;
}

/* HTML5 display-role reset for older browsers */

article,
aside,
details,
figcaption,
figure,
footer,
header,
hgroup,
menu,
nav,
section {
  display: block;
}

body {
  line-height: 1;
}

ol,
ul {
  list-style: none;
}

blockquote,
q {
  quotes: none;
}

blockquote:before,
blockquote:after {
  content: "";
  content: none;
}

q:before,
q:after {
  content: "";
  content: none;
}

table {
  border-collapse: collapse;
  border-spacing: 0;
}
h1,
h3,
h2{
  margin: 30px 0;
}

</style>