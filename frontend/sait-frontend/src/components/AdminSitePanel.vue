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

    <!-- Фотографии двора -->
    <section class="section-card">
      <div class="section-header">
        <h2>Фотографии двора</h2>
        <button @click="showPhotoUpload = true" class="btn-add">Добавить фото</button>
      </div>
      
      <div class="photo-management">
        <div class="photo-grid">
          <div v-for="photo in courtyardPhotos" :key="photo.id" class="photo-card">
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
    </section>

    <!-- Отзывы -->
    <section class="section-card">
      <div class="section-header">
        <h2>Отзывы</h2>
        <button @click="openTestimonialModal(null)" class="btn-add">Добавить отзыв</button>
      </div>
      
      <div class="items-list">
        <div v-for="testimonial in testimonials" :key="testimonial.id" class="list-item">
          <div class="item-info">
            <div class="item-header">
              <img :src="getFullUrl(testimonial.author_icon_url)" class="author-icon">
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
        <h3>Добавить фотографии двора</h3>
        <form @submit.prevent="addCourtyardPhotos">
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
            <input type="file" @change="handleTestimonialPhotoChange" accept="image/*">
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
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';

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
    const testimonialPhotoFile = ref(null);
    
    // Состояния редактирования
    const editingTestimonial = ref(null);
    const editingFaq = ref(null);

    const API_BASE = 'http://localhost:8000/site';
    
    // Загрузка данных
    const loadData = async () => {
        try {
            // Получаем все данные одним запросом
            const response = await axios.get(`${API_BASE}/`);
            const data = response.data;
            
            // Сохраняем основную информацию
            siteInfo.value = data;
            Object.assign(editableSiteInfo, {
            main_description: data.main_description
            });
            
            // Сохраняем связанные данные
            courtyardPhotos.value = data.courtyard_photos || [];
            testimonials.value = data.testimonials || [];
            faqs.value = data.faqs || [];
            
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
        }
    };

    // Получение полного URL
    const getFullUrl = (url) => {
      if (!url) return ''; // Защита от undefined/null
      return url.startsWith('http') ? url : `http://localhost:8000${url}`;
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

    const handleTestimonialPhotoChange = (e) => {
      testimonialPhotoFile.value = e.target.files[0];
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
        
        if (mainPhotoFile.value) {
          formData.append('main_photo_file', mainPhotoFile.value);
        }
        
        formData.append('main_description', editableSiteInfo.main_description);
        
        const response = await axios.put(
          `${API_BASE}/`, 
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
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
        
        const response = await axios.post(
          `${API_BASE}/courtyard-photos`, 
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
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
      } catch (error) {
        console.error('Ошибка добавления фото:', error);
        alert('Ошибка при загрузке фото: ' + (error.response?.data?.detail || error.message));
      }
    };

    const deleteCourtyardPhoto = async (id) => {
      if (!confirm('Удалить эту фотографию?')) return;
      
      try {
        await axios.delete(`${API_BASE}/courtyard-photos/${id}`);
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
      } else {
        Object.assign(editableTestimonial, {
          author_name: '',
          comment: ''
        });
      }
      
      testimonialPhotoFile.value = null;
      showTestimonialModal.value = true;
    };

    const saveTestimonial = async () => {
      try {
        const formData = new FormData();
        
        formData.append('author_name', editableTestimonial.author_name);
        formData.append('comment', editableTestimonial.comment);
        
        if (testimonialPhotoFile.value) {
          formData.append('author_icon_file', testimonialPhotoFile.value);
        }
        
        let response;
        
        if (editingTestimonial.value) {
          response = await axios.put(
            `${API_BASE}/testimonials/${editingTestimonial.value}`,
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
          );
          const index = testimonials.value.findIndex(t => t.id === editingTestimonial.value);
          testimonials.value[index] = response.data;
        } else {
          response = await axios.post(
            `${API_BASE}/testimonials`,
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
          );
          testimonials.value.push(response.data);
        }
        
        showTestimonialModal.value = false;
        testimonialPhotoFile.value = null;
        loadData();
      } catch (error) {
        console.error('Ошибка сохранения отзыва:', error);
        alert('Ошибка при сохранении отзыва: ' + (error.response?.data?.detail || error.message));
      }
    };

    const deleteTestimonial = async (id) => {
      if (!confirm('Удалить этот отзыв?')) return;
      
      try {
        await axios.delete(`${API_BASE}/testimonials/${id}`);
        testimonials.value = testimonials.value.filter(t => t.id !== id);
      } catch (error) {
        console.error('Ошибка удаления отзыва:', error);
      }
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
          response = await axios.put(
            `${API_BASE}/faqs/${editingFaq.value}`,
            faqData
          );
          const index = faqs.value.findIndex(f => f.id === editingFaq.value);
          faqs.value[index] = response.data;
        } else {
          response = await axios.post(`${API_BASE}/faqs`, faqData);
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
        await axios.delete(`${API_BASE}/faqs/${id}`);
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
      faqs,
      selectedCourtyardFiles,
      
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
      openTestimonialModal,
      saveTestimonial,
      handleTestimonialPhotoChange,
      deleteTestimonial,
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
}

.photo-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  aspect-ratio: 4/3;
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