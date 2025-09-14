import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useUserStore = defineStore('userStore', () => {
  const username = ref('');

  function setUsername(name: string) {
    username.value = name;
  }

  return { username, setUsername };
});