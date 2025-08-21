<template>
  <div v-if="notification" class="notification" :class="notification.type">
    {{ notification.message }}
  </div>
</template>

<script>
export default {
  props: {
    notification: Object  // Может быть null!
  },
  watch: {
    // Исправленный watch с проверкой на null
    notification(newVal) {
      if (newVal) {
        this.show(newVal);
      }
    }
  },
  methods: {
    show(notification) {
      // ДОБАВЬТЕ ПРОВЕРКУ НА NULL!
      if (!notification) return;
      
      console.log("Showing notification:", notification.message);
      
      // Автоматическое скрытие через 5 сек

    },
    
  }
};
</script>

<style scoped>
/* Уведомления */
.notification {
  height: fit-content;
  position: fixed;
  
  padding: 1rem;
  border-radius: 4px;
  color: white;
}

.notification.success {
  background: #2ecc71;
}

.notification.error {
  background: #e74c3c;
}

</style>