<template>
  <div class="guests-container">
    <input 
      type="text" 
      :value="displayText" 
      placeholder="Гости" 
      readonly
      id="guestsInput"
    >
    <div class="guests-controls">
      <button 
        class="guest-btn minus-btn" 
        @click="changeGuests(-1)" 
        :disabled="currentCount <= MIN_GUESTS"
      >-</button>
      <button 
        class="guest-btn plus-btn" 
        @click="changeGuests(1)" 
        :disabled="currentCount >= MAX_GUESTS"
      >+</button>
    </div>
  </div>
</template>

<script>
import { computed, ref, watch } from 'vue';

export default {
  props: {
    count: {
      type: Number,
      default: 1
    },
    MIN_GUESTS: {
      type: Number,
      default: 1
    },
    MAX_GUESTS: {
      type: Number,
      required: true
    }
  },
  emits: ['update:count'],
  setup(props, { emit }) {
    const currentCount = ref(props.count);

    watch(() => props.count, (newVal) => {
      currentCount.value = newVal;
    });

    const getGuestsWordForm = (number) => {
      const num = Math.abs(number);
      if (num % 10 === 1 && num % 100 !== 11) return 'Гость';
      if ([2, 3, 4].includes(num % 10) && ![12, 13, 14].includes(num % 100)) return 'Гостя';
      return 'Гостей';
    };

    const displayText = computed(() => {
      return `${getGuestsWordForm(currentCount.value)} ${currentCount.value}`;
    });

    const changeGuests = (delta) => {
      const newValue = Math.min(
        props.MAX_GUESTS, 
        Math.max(props.MIN_GUESTS, currentCount.value + delta)
      );
      currentCount.value = newValue;
      emit('update:count', newValue);
    };

    return {
      displayText,
      changeGuests,
      currentCount
    };
  }
};
</script>
  
  <style scoped>
  .guests-container {
    position: relative;
    padding-left: 20px;
    font-size: 14px;
    transition: all 0.3s ease;
    border: none;

  }
  
  #guestsInput {
    box-sizing: border-box;
    width: 100%;
    border: none;
    color: #757587;
    padding: 0;
    background: transparent;
    cursor: pointer;
    text-align: left;
  }
  
  .guests-controls {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    gap: 6px;
    align-items: center;
  }
  
  .guest-btn {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 50%;
    background: #f8f9fa;
    color: #4c4cf7;
    font-size: 18px;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  #guestsInput{
    outline: none;
  }
  
  .guest-btn:hover:not(:disabled) {
    background: #4c4cf7;
    color: white;
    transform: scale(1.05);
  }
  
  .guest-btn:active:not(:disabled) {
    transform: scale(0.95);
  }
  
  .guest-btn:disabled {
    opacity: 0.5;
    background: #f8f9fa;
    color: #6c757d;
    box-shadow: none;
  }
  
  @media (max-width: 480px) {
    .guests-container {
      width: 100%;
    }
    
    #guestsInput {
      padding-right: 70px;
    }
  }
  </style>