<template>
  <section 
    class="section__intro" 
    :style="mainPhotoStyle"
  >
    <div class="container">
      <div class="into__inner">
        <h1 class="into__inner-header">Виноградная лоза</h1>
        <h2 class="into__inner-titel">
          Гостеприимство и уют ждут вас в нашем гостевом домике, расположенным на южном берегу Крыма.
        </h2>
        <SearchForm 
          @search="handleSearch" 
          :fetchAllRooms="fetchAllRooms" 
          @clire="Clire" 
        />
      </div>
    </div>
  </section>
  
  <div class="main_vrapper">
    <RoomComponent 
      :pfoto_dvor="getPhotoDvor"
      :rooms="filteredRooms"
      :url_data="urldata" 
      :is-loading="isLoading"
    />
    <div class="activities-grid">
            <!-- Первая строка -->
            <div class="activity-card">
                <div class="activity-icon">
                     <img class="activiti_svg" src="@/assets/icons/shop.svg" alt="Назад">
                </div>
                <h3 class="activity-title">Магазины и кафе
</h3>
                
            </div>
            
            <div class="activity-card">
                <div class="activity-icon">
                     <img class="activiti_svg" src="@/assets/icons/place.svg" alt="Назад">
                </div>
                <h3 class="activity-title">Поездки по Крыму</h3>
                
            </div>
            
            <div class="activity-card">
                <div class="activity-icon">
                     <img class="activiti_svg" src="@/assets/icons/games.svg" alt="Назад">
                </div>
                <h3 class="activity-title">Пляжные развлечения
</h3>
            </div>
            
            <!-- Вторая строка -->
            <div class="activity-card">
                <div class="activity-icon">
                     <img class="activiti_svg" src="@/assets/icons/beach.svg" alt="Назад">
                </div>
                <h3 class="activity-title">Пляж бесплатный</h3>

            </div>
            
            <div class="activity-card">
                <div class="activity-icon">
                     <img class="activiti_svg" src="@/assets/icons/jur.svg" alt="Назад">
                </div>
                <h3 class="activity-title">Знаковые места</h3>
                
            </div>
            
            <div class="activity-card">
                <div class="activity-icon">
                     <img class="activiti_svg" src="@/assets/icons/football.svg" alt="Назад">
                </div>
                <h3 class="activity-title">Стадион и парк</h3>
            </div>
        </div>
  </div>


</template>

<script>
import SearchForm from './SearchForm.vue';
import RoomComponent from './RoomComponent.vue';
import axios from 'axios';
import defaultImage from '@/assets/rybache1.jpg'; // Импортируем дефолтное изображение

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
      siteInfo: null, // Добавляем данные о сайте
      defaultImage: defaultImage // Сохраняем дефолтное изображение
    };
  },
  computed: {
    // Вычисляемое свойство для стилей фона
    mainPhotoStyle() {
      let backgroundImage = this.defaultImage;
      
      if (this.siteInfo?.main_photo) {
        backgroundImage = this.siteInfo.main_photo.startsWith('http') 
          ? this.siteInfo.main_photo 
          : `http://localhost:8000${this.siteInfo.main_photo}`;
      }
      
      return {
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      };
    },
    getPhotoDvor(){
      // Добавляем проверку на null
      return this.siteInfo?.courtyard_photos || [];
    }
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
    await this.fetchSiteInfo(); // Загружаем информацию о сайте
    await this.fetchAllRooms(); // Загружаем комнаты
  },
  methods: {
    Clire() {
      this.urldata = null;
    },
    
    // Загрузка информации о сайте
    async fetchSiteInfo() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/site/');
        this.siteInfo = response.data;
      } catch (error) {
        console.error('Ошибка загрузки информации о сайте:', error);
        this.siteInfo = {};
      }
    },
    
    async fetchAllRooms() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/rooms/');
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
        
        const response = await axios.post(
          'http://127.0.0.1:8000/rooms/filter/', 
          searchData
        );
        
        this.filteredRooms = response.data;
      } catch (error) {
        console.error('Ошибка при поиске комнат:', error);
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

  <style>

  .main_vrapper{
    max-width: 1120px;
    display: flex;
    padding: 30px;
    flex-direction: column;
    align-items: center;
    margin: 0 auto;
  }
  .container {
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    max-width: 1120px;
    height: 100%;
    margin: 0 auto;
    padding: 0 100px;
  }


  .section__intro {
    height: 45vh;
    width: 100%;
  }

  .into__inner {
    text-align: center;

    color: white;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
        -ms-flex-direction: column;
            flex-direction: column;
    -webkit-box-pack: center;
        -ms-flex-pack: center;
            justify-content: center;
    max-width: 678px;
    height: 100%;
  }

  .into__inner-titel {
    margin-top: 20px;
    line-height: 45px;
  }

  .into__inner-header {
    font-size: 72px;
    max-width: 680px;
  }
  .section__intro {
    position: relative;
    z-index: 1;

    background-size: cover;
    
    background-position: center;
    background-repeat: no-repeat;
  }


  .section__intro::before{
      content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    
    background: 
      linear-gradient(
        135deg, 
        rgba(255, 255, 255, 0.15) 0%,
        rgba(255, 255, 255, 0.05) 100%
      );
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    
    z-index: -1;
  }
.section-title {
            text-align: center;
            margin-bottom: 40px;
            font-size: 2.5rem;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .activities-grid {
    display: grid;

    grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
    gap: 20px;
    max-width: 1120px;
    margin: 40px 0;
}

        .activity-card {
            height: 70px;
            padding: 15px 10px;
            align-items: center;
            text-align: center;
            justify-content: center;
            justify-content: space-around;
            gap: 12px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            display: flex;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .activity-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        }

        .activity-icon {
            font-size: 2rem;

            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }

        .activity-title {
            font-size: 1.3rem;
            font-weight: 600;
        }

        .activity-desc {
            font-size: 0.9rem;
            line-height: 1.4;
            text-align: center;
            margin-top: 3px;
        }
        .activiti_svg{
          width: clamp(30px, 3vw, 50px);
        }

        /* Адаптивность */
        @media (max-width: 900px) {
            .activities-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 600px) {
            .activities-grid {
                grid-template-columns: 1fr;
            }
            
            .section-title {
                font-size: 2rem;
            }
        }



  </style>