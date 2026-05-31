<template>
  <div class="admin-panel">
    <AdminHeader></AdminHeader>
    
    <!-- Главная информация -->
    <section class="section-card">
      <div class="section-header">
        <h2>Основная информация</h2>
        <button @click="openSiteInfoModal" class="btn-edit">Редактировать</button>
      </div>
      
      <div v-if="siteInfo" class="info-grid">
        <div class="main-photo-preview">
          <img v-if="siteInfo.main_photo" :src="getFullUrl(siteInfo.main_photo)" alt="Main Photo" class="photo-preview">
          <div v-else class="photo-placeholder">Нет фото</div>
        </div>
        <div class="description-preview">
          <p>{{ siteInfo.main_description || 'Описание отсутствует' }}</p>
        </div>
      </div>
    </section>

    <!-- Фотографии территории -->
    <section class="section-card">
      <div class="section-header">
        <h2>Фотографии территории</h2>
        <button @click="showPhotoUpload = true" class="btn-add">Добавить фото</button>
      </div>
      
      <div class="photo-management">
        <div
          v-for="group in territoryCategories"
          :key="group.value"
          class="photo-group"
        >
          <div class="photo-group-header">
            <h3>{{ group.label }}</h3>
            <span>{{ groupedCourtyardPhotos[group.value]?.length || 0 }} фото</span>
          </div>

          <div
            class="photo-grid"
            @dragover.prevent
            @drop="dropPhotoIntoCategory(group.value)"
          >
            <div
              v-for="photo in groupedCourtyardPhotos[group.value]"
              :key="photo.id"
              class="photo-card"
              draggable="true"
              @dragstart="startPhotoDrag(photo)"
              @dragover.prevent
              @drop.stop="dropPhoto(photo, group.value)"
            >
              <img :src="getFullUrl(photo.url)" class="photo-preview">
              <div class="photo-controls">
                <button 
                  @click="deleteCourtyardPhoto(photo.id)"
                  title="Удалить"
                  class="delete-btn"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Отзывы -->
    <section class="section-card">
      <div class="section-header">
        <h2>Отзывы</h2>
        <button @click="openTestimonialModal(null)" class="btn-add">Добавить отзыв</button>
      </div>

      <div class="testimonial-library">
        <div class="testimonial-library-header">
          <div>
            <h3>Фото для отзывов</h3>
            <p>Загрузите изображения один раз, а потом выбирайте их в отзыве.</p>
          </div>
          <label class="btn-add upload-label">
            Загрузить фото
            <input
              type="file"
              multiple
              class="hidden-file"
              accept="image/*,.svg,image/svg+xml"
              @change="handleTestimonialLibraryChange"
            >
          </label>
        </div>
        <div v-if="testimonialImages.length" class="testimonial-image-grid">
          <div
            v-for="image in testimonialImages"
            :key="image.id"
            class="testimonial-image-card"
          >
            <img :src="getFullUrl(image.url)" alt="Фото для отзыва">
            <button
              type="button"
              class="delete-btn testimonial-image-delete"
              title="Удалить"
              @click="deleteTestimonialImage(image.id)"
            >
              ×
            </button>
          </div>
        </div>
        <p v-else class="empty-note">Пока нет загруженных фото для отзывов.</p>
      </div>
      
      <div class="items-list">
        <div v-for="testimonial in testimonials" :key="testimonial.id" class="list-item">
          <div class="item-info">
            <div class="item-header">
              <img v-if="testimonial.author_icon_url" :src="getFullUrl(testimonial.author_icon_url)" class="author-icon">
              <span v-else class="author-icon author-icon-placeholder">{{ getInitials(testimonial.author_name) }}</span>
              <strong>{{ testimonial.author_name }}</strong>
            </div>
            <p>{{ testimonial.comment }}</p>
          </div>
          <div class="item-actions">
            <button @click="openTestimonialModal(testimonial)" class="btn-edit">Изменить</button>
            <button @click="deleteTestimonial(testimonial.id)" class="btn-delete">Удалить</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Вопросы-ответы -->
    <section class="section-card">
      <div class="section-header">
        <h2>Вопросы-ответы</h2>
        <button @click="openFaqModal(null)" class="btn-add">Добавить вопрос</button>
      </div>
      
      <div class="items-list">
        <div v-for="faq in faqs" :key="faq.id" class="list-item">
          <div class="item-info">
            <p><strong>Вопрос:</strong> {{ faq.question }}</p>
            <p><strong>Ответ:</strong> {{ faq.answer }}</p>
          </div>
          <div class="item-actions">
            <button @click="openFaqModal(faq)" class="btn-edit">Изменить</button>
            <button @click="deleteFaq(faq.id)" class="btn-delete">Удалить</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Модальные окна -->
    <!-- Редактирование основной информации -->
    <div v-if="showSiteInfoModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Редактировать основную информацию</h3>
        <form @submit.prevent="saveSiteInfo">
          <div class="form-group">
            <label>Главное фото:</label>
            <input type="file" @change="handleMainPhotoChange" accept="image/*">
          </div>
          <div class="form-group">
            <label>Описание:</label>
            <textarea v-model="editableSiteInfo.main_description" rows="4"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showSiteInfoModal = false" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-save">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Добавление фото двора -->
    <div v-if="showPhotoUpload" class="modal-overlay">
      <div class="modal-content">
        <h3>Добавить фотографии территории</h3>
        <form @submit.prevent="addCourtyardPhotos">
          <div class="form-group">
            <label>Группа:</label>
            <select v-model="selectedCourtyardCategory">
              <option v-for="category in territoryCategories" :key="category.value" :value="category.value">
                {{ category.label }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Выберите фото (можно несколько):</label>
            <input 
              type="file" 
              multiple 
              ref="courtyardFileInput"
              @change="handleCourtyardPhotoChange" 
              accept="image/*"
            >
          </div>
          
          <!-- Превью выбранных файлов -->
          <div v-if="selectedCourtyardFiles.length" class="preview-grid">
            <div v-for="(file, index) in selectedCourtyardFiles" :key="index" class="preview-item">
              <img :src="getObjectURL(file)" class="preview-image">
              <span class="file-name">{{ file.name }}</span>
              <button @click="removeCourtyardFile(index)" class="remove-btn">×</button>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showPhotoUpload = false" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-save">Загрузить ({{ selectedCourtyardFiles.length }})</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Редактирование отзыва -->
    <div v-if="showTestimonialModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ editingTestimonial ? 'Редактировать отзыв' : 'Добавить отзыв' }}</h3>
        <form @submit.prevent="saveTestimonial">
          <div class="form-group">
            <label>Имя автора:</label>
            <input type="text" v-model="editableTestimonial.author_name" required>
          </div>
          <div class="form-group">
            <label>Фото автора:</label>
            <label class="btn-add upload-label upload-label-inline">
              Добавить в библиотеку
              <input
                type="file"
                multiple
                class="hidden-file"
                accept="image/*,.svg,image/svg+xml"
                @change="handleTestimonialLibraryChange"
              >
            </label>
            <div v-if="testimonialImages.length" class="testimonial-picker">
              <button
                v-for="image in testimonialImages"
                :key="image.id"
                type="button"
                class="testimonial-picker-item"
                :class="{ 'testimonial-picker-item--active': selectedTestimonialImageUrl === image.url }"
                @click="selectTestimonialImage(image.url)"
              >
                <img :src="getFullUrl(image.url)" alt="">
              </button>
            </div>
            <p v-else class="empty-note">Сначала загрузите фото в библиотеку.</p>
          </div>
          <div class="form-group">
            <label>Комментарий:</label>
            <textarea v-model="editableTestimonial.comment" rows="4" required></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showTestimonialModal = false" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-save">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Редактирование FAQ -->
    <div v-if="showFaqModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ editingFaq ? 'Редактировать вопрос' : 'Добавить вопрос' }}</h3>
        <form @submit.prevent="saveFaq">
          <div class="form-group">
            <label>Вопрос:</label>
            <textarea v-model="editableFaq.question" rows="2" required></textarea>
          </div>
          <div class="form-group">
            <label>Ответ:</label>
            <textarea v-model="editableFaq.answer" rows="4" required></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showFaqModal = false" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-save">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted, reactive } from 'vue';
import api, { API_BASE_URL } from '@/api';

import AdminHeader  from './AdminHeader.vue';

export default {
  components: {
    AdminHeader
  },

  setup() {
    // Основные данные
    const siteInfo = ref(null);
    const courtyardPhotos = ref([]);
    const testimonials = ref([]);
    const testimonialImages = ref([]);
    const faqs = ref([]);
    
    // Модальные окна
    const showSiteInfoModal = ref(false);
    const showPhotoUpload = ref(false);
    const showTestimonialModal = ref(false);
    const showFaqModal = ref(false);
    
    // Редактируемые объекты
    const editableSiteInfo = reactive({ main_description: '' });
    const editableTestimonial = reactive({ author_name: '', comment: '' });
    const editableFaq = reactive({ question: '', answer: '' });
    
    // Файлы
    const mainPhotoFile = ref(null);
    const selectedCourtyardFiles = ref([]);
    const selectedCourtyardCategory = ref('yard');
    const selectedTestimonialImageUrl = ref('');
    const draggedPhoto = ref(null);
    
    // Состояния редактирования
    const editingTestimonial = ref(null);
    const editingFaq = ref(null);
    const territoryCategories = [
      { value: 'yard', label: 'Двор' },
      { value: 'kitchen', label: 'Кухня' },
      { value: 'rest', label: 'Зона отдыха' },
    ];

    const sortCourtyardPhotos = (photos) => [...photos].sort((a, b) => {
      const orderDiff = (a.sort_order || 0) - (b.sort_order || 0);
      return orderDiff || a.id - b.id;
    });

    const groupedCourtyardPhotos = computed(() => {
      const groups = territoryCategories.reduce((acc, category) => {
        acc[category.value] = [];
        return acc;
      }, {});

      courtyardPhotos.value.forEach(photo => {
        const category = photo.category || 'yard';
        if (!groups[category]) groups[category] = [];
        groups[category].push(photo);
      });

      Object.keys(groups).forEach(category => {
        groups[category] = sortCourtyardPhotos(groups[category]);
      });

      return groups;
    });

    const API_BASE = '/site';

    // Заголовки авторизации для админ-запросов (эндпоинты требуют check_superuser)
    const authHeader = () => ({ Authorization: `Bearer ${localStorage.getItem('access_token')}` });
    const authHeaders = () => ({ headers: authHeader() });
    const authMultipart = () => ({ headers: { ...authHeader(), 'Content-Type': 'multipart/form-data' } });
    
    // Загрузка данных
    const loadData = async () => {
        try {
            // Получаем все данные одним запросом
            const response = await api.get(`${API_BASE}/`);
            const data = response.data;
            
            // Сохраняем основную информацию
            siteInfo.value = data;
            Object.assign(editableSiteInfo, {
            main_description: data.main_description
            });
            
            // Сохраняем связанные данные
            courtyardPhotos.value = sortCourtyardPhotos(data.courtyard_photos || []);
            testimonials.value = data.testimonials || [];
            testimonialImages.value = data.testimonial_images || [];
            faqs.value = data.faqs || [];
            
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
        }
    };

    // Получение полного URL
    const getFullUrl = (url) => {
      if (!url) return ''; // Защита от undefined/null
      return url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
    };

    // Генерация URL для предпросмотра
    const getObjectURL = (file) => {
      return URL.createObjectURL(file);
    };

    // Обработчики файлов
    const handleMainPhotoChange = (e) => {
      mainPhotoFile.value = e.target.files[0];
    };

    const handleCourtyardPhotoChange = (e) => {
      selectedCourtyardFiles.value = Array.from(e.target.files);
    };

    const handleTestimonialLibraryChange = async (e) => {
      const files = Array.from(e.target.files || []);
      e.target.value = '';
      if (!files.length) return;

      try {
        const formData = new FormData();
        files.forEach(file => {
          formData.append('files', file);
        });

        const response = await api.post(
          `${API_BASE}/testimonial-images`,
          formData,
          authMultipart()
        );

        testimonialImages.value = [...testimonialImages.value, ...response.data];
        if (!selectedTestimonialImageUrl.value && response.data[0]?.url) {
          selectedTestimonialImageUrl.value = response.data[0].url;
        }
      } catch (error) {
        console.error('Ошибка загрузки фото для отзывов:', error);
        alert('Ошибка при загрузке фото для отзывов: ' + (error.response?.data?.detail || error.message));
      }
    };

    // Удаление файла из списка выбранных
    const removeCourtyardFile = (index) => {
      selectedCourtyardFiles.value = selectedCourtyardFiles.value.filter((_, i) => i !== index);
    };

    // Методы для основной информации
    const openSiteInfoModal = () => {
      showSiteInfoModal.value = true;
    };

    const saveSiteInfo = async () => {
      try {
        const formData = new FormData();
        formData.append('category', selectedCourtyardCategory.value);
        
        if (mainPhotoFile.value) {
          formData.append('main_photo_file', mainPhotoFile.value);
        }
        
        formData.append('main_description', editableSiteInfo.main_description);
        
        const response = await api.put(
          `${API_BASE}/`, 
          formData,
          authMultipart()
        );
        
        siteInfo.value = response.data;
        showSiteInfoModal.value = false;
        mainPhotoFile.value = null;
        
        // Перезагружаем данные после обновления
        loadData();
      } catch (error) {
        console.error('Ошибка сохранения основной информации:', error);
        alert('Ошибка при сохранении: ' + (error.response?.data?.detail || error.message));
      }
    };

    // Методы для фотографий двора (множественная загрузка)
    const addCourtyardPhotos = async () => {
      if (selectedCourtyardFiles.value.length === 0) return;
      
      try {
        const formData = new FormData();
        
        // Добавляем все выбранные файлы
        selectedCourtyardFiles.value.forEach(file => {
          formData.append('files', file);
        });
        
        const response = await api.post(
          `${API_BASE}/courtyard-photos`, 
          formData,
          authMultipart()
        );
        
        // Обработка ответа в новом формате
        if (response.data.success) {
          // Добавляем успешно загруженные фото
          response.data.success.forEach(photo => {
            courtyardPhotos.value.push(photo);
          });
          
          // Показываем ошибки, если есть
          if (response.data.errors && response.data.errors.length > 0) {
            const errorMessages = response.data.errors.map(e => 
              `${e.filename}: ${e.error}`
            ).join('\n');
            alert(`Некоторые фото не загружены:\n${errorMessages}`);
          }
        } else {
          // Для обратной совместимости
          response.data.forEach(photo => {
            courtyardPhotos.value.push(photo);
          });
        }
        
        showPhotoUpload.value = false;
        selectedCourtyardFiles.value = [];
        selectedCourtyardCategory.value = 'yard';
        loadData();
      } catch (error) {
        console.error('Ошибка добавления фото:', error);
        alert('Ошибка при загрузке фото: ' + (error.response?.data?.detail || error.message));
      }
    };

    const persistPhotoOrder = async (photos) => {
      const payload = photos.map((photo, index) => ({
        id: photo.id,
        category: photo.category || 'yard',
        sort_order: index + 1
      }));
      await api.patch(`${API_BASE}/courtyard-photos/order`, payload, authHeaders());
      await loadData();
    };

    const startPhotoDrag = (photo) => {
      draggedPhoto.value = photo;
    };

    const dropPhoto = async (targetPhoto, targetCategory) => {
      const sourcePhoto = draggedPhoto.value;
      draggedPhoto.value = null;
      if (!sourcePhoto || sourcePhoto.id === targetPhoto.id) return;

      const nextPhotos = courtyardPhotos.value.map(photo => (
        photo.id === sourcePhoto.id
          ? { ...photo, category: targetCategory }
          : { ...photo }
      ));

      const group = sortCourtyardPhotos(nextPhotos.filter(photo => (photo.category || 'yard') === targetCategory));
      const fromIndex = group.findIndex(photo => photo.id === sourcePhoto.id);
      const toIndex = group.findIndex(photo => photo.id === targetPhoto.id);
      const [moved] = group.splice(fromIndex, 1);
      group.splice(toIndex, 0, moved);

      const otherPhotos = nextPhotos.filter(photo => (photo.category || 'yard') !== targetCategory);
      courtyardPhotos.value = [...otherPhotos, ...group];

      try {
        await persistPhotoOrder(group);
      } catch (error) {
        console.error('Ошибка сохранения порядка фото:', error);
        alert('Не удалось сохранить порядок фото');
        loadData();
      }
    };

    const dropPhotoIntoCategory = async (targetCategory) => {
      const sourcePhoto = draggedPhoto.value;
      draggedPhoto.value = null;
      if (!sourcePhoto) return;

      const group = sortCourtyardPhotos(
        courtyardPhotos.value
          .filter(photo => photo.id === sourcePhoto.id || (photo.category || 'yard') === targetCategory)
          .map(photo => photo.id === sourcePhoto.id ? { ...photo, category: targetCategory } : { ...photo })
      );

      try {
        await persistPhotoOrder(group);
      } catch (error) {
        console.error('Ошибка сохранения порядка фото:', error);
        alert('Не удалось сохранить порядок фото');
        loadData();
      }
    };

    const deleteCourtyardPhoto = async (id) => {
      if (!confirm('Удалить эту фотографию?')) return;
      
      try {
        await api.delete(`${API_BASE}/courtyard-photos/${id}`, authHeaders());
        courtyardPhotos.value = courtyardPhotos.value.filter(p => p.id !== id);
      } catch (error) {
        console.error('Ошибка удаления фото:', error);
      }
    };

    // Методы для отзывов
    const openTestimonialModal = (testimonial) => {
      editingTestimonial.value = testimonial ? testimonial.id : null;
      
      if (testimonial) {
        Object.assign(editableTestimonial, {
          author_name: testimonial.author_name,
          comment: testimonial.comment
        });
        selectedTestimonialImageUrl.value = testimonial.author_icon_url || '';
      } else {
        Object.assign(editableTestimonial, {
          author_name: '',
          comment: ''
        });
        selectedTestimonialImageUrl.value = testimonialImages.value[0]?.url || '';
      }
      
      showTestimonialModal.value = true;
    };

    const selectTestimonialImage = (url) => {
      selectedTestimonialImageUrl.value = selectedTestimonialImageUrl.value === url ? '' : url;
    };

    const saveTestimonial = async () => {
      try {
        const formData = new FormData();
        
        formData.append('author_name', editableTestimonial.author_name);
        formData.append('comment', editableTestimonial.comment);
        formData.append('author_icon_url', selectedTestimonialImageUrl.value || '');
        
        let response;
        
        if (editingTestimonial.value) {
          response = await api.put(
            `${API_BASE}/testimonials/${editingTestimonial.value}`,
            formData,
            authMultipart()
          );
          const index = testimonials.value.findIndex(t => t.id === editingTestimonial.value);
          testimonials.value[index] = response.data;
        } else {
          response = await api.post(
            `${API_BASE}/testimonials`,
            formData,
            authMultipart()
          );
          testimonials.value.push(response.data);
        }
        
        showTestimonialModal.value = false;
        selectedTestimonialImageUrl.value = '';
        loadData();
      } catch (error) {
        console.error('Ошибка сохранения отзыва:', error);
        alert('Ошибка при сохранении отзыва: ' + (error.response?.data?.detail || error.message));
      }
    };

    const deleteTestimonial = async (id) => {
      if (!confirm('Удалить этот отзыв?')) return;
      
      try {
        await api.delete(`${API_BASE}/testimonials/${id}`, authHeaders());
        testimonials.value = testimonials.value.filter(t => t.id !== id);
      } catch (error) {
        console.error('Ошибка удаления отзыва:', error);
      }
    };

    const deleteTestimonialImage = async (id) => {
      if (!confirm('Удалить это фото из библиотеки отзывов?')) return;

      try {
        await api.delete(`${API_BASE}/testimonial-images/${id}`, authHeaders());
        const deleted = testimonialImages.value.find(image => image.id === id);
        testimonialImages.value = testimonialImages.value.filter(image => image.id !== id);
        if (deleted?.url === selectedTestimonialImageUrl.value) {
          selectedTestimonialImageUrl.value = '';
        }
      } catch (error) {
        console.error('Ошибка удаления фото для отзывов:', error);
        alert('Не удалось удалить фото: ' + (error.response?.data?.detail || error.message));
      }
    };

    const getInitials = (name) => {
      return (name || '?')
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map(part => part[0]?.toUpperCase())
        .join('') || '?';
    };

    // Методы для FAQ
    const openFaqModal = (faq) => {
      editingFaq.value = faq ? faq.id : null;
      
      if (faq) {
        Object.assign(editableFaq, {
          question: faq.question,
          answer: faq.answer
        });
      } else {
        Object.assign(editableFaq, {
          question: '',
          answer: ''
        });
      }
      
      showFaqModal.value = true;
    };

    const saveFaq = async () => {
      try {
        let response;
        const faqData = {
          question: editableFaq.question,
          answer: editableFaq.answer
        };
        
        if (editingFaq.value) {
          response = await api.put(
            `${API_BASE}/faqs/${editingFaq.value}`,
            faqData,
            authHeaders()
          );
          const index = faqs.value.findIndex(f => f.id === editingFaq.value);
          faqs.value[index] = response.data;
        } else {
          response = await api.post(`${API_BASE}/faqs`, faqData, authHeaders());
          faqs.value.push(response.data);
        }
        
        showFaqModal.value = false;
      } catch (error) {
        console.error('Ошибка сохранения FAQ:', error);
      }
    };

    const deleteFaq = async (id) => {
      if (!confirm('Удалить этот вопрос?')) return;
      
      try {
        await api.delete(`${API_BASE}/faqs/${id}`, authHeaders());
        faqs.value = faqs.value.filter(f => f.id !== id);
      } catch (error) {
        console.error('Ошибка удаления FAQ:', error);
      }
    };

    // Загрузка данных при монтировании
    onMounted(loadData);

    return {
      // Данные
      siteInfo,
      courtyardPhotos,
      testimonials,
      testimonialImages,
      faqs,
      selectedCourtyardFiles,
      selectedCourtyardCategory,
      selectedTestimonialImageUrl,
      territoryCategories,
      groupedCourtyardPhotos,
      
      // Модальные окна
      showSiteInfoModal,
      showPhotoUpload,
      showTestimonialModal,
      showFaqModal,
      
      // Редактируемые объекты
      editableSiteInfo,
      editableTestimonial,
      editableFaq,
      
      // Состояния
      editingTestimonial,
      editingFaq,
      
      // Методы
      getFullUrl,
      getObjectURL,
      openSiteInfoModal,
      saveSiteInfo,
      handleMainPhotoChange,
      addCourtyardPhotos,
      handleCourtyardPhotoChange,
      removeCourtyardFile,
      deleteCourtyardPhoto,
      startPhotoDrag,
      dropPhoto,
      dropPhotoIntoCategory,
      openTestimonialModal,
      saveTestimonial,
      handleTestimonialLibraryChange,
      selectTestimonialImage,
      deleteTestimonialImage,
      deleteTestimonial,
      getInitials,
      openFaqModal,
      saveFaq,
      deleteFaq
    };
  }
};
</script>


<style scoped>
.admin-panel {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.section-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 25px;
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

/* Кнопки */
.btn-add, .btn-edit, .btn-delete, .btn-save, .btn-cancel {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-add {
  background: #3498db;
  color: white;
}

.btn-edit {
  background: #f39c12;
  color: white;
}

.btn-delete {
  background: #e74c3c;
  color: white;
  margin-left: 10px;
}

.btn-save {
  background: #2ecc71;
  color: white;
  padding: 10px 20px;
}

.btn-cancel {
  background: #95a5a6;
  color: white;
  padding: 10px 20px;
  margin-right: 10px;
}

.btn-add:hover { background: #2980b9; }
.btn-edit:hover { background: #e67e22; }
.btn-delete:hover { background: #c0392b; }
.btn-save:hover { background: #27ae60; }
.btn-cancel:hover { background: #7f8c8d; }

/* Основная информация */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
}

.main-photo-preview {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
}

.photo-preview {
  max-width: 100%;
  max-height: 300px;
  display: block;
}

.photo-placeholder {
  color: #95a5a6;
  font-size: 1.2rem;
}

.description-preview p {
  margin: 0;
  line-height: 1.6;
  color: #34495e;
}

/* Управление фотографиями */
.photo-management {
  margin-top: 20px;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 15px;
  margin-top: 15px;
  min-height: 70px;
}

.photo-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  aspect-ratio: 4/3;
  cursor: grab;
  background: #f4f6f8;
}

.photo-card:active {
  cursor: grabbing;
}

.photo-group {
  margin-bottom: 28px;
}

.photo-group-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eef0f2;
}

.photo-group-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.photo-group-header span {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.form-group select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #d7dde3;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.94);
  font-size: 0.9rem;
}

.photo-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  padding: 8px;
  background: rgba(0, 0, 0, 0.6);
  opacity: 0;
  transition: opacity 0.3s;
}
.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  margin: 15px 0;
}
.preview-item {
    width: 150px;
  height: 150px;
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.file-name {
  display: block;
  padding: 5px;
  font-size: 0.8rem;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(231, 76, 60, 0.8);
  color: white;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}


.preview-image {
    width: 150px;
  height: 150px;

  object-fit: cover;
  display: block;
}
.photo-card:hover .photo-controls {
  opacity: 1;
}

.delete-btn {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: white;
  transform: scale(1.1);
}

/* Списки элементов */
.items-list {
  margin-top: 20px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.list-item:hover {
  background: #f9f9f9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.item-info {
  flex-grow: 1;
}

.item-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.author-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 12px;
  object-fit: cover;
}

.author-icon-placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #f0eeff;
  color: #6257d8;
  font-weight: 700;
}

.testimonial-library {
  padding: 16px;
  border: 1px solid #ece9ff;
  border-radius: 10px;
  background: linear-gradient(180deg, #fbfaff 0%, #fff 100%);
}

.testimonial-library-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.testimonial-library-header h3 {
  margin: 0 0 4px;
  color: #2c3e50;
  font-size: 1rem;
}

.testimonial-library-header p,
.empty-note {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.upload-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.upload-label-inline {
  width: fit-content;
  margin-bottom: 12px;
}

.hidden-file {
  display: none;
}

.testimonial-image-grid,
.testimonial-picker {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(76px, 1fr));
  gap: 10px;
}

.testimonial-image-card,
.testimonial-picker-item {
  position: relative;
  aspect-ratio: 1;
  border: 1px solid #ece9ff;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}

.testimonial-image-card img,
.testimonial-picker-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.testimonial-image-delete {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.testimonial-image-card:hover .testimonial-image-delete {
  opacity: 1;
}

.testimonial-picker {
  grid-template-columns: repeat(auto-fill, minmax(72px, 72px));
}

.testimonial-picker-item {
  padding: 0;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.testimonial-picker-item--active {
  border-color: #6257d8;
  box-shadow: 0 0 0 3px rgba(98, 87, 216, 0.16);
  transform: translateY(-1px);
}

.item-actions {
  flex-shrink: 0;
  margin-left: 15px;
}

/* Модальные окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  padding: 30px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 1.4rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #34495e;
}

.form-group input[type="text"],
.form-group textarea,
.form-group input[type="file"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 25px;
}

/* Адаптивность */
@media (max-width: 992px) {
  .info-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .main-photo-preview {
    min-height: 150px;
  }
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .section-header h2 {
    margin-bottom: 15px;
  }
  
  .list-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .item-actions {
    margin-left: 0;
    margin-top: 15px;
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
  
  .photo-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}

@media (max-width: 576px) {
  .admin-panel {
    padding: 15px;
  }
  
  .section-card {
    padding: 20px;
  }
  
  .modal-content {
    padding: 20px;
    width: 95%;
  }
  
  .photo-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
